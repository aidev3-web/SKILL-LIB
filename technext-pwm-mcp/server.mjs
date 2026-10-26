// pwm-mcp: a tiny MCP server that fills .env keys from Vaultwarden/Bitwarden items.
// Rule: a secret (vault item password, master password, BW session) is never returned to the model,
// logged, written to disk, or put in an error message. The session lives only in this process's memory.
import fs from 'node:fs';
import path from 'node:path';
import { execFile } from 'node:child_process';
import { createHash } from 'node:crypto';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

const ROOT = process.env.PWM_ROOT ? path.resolve(process.env.PWM_ROOT) : process.cwd();
const IDLE_MS = Math.max(1, Number(process.env.PWM_IDLE_MIN) || 10) * 60_000;
const NAME_RE = /^[A-Za-z0-9_.@-](?:[A-Za-z0-9_.@ -]{0,98}[A-Za-z0-9_.@-])?$/;
const KEY_RE = /^[A-Za-z_][A-Za-z0-9_]*$/;
const WIN = process.platform === 'win32';

let session = null; // BW session key, memory only
let idleTimer = null;

// Every child gets a clean env: never inherit a BW_SESSION from Claude Code's environment.
function childEnv(extra = {}) {
  const env = { ...process.env };
  delete env.BW_SESSION;
  delete env.PWM_MP;
  return { ...env, ...(session ? { BW_SESSION: session } : {}), ...extra };
}

// bw is a .cmd shim on Windows, so it needs a shell; every non-constant arg is validated first.
function run(file, args, { env = childEnv(), timeout = 20000, shell = false, hide = true } = {}) {
  return new Promise((resolve, reject) => {
    const a = shell && WIN ? args.map(x => (/\s/.test(x) ? `"${x}"` : x)) : args;
    const child = execFile(file, a, { encoding: 'utf8', env, shell, windowsHide: hide, timeout }, (err, stdout) =>
      err ? reject(new Error('command failed')) : resolve(stdout));
    child.stdin?.end();
  });
}

const bw = (args, opts) => run('bw', [...args, '--nointeraction'], { ...opts, shell: WIN });

// One tool call at a time: parallel `bw` calls collide, and two dialogs must never open together.
let queue = Promise.resolve();
const exclusive = fn => {
  const p = queue.then(fn);
  queue = p.catch(() => {});
  return p;
};

function touchIdle() {
  clearTimeout(idleTimer);
  if (!session) return;
  idleTimer = setTimeout(() => { lockVault().catch(() => {}); }, IDLE_MS);
  idleTimer.unref();
}

async function lockVault() {
  clearTimeout(idleTimer);
  const had = session;
  try { if (had) await bw(['lock']); } catch {}
  session = null;
  return Boolean(had);
}

async function vaultStatus() {
  try { return JSON.parse(await bw(['status'])).status; } catch { return 'unavailable'; }
}

// Windows password dialog. The master password goes user -> this process, never through the model.
// It comes back base64(UTF-8) over stdout so non-ASCII characters survive.
const DIALOG_PS = `
Add-Type -AssemblyName System.Windows.Forms
$f = New-Object Windows.Forms.Form
$f.Text = 'pwm-mcp: unlock vault'; $f.Size = New-Object Drawing.Size(380,170)
$f.StartPosition = 'CenterScreen'; $f.TopMost = $true; $f.FormBorderStyle = 'FixedDialog'
$f.MaximizeBox = $false; $f.MinimizeBox = $false
$l = New-Object Windows.Forms.Label; $l.Text = 'Bitwarden master password:'
$l.Location = New-Object Drawing.Point(12,12); $l.AutoSize = $true
$t = New-Object Windows.Forms.TextBox; $t.UseSystemPasswordChar = $true
$t.Location = New-Object Drawing.Point(12,40); $t.Width = 340
$ok = New-Object Windows.Forms.Button; $ok.Text = 'Unlock'; $ok.DialogResult = 'OK'
$ok.Location = New-Object Drawing.Point(196,85)
$no = New-Object Windows.Forms.Button; $no.Text = 'Cancel'; $no.DialogResult = 'Cancel'
$no.Location = New-Object Drawing.Point(277,85)
$f.AcceptButton = $ok; $f.CancelButton = $no
$f.Controls.AddRange(@($l,$t,$ok,$no))
if ($f.ShowDialog() -eq 'OK' -and $t.Text.Length -gt 0) {
  [Console]::Out.Write([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($t.Text)))
}
`;

