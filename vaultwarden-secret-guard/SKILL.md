---
name: vaultwarden-secret-guard
description: Use a Bitwarden/Vaultwarden password in a command, a browser form or a .env file without ever seeing or printing it, using vault placeholders and a set of Claude Code hooks that block reading .env files and scrub secrets from output. Use when a task needs a password, API key or login from the vault, when asked to fill a .env value, log in to a site, install this secret guard in another project, or when a command was blocked with "reading a .env file from the shell is not allowed". Trigger phrases include "điền mật khẩu từ vault", "lấy key từ Bitwarden", "chặn đọc .env", "vaultwarden", "bw unlock".
---

# Vaultwarden secret guard

Claude must be able to *use* a secret without being able to *read* it. Secrets live in Bitwarden/Vaultwarden. Claude only writes the item's name inside a placeholder, and a hook swaps in the real value just before the tool runs.

Placeholder syntax: two opening braces, `bw:`, the exact item name, two closing braces (for example the item `OpenRouter` becomes `{{bw:OpenRouter}}`). Never type a placeholder in a command that merely *documents* it: the hook resolves every placeholder it sees and blocks the call if it cannot.

## Rules for Claude

1. **Never read a `.env` file** (no `cat`, `type`, `Get-Content`, `grep`, and no Read or Grep tool on it). `.env.example` and `.env.sample` are fine.
2. **Never ask the user to paste a password into the chat.** Use the vault.
3. To use a secret in a Bash command or a Chrome `form_input`, write the placeholder where the value goes. The item must be a Login, and its name must match exactly one item (letters, digits, `_ . @ -`, single inner spaces).
4. To set a value in `.env`, run exactly this, alone on the line (no `;`, `&&`, `|`, redirects or `$()`):
   `node .claude/hooks/fill-env.js <ENV_KEY> "<Item Name>" <path-to-.env>`
   It writes only that one key, prints nothing secret, and verifies the other lines are unchanged.
5. `mcp__bitwarden__list` returns passwords, TOTP, card numbers and CVV already replaced by placeholders; the names are the only usable handle.
6. Never echo, log, save to a file, or put a resolved secret in a commit, PR, report or screenshot. If a secret value ever appears in output, tell the user and recommend rotating it.
7. If a hook blocks a call, do not look for a way around it. Use `fill-env.js` or a placeholder, or ask the user.

## What the hooks do (all in `hooks/`)

| File | Event | Effect |
|---|---|---|
| `guard-env.js` | PreToolUse Bash, PowerShell | Blocks any command mentioning a real `.env`; only a bare `fill-env.js` call passes |
| `resolve.js` | PreToolUse Bash, Chrome `form_input` | Replaces each placeholder with the real password; blocks the call if the vault is locked or the name is not unique |
| `redact-list.js` | PostToolUse `mcp__bitwarden__list` | Redacts secrets in the listing |
| `scrub-output.js` | PostToolUse Bash, Chrome tools | Turns any known password in the output back into its placeholder |
| `fill-env.js` | Run by Claude | Writes one `.env` key from a vault item without printing it |
| `lib.js` | shared | Name validation and the `bw` CLI wrapper |

## Install in a project

1. Copy `hooks/*.js` to `<project>/.claude/hooks/`.
2. Merge `settings-snippet.json` into `<project>/.claude/settings.json` (or `settings.local.json`), keeping existing hooks.
3. Requirements: Node.js, the Bitwarden CLI `bw` on PATH, and an unlocked vault (`bw unlock`, with the session available to the hook's environment).
4. Test with a harmless vault item: run a command that uses its placeholder, then confirm that `cat .env` is blocked.

## Known limits

- Only shell commands are guarded for `.env`. The Read and Grep tools are not, so rule 1 is also a behaviour rule.
- Scrubbing matches the exact password string; an encoded or split copy (base64, chunks) is not caught.
- Secrets shorter than 6 characters are not scrubbed.
- With a locked vault, `resolve.js` fails closed (blocks) and `scrub-output.js` does nothing.
