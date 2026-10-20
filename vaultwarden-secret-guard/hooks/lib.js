// Shared helpers for the Bitwarden placeholder hooks (V2).
// Rule: never print or log a secret value. Only placeholders may reach stdout/stderr text.
const fs = require('fs');
const { execFileSync } = require('child_process');

// Item names: ASCII letters, digits and _ . @ - ; single spaces allowed inside (not at the ends).
// Everything else (& | < > " ^ % ` $ ; quotes ...) never matches, so it can never reach a shell.
const NAME_CHARS = 'A-Za-z0-9_.@ -';
const NAME = `[A-Za-z0-9_.@-](?:[${NAME_CHARS}]{0,98}[A-Za-z0-9_.@-])?`;
const NAME_RE = new RegExp(`^${NAME}$`);
const PLACEHOLDER = new RegExp(`\\{\\{bw:(${NAME})\\}\\}`, 'g');
const MIN_SECRET_LEN = 6;

function readInput() {
  return JSON.parse(fs.readFileSync(0, 'utf8'));
}

function mapStrings(v, f) {
  if (typeof v === 'string') return f(v);
  if (Array.isArray(v)) return v.map(x => mapStrings(x, f));
  if (v && typeof v === 'object') {
    return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, mapStrings(x, f)]));
  }
  return v;
}

// bw is a .cmd/.ps1 shim on Windows, so cmd.exe is needed and Node joins args WITHOUT quoting.
// Every non-constant arg is NAME_RE-validated first, so wrapping in double quotes is safe.
// stdin must be an empty pipe plus --nointeraction, or bw hangs when a hook's stdin is a pipe.
function bw(args) {
  const win = process.platform === 'win32';
  const a = [...args, '--nointeraction'].map(x => (win && /\s/.test(x) ? `"${x}"` : x));
  return execFileSync('bw', a, {
    encoding: 'utf8',
    shell: win,
    windowsHide: true,
    stdio: ['pipe', 'pipe', 'pipe'],
    input: '',
    timeout: 30000,
  });
}

// Exact-name lookup. `bw get` matches substrings, so "test" could return "test_shared"; this does not.
function getPassword(name) {
  if (!NAME_RE.test(name)) throw new Error('bad name');
  const items = JSON.parse(bw(['list', 'items', '--search', name]));
  const hits = items.filter(it => it && it.type === 1 && it.name === name && it.login && it.login.password);
  if (hits.length !== 1) throw new Error('not exactly one login named that');
  return hits[0].login.password;
}

// value -> placeholder map built in memory only (never written to disk)
function secretMap() {
  const items = JSON.parse(bw(['list', 'items']));
  const map = new Map();
  for (const it of items) {
    const pw = it && it.login && it.login.password;
    if (typeof pw === 'string' && pw.length >= MIN_SECRET_LEN && NAME_RE.test(it.name)) {
      map.set(pw, `{{bw:${it.name}}}`);
    }
  }
  return map;
}

function block(msg) {
  process.stderr.write(msg + '\n');
  process.exit(2);
}

module.exports = { NAME_RE, PLACEHOLDER, readInput, mapStrings, getPassword, secretMap, block };