async function askMasterPassword() {
  const enc = Buffer.from(DIALOG_PS, 'utf16le').toString('base64');
  let out;
  try {
    out = await run('powershell.exe', ['-NoProfile', '-STA', '-EncodedCommand', enc], { timeout: 120_000, hide: false });
  } catch {
    throw new Error('Password dialog failed or timed out.');
  }
  if (!out.trim()) throw new Error('Unlock cancelled.');
  return Buffer.from(out.trim(), 'base64').toString('utf8');
}

async function ensureUnlocked() {
  if (session && (await vaultStatus()) === 'unlocked') { touchIdle(); return; }
  session = null;
  const st = await vaultStatus();
  if (st === 'unauthenticated') throw new Error('Not logged in. Run "bw login" once, then retry.');
  if (st === 'unavailable') throw new Error('Cannot run the bw CLI (is it on PATH?).');
  if (!WIN) throw new Error('Unlock dialog is only implemented for Windows.');

  let mp = await askMasterPassword();
  try {
    const raw = (await bw(['unlock', '--passwordenv', 'PWM_MP', '--raw'], { env: childEnv({ PWM_MP: mp }) })).trim();
    if (!raw) throw new Error('empty');
    session = raw;
  } catch {
    throw new Error('Unlock failed (wrong master password?).');
  } finally {
    mp = null;
  }
  touchIdle();
}

async function getPassword(name) {
  if (!NAME_RE.test(name)) throw new Error('Invalid item name.');
  const items = JSON.parse(await bw(['list', 'items', '--search', name]));
  const hits = items.filter(it => it && it.type === 1 && it.name === name && it.login?.password);
  if (hits.length !== 1) throw new Error(`Expected exactly one login named "${name}", found ${hits.length}.`);
  return hits[0].login.password;
}

function resolveEnvPath(p) {
  const full = path.resolve(ROOT, p);
  const rel = path.relative(ROOT, full);
  if (rel.startsWith('..') || path.isAbsolute(rel)) throw new Error('Path must be inside the project folder.');
  if (!path.basename(full).startsWith('.env')) throw new Error('Only .env* files can be written.');
  if (!fs.existsSync(full)) throw new Error(`File not found: ${rel}`);
  return full;
}

