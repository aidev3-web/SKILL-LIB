// PostToolUse hook (Bash): if the output contains a known password, turn it back into its placeholder.
// The value->placeholder map lives only in this process's memory.
const { readInput, mapStrings, secretMap } = require('./lib');

const input = readInput();
let map;
try {
  map = secretMap();
} catch {
  process.exit(0); // vault locked or bw missing: nothing known to scrub
}
if (map.size === 0) process.exit(0);

// longest values first so a short secret never breaks a longer one
const pairs = [...map.entries()].sort((a, b) => b[0].length - a[0].length);
let changed = false;
const out = mapStrings(input.tool_response, s => {
  let r = s;
  for (const [val, ph] of pairs) {
    if (r.includes(val)) {
      r = r.split(val).join(ph);
      changed = true;
    }
  }
  return r;
});

if (!changed) process.exit(0);
process.stdout.write(JSON.stringify({ hookSpecificOutput: { hookEventName: 'PostToolUse', updatedToolOutput: out } }));
