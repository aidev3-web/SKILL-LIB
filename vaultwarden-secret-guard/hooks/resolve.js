// PreToolUse hook (Bash): replace {{bw:name}} with the real password just before the command runs.
// Fails closed: any lookup problem blocks the tool call, so a raw placeholder is never sent on.
const { PLACEHOLDER, readInput, mapStrings, getPassword, block } = require('./lib');

const input = readInput();
const cache = new Map();
let failed = null;

const out = mapStrings(input.tool_input, s =>
  s.replace(PLACEHOLDER, (_, name) => {
    if (cache.has(name)) return cache.get(name);
    try {
      const v = getPassword(name);
      cache.set(name, v);
      return v;
    } catch {
      failed = failed || name;
      return '';
    }
  })
);

if (failed) {
  block(`Bitwarden hook: cannot resolve {{bw:${failed}}}. Is the vault unlocked (bw unlock), and is there exactly one item with that name?`);
}
if (cache.size === 0) process.exit(0); // nothing to substitute: leave the call untouched

process.stdout.write(JSON.stringify({ hookSpecificOutput: { hookEventName: 'PreToolUse', updatedInput: out } }));