function writeKey(file, key, value) {
  const q = /[\s#"'\\]/.test(value) ? '"' + value.replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"' : value;
  const raw = fs.readFileSync(file, 'utf8');
  const eol = raw.includes('\r\n') ? '\r\n' : '\n';
  const lines = raw.split(/\r?\n/);
  const re = new RegExp('^\\s*' + key + '\\s*=');
  const idx = lines.findIndex(l => re.test(l));
  const next = lines.slice();
  if (idx >= 0) next[idx] = `${key}=${q}`;
  else if (next.length && next[next.length - 1] === '') next.splice(next.length - 1, 0, `${key}=${q}`);
  else next.push(`${key}=${q}`);

  const tmp = path.join(path.dirname(file), `.env.tmp-${process.pid}`);
  try {
    fs.writeFileSync(tmp, next.join(eol), { mode: 0o600 });
    fs.renameSync(tmp, file);
  } catch {
    try { fs.unlinkSync(tmp); } catch {}
    throw new Error('Write failed; original file untouched.');
  }
  return idx >= 0 ? 'replaced' : 'appended';
}

const text = s => ({ content: [{ type: 'text', text: s }] });
const fail = e => ({ isError: true, ...text(e instanceof Error ? e.message : String(e)) });

const server = new McpServer({ name: 'pwm', version: '2.0.0' });

server.tool('vault_status', 'Report whether the vault is locked or unlocked (never prompts).', {}, () =>
  exclusive(async () => text(`Vault status: ${session ? await vaultStatus() : 'locked'}`)));

const ID_RE = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;

server.tool(
  'vault_list',
  'List what is in the vault, never passwords. kind=items: login item names (filter with search, organization_id, collection_id). kind=organizations: the user\'s organizations (names and ids). kind=collections: visible collections grouped by organization (names and ids; filter with organization_id). Prompts the user to unlock if needed.',
  {
    kind: z.enum(['items', 'organizations', 'collections']).default('items'),
    search: z.string().max(100).optional().describe('kind=items only: name filter'),
    organization_id: z.string().regex(ID_RE).optional().describe('kind=items or collections: only this organization'),
    collection_id: z.string().regex(ID_RE).optional().describe('kind=items only: only this collection'),
  },
  ({ kind, search, organization_id, collection_id }) => exclusive(async () => {
    try {
      const misuse = [
        search && kind !== 'items' && 'search',
        collection_id && kind !== 'items' && 'collection_id',
        organization_id && kind === 'organizations' && 'organization_id',
      ].filter(Boolean);
      if (misuse.length) throw new Error(`${misuse.join(', ')} not valid with kind=${kind}.`);
      if (search && !NAME_RE.test(search)) throw new Error('Invalid search text.');
      await ensureUnlocked();
      // every bw call below is sequential on purpose: parallel calls collide
      let out;
      if (kind === 'organizations') {
        const orgs = JSON.parse(await bw(['list', 'organizations']));
        out = orgs.length ? orgs.map(o => `${o.name}  [${o.id}]`).join('\n') : 'No organizations.';
      } else if (kind === 'collections') {
        const cols = JSON.parse(await bw(organization_id ? ['list', 'collections', '--organizationid', organization_id] : ['list', 'collections']));
        const orgs = JSON.parse(await bw(['list', 'organizations']));
        const orgName = new Map(orgs.map(o => [o.id, o.name]));
        const byOrg = new Map();
        for (const c of cols) {
          const k = orgName.get(c.organizationId) ?? c.organizationId ?? '(personal)';
          byOrg.set(k, [...(byOrg.get(k) ?? []), `  ${c.name}  [${c.id}]`]);
        }
        out = cols.length ? [...byOrg].map(([k, v]) => `${k}\n${v.sort().join('\n')}`).join('\n\n') : 'No collections.';
      } else {
        const args = ['list', 'items'];
        if (search) args.push('--search', search);
        if (organization_id) args.push('--organizationid', organization_id);
        if (collection_id) args.push('--collectionid', collection_id);
        const names = JSON.parse(await bw(args)).filter(it => it?.type === 1).map(it => it.name).sort();
        out = names.length ? names.join('\n') : 'No matching login items.';
      }
      touchIdle();
      return text(out);
    } catch (e) { return fail(e); }
  }),
);


server.tool(
  'fill_env',
  'Set one KEY in a .env file to the password of a vault login item. The value is never returned.',
  {
    key: z.string().regex(KEY_RE).describe('Env variable name, e.g. WIFI_PASSWORD'),
    item: z.string().describe('Exact name of the vault login item'),
    path: z.string().default('.env').describe('Path to the .env file, relative to the project'),
  },
  ({ key, item, path: p }) => exclusive(async () => {
    try {
      const file = resolveEnvPath(p);
      await ensureUnlocked();
      let value = await getPassword(item);
      const how = writeKey(file, key, value);
      const len = value.length;
      value = null;
      touchIdle();
      return text(`OK: ${key} ${how} in ${path.relative(ROOT, file)} from item "${item}" (${len} chars). Value not shown.`);
    } catch (e) { return fail(e); }
  }),
);

// Clipboard: the value goes user-clipboard only. Excluded from Windows clipboard history and cloud sync.
// The value reaches PowerShell through the child's env, never an argument; only its hash is kept here.
const PS_SET_CLIP = `
Add-Type -AssemblyName System.Windows.Forms
$d = New-Object Windows.Forms.DataObject
$d.SetText($env:PWM_CLIP)
if ($env:PWM_HIST -ne '1') {
  $d.SetData('ExcludeClipboardContentFromMonitorProcessing', (New-Object IO.MemoryStream(,[byte[]](1,0,0,0))))
  $d.SetData('CanIncludeInClipboardHistory', (New-Object IO.MemoryStream(,[byte[]](0,0,0,0))))
}
$d.SetData('CanUploadToCloudClipboard', (New-Object IO.MemoryStream(,[byte[]](0,0,0,0))))
[Windows.Forms.Clipboard]::SetDataObject($d, $true)
`;
const PS_CLEAR_IF_SAME = `
Add-Type -AssemblyName System.Windows.Forms
$t = [Windows.Forms.Clipboard]::GetText()
$h = [BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($t))).Replace('-','').ToLower()
if ($h -eq $env:PWM_HASH) { [Windows.Forms.Clipboard]::Clear() }
`;
const ps = (script, env) =>
  run('powershell.exe', ['-NoProfile', '-STA', '-EncodedCommand', Buffer.from(script, 'utf16le').toString('base64')],
    { env: childEnv(env), timeout: 15000 });

let clipTimer = null;
let pendingClear = null; // () => Promise, clears the clipboard if it still holds our value

async function clearClipboardNow() {
  clearTimeout(clipTimer);
  const fn = pendingClear;
  pendingClear = null;
  if (fn) { try { await fn(); } catch {} }
}

server.tool(
  'copy_password',
  'Copy a vault login password to the user\'s clipboard so they can paste it themselves. The value is never returned. The clipboard is cleared automatically.',
  {
    item: z.string().describe('Exact name of the vault login item'),
    clear_after_sec: z.number().int().min(5).max(300).default(30).describe('Seconds before the clipboard is cleared'),
    keep_in_history: z.boolean().default(true).describe('Keep it in Windows clipboard history (Win+V) so the user can paste it later'),
  },
  ({ item, clear_after_sec, keep_in_history }) => exclusive(async () => {
    try {
      if (!WIN) throw new Error('Clipboard copy is only implemented for Windows.');
      await ensureUnlocked();
      let value = await getPassword(item);
      await clearClipboardNow(); // an older copy must not outlive its own timer
      const hash = createHash('sha256').update(value, 'utf8').digest('hex');
      const len = value.length;
      await ps(PS_SET_CLIP, { PWM_CLIP: value, PWM_HIST: keep_in_history ? '1' : '0' });
      value = null;
      pendingClear = () => ps(PS_CLEAR_IF_SAME, { PWM_HASH: hash });
      clipTimer = setTimeout(() => { clearClipboardNow(); }, clear_after_sec * 1000);
      clipTimer.unref();
      touchIdle();
      return text(`OK: password of "${item}" (${len} chars) copied to the clipboard. Paste it yourself within ${clear_after_sec}s, then the live clipboard is cleared.${keep_in_history ? ' A copy stays in Windows clipboard history (Win+V) until the user deletes it.' : ''} Value not shown.`);
    } catch (e) { return fail(e); }
  }),
);

server.tool('lock_vault', 'Lock the vault and forget the session now.', {}, () =>
  exclusive(async () => text((await lockVault()) ? 'Vault locked.' : 'Vault was already locked.')));

const shutdown = () => { clearClipboardNow().then(lockVault).finally(() => process.exit(0)); };
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
process.stdin.on('end', shutdown);

await server.connect(new StdioServerTransport());
