// Usage: node fill-env.js <ENV_KEY> <bitwarden_item_name> <path-to-.env>
// Sets ENV_KEY in the .env file to the password of the Bitwarden item, without ever printing it.
// Only the target line changes; every other line is verified byte-for-byte after the write.
const fs = require('fs');
const path = require('path');
const { getPassword, NAME_RE } = require('./lib');

const [key, item, file] = process.argv.slice(2);
const fail = msg => { console.error('fill-env: ' + msg); process.exit(1); };

if (!key || !item || !file) fail('usage: node fill-env.js <ENV_KEY> <item_name> <path-to-.env>');
if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(key)) fail('invalid ENV_KEY');
if (!NAME_RE.test(item)) fail('invalid item name (ASCII letters, digits, _ . @ - and inner spaces only)');
if (!fs.existsSync(file)) fail('file not found: ' + file);

let value;
try { value = getPassword(item); } catch { fail('cannot read item "' + item + '" (vault locked, or not exactly one item with that name)'); }

const q = /[\s#"'\\]/.test(value) ? '"' + value.replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"' : value;
const raw = fs.readFileSync(file, 'utf8');
const eol = raw.includes('\r\n') ? '\r\n' : '\n';
const lines = raw.split(/\r?\n/);
const re = new RegExp('^\\s*' + key + '\\s*=');
const idx = lines.findIndex(l => re.test(l));
const next = lines.slice();
if (idx >= 0) next[idx] = key + '=' + q;
else { if (next.length && next[next.length - 1] === '') next.splice(next.length - 1, 0, key + '=' + q); else next.push(key + '=' + q); }

// atomic write: temp file in same folder, then rename over the original
const tmp = path.join(path.dirname(file), '.env.tmp-' + process.pid);
try {
  fs.writeFileSync(tmp, next.join(eol), { mode: 0o600 });
  fs.renameSync(tmp, file);
} catch (e) {
  try { fs.unlinkSync(tmp); } catch {}
  fail('write failed, original file untouched');
}

// verify: all other lines identical, target line present
const after = fs.readFileSync(file, 'utf8').split(/\r?\n/);
const targetAt = idx >= 0 ? idx : after.findIndex(l => re.test(l));
if (targetAt < 0 || !re.test(after[targetAt])) fail('verification failed: target line missing');
// replace keeps every index; append only adds one line, so compare the original lines before it
const keep = idx >= 0 ? lines.length : lines.length - (lines[lines.length - 1] === '' ? 1 : 0);
let diff = 0;
for (let i = 0; i < keep; i++) {
  if (i !== idx && lines[i] !== after[i]) diff++;
}
if (idx >= 0 && after.length !== lines.length) diff++;
if (diff > 0) fail('verification failed: other lines changed (' + diff + ')');

console.log('OK: ' + key + ' set from {{bw:' + item + '}} (' + value.length + ' chars). ' + (idx >= 0 ? 'Replaced existing line.' : 'Appended new line.') + ' Other lines unchanged.');
