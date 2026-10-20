// PreToolUse hook (Bash): stop Claude from reading a real .env through the shell.
// Allowed: running fill-env.js on its own (no chaining). Blocked: any other command that mentions a .env file.
const { readInput, block } = require('./lib');

const input = readInput();
const cmd = String((input.tool_input && input.tool_input.command) || '');

// a ".env" file name that is not ".env.example" / ".env.sample"
const mentionsEnv = /(^|\W)\.env(?![\w-])(?![.\w-]*(example|sample))/i.test(cmd);
if (!mentionsEnv) process.exit(0);

const isFill = /fill-env\.js/.test(cmd) && !/[;&|<>`$()\r\n]/.test(cmd);
if (isFill) process.exit(0);

block('Blocked: reading a .env file from the shell is not allowed (it holds real keys). Use .claude/hooks/fill-env.js to set a value, or ask the user.');
