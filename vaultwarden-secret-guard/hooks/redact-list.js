// PostToolUse hook for mcp__bitwarden__list: replace secrets in the result with placeholders.
const { readInput, mapStrings } = require('./lib');

const input = readInput();
const ph = name => `{{bw:${name}}}`;

function redactItem(it) {
  if (!it || typeof it !== 'object') return it;
  const name = String(it.name || 'item');
  if (it.login && typeof it.login === 'object') {
    if (it.login.password) it.login.password = ph(name);
    if (it.login.totp) it.login.totp = ph(name + '.totp');
  }
  if (Array.isArray(it.passwordHistory) && it.passwordHistory.length) {
    it.passwordHistory = it.passwordHistory.map(() => ({ password: ph(name + '.old') }));
  }
  if (Array.isArray(it.fields)) {
    it.fields = it.fields.map(f => (f && f.type === 1 ? { ...f, value: ph(name + '.' + (f.name || 'field')) } : f));
  }
  if (it.card && typeof it.card === 'object') {
    if (it.card.number) it.card.number = ph(name + '.card');
    if (it.card.code) it.card.code = ph(name + '.cvv');
  }
  return it;
}

function redactString(s) {
  try {
    const j = JSON.parse(s);
    const out = Array.isArray(j) ? j.map(redactItem) : redactItem(j);
    return JSON.stringify(out);
  } catch {
    // Not JSON: fail closed if it looks like it carries a secret field.
    return /"(password|totp|code|number)"\s*:/.test(s) ? '[redacted: could not parse Bitwarden output]' : s;
  }
}

const out = mapStrings(input.tool_response, redactString);
process.stdout.write(JSON.stringify({ hookSpecificOutput: { hookEventName: 'PostToolUse', updatedToolOutput: out } }));
