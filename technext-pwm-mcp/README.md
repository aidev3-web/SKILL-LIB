# technext-pwm-mcp

A small MCP server that lets an AI agent *use* a Bitwarden/Vaultwarden password without ever *seeing* it. The agent asks for an action ("fill item X into variable Y"). The server unlocks the vault, fetches the password and puts it into a `.env` file or the clipboard. The agent only gets back a sentence such as "written, 8 characters".

Windows only (the unlock dialog and clipboard use PowerShell). Tried on Node 24; the MCP SDK needs Node 18 or newer.

## Tools

| Tool | What it does | Returned to the agent |
|---|---|---|
| `vault_status` | Reports locked or unlocked, never prompts | locked / unlocked |
| `vault_list` | `kind=items` (filter by `search`, `organization_id`, `collection_id`), `organizations`, or `collections` | names (and ids for orgs and collections) |
| `fill_env` | Writes one item's password into one variable of a `.env*` file inside the project | variable, item, character count |
| `copy_password` | Copies a password to the clipboard, cleared after `clear_after_sec` (5-300, default 30); `keep_in_history` keeps it in Win+V history | character count |
| `lock_vault` | Locks the vault and drops the session now | confirmation |

No tool returns a password to the agent.

## How it keeps secrets out of the chat

- When the vault is locked, a Windows dialog asks the user for the master password. It goes from the user into the server, never through the agent.
- The Bitwarden session lives only in the server's memory. It is not written to a file or set in a global environment, and `BW_SESSION` from the parent environment is ignored.
- The vault locks itself after 10 idle minutes (`PWM_IDLE_MIN`) and when the server exits.
- Tool calls run one at a time, so parallel `bw` calls cannot collide.
- `fill_env` only writes `.env*` files inside the project folder (`PWM_ROOT`).

## Install

1. Install Node.js and the Bitwarden CLI (`bw`) and put both on PATH.
2. Log in once, in your own terminal: `bw config server <your-vaultwarden-url>` then `bw login`.
3. Copy this folder into your project (for example as `pwm-mcp/`) and run `npm install` in it.
4. Add the server to the project's `.mcp.json`. Do **not** put `BW_SESSION` here.

   ```json
   {
     "mcpServers": {
       "pwm": {
         "command": "node",
         "args": ["pwm-mcp/server.mjs"],
         "env": { "PWM_ROOT": ".", "PWM_IDLE_MIN": "10" }
       }
     }
   }
   ```

5. Recommended, in `.claude/settings.json`:

   ```json
   { "permissions": { "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./.mcp.json)"] } }
   ```

6. Restart Claude Code, or run `/mcp` and reconnect `pwm`. You should see 5 tools.

## Known limits

- While a password is in the clipboard (or in Win+V history when `keep_in_history` is on), other programs on the machine can read it. A history entry is not removed automatically.
- Blocking reads of `.env` through `permissions.deny` happens in the agent's tools, not in the operating system. Nothing stops a user from pasting a password into the chat themselves.
- The unlock dialog, auto-lock, `copy_password` and `vault_list` (organizations and collections) have not been verified against a real vault on a clean machine.
