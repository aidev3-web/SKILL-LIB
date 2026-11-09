---
name: technext-sales
description: The single entry point for TechNext sales work on the Proposal Portal. Claims an open job from the portal queue (generate_all, ingest_notes, regenerate) through the portal MCP tools and runs the generators — research, proposal, Sales Journey kit, quote module suggestions — against ONE version of the lead record, then saves each output as a draft for an approver to publish. Use when the person says "chạy việc mới", "run the open TechNext sales job for lead <slug>", "có việc gì trên portal", "cập nhật lead từ ghi chú họp", or arrives from the portal's New-lead button deep link.
---

# TechNext Sales — job runner

Implements §5.4/5.5 of `proposal-library/2026-11-05 Design – Một engine cho proposal, journey và báo giá.md`.
Code holds the contracts on the portal (`lib/lead.mjs`, `lib/leads.mjs`, `lib/jobs.mjs`, `lib/journey.mjs`,
`lib/adapters/findings.mjs`, `lib/pricing.mjs`); this skill only orchestrates and does the AI steps.
Never bypass a validator or a refusal to "make it pass".

## Entry
The portal's New-lead button opens Claude Code with exactly:
`Run the open TechNext sales job for lead <slug>: use the technext-sales skill, claim the job, and follow it.`
Without a slug ("chạy việc mới"), list the open jobs and let the person choose.

## Setup (once per machine, once per person)
**Portal address (the only place it is written):** `PORTAL = https://proposal-portal-preview.vercel.app`, MCP endpoint `PORTAL/api/v1/mcp`.
This is the **PREVIEW** address. It shares its data with production, and it will change to the production address after Trung merges `preview` into `main`; update this line only.

1. **Install this skill**: copy `skills/technext-sales/` to `~/.claude/skills/technext-sales/` (Windows: `%USERPROFILE%\.claude\skills\`), or `pull_skill` it from the TechNext skill library. The research and proposal steps also need `technext-sales-proposal` (with its sub-skills) and `technext-meeting-to-proposal` installed.
2. **Make your own token** on the portal: My tokens → scopes `read`, `facts.write`, `draft.write`, `jobs`. It is shown once. Never share it, never paste it in chat, a file in git, or a prompt.
3. **Store it in an environment variable** on your own machine, e.g. `TECHNEXT_PORTAL_TOKEN` (Windows: `setx TECHNEXT_PORTAL_TOKEN "<token>"` in a new terminal, then reopen Claude Code).
4. **Add the portal MCP server** so that Claude Code reads the token from that variable at run time; never write the token itself into a config file. Put this in `.mcp.json` (project) or the `mcpServers` of `~/.claude.json`:
   ```json
   {"mcpServers": {"technext-portal": {"type": "http", "url": "https://proposal-portal-preview.vercel.app/api/v1/mcp  (= PORTAL/api/v1/mcp above)",
     "headers": {"Authorization": "Bearer ${TECHNEXT_PORTAL_TOKEN}"}}}}
   ```
   (Claude Code expands `${...}` itself. Do not use `claude mcp add --header "...$TECHNEXT_PORTAL_TOKEN"` in a shell: the shell would expand it and store the real token in the config.)
5. **Test** in Claude Code: ask for `list_leads` or `get_price_matrix`. A `401` means the token is wrong or expired; `403 token_scope` names the missing scope. Do not retry until it is fixed.
6. The portal's **Open Claude Code** button needs Claude Code installed and run once on that machine (it registers the `claude-cli://` link). If nothing opens, use **Copy command** and paste it into Claude Code.

## Every write (LEAD-V1-CONTRACT.md)
- Every write carries a `command_id` (`^[A-Za-z0-9_-]{8,64}$`; a UUID works). Make one per logical write and keep it: on a timeout or network error, retry with the **same** `command_id` (the server returns the first result and writes nothing twice). A new attempt at a different change gets a new id. For `upload_kyc` it is the `command_id` argument (the server sends it as the `Command-Id` header).
- A reply with `suggested: [paths]` is **normal**: those fields were edited by a person on the portal and are locked, so your values became suggestions for them to accept or reject. Never retry, never work around it; mention it in the summary.
- `409 conflict` on `patch_journey` means a field changed since you read it: `get_page`/`get_lead` again, rebuild the change from the current value, and send a new `command_id`.

## Hard rules (design §2)
1. The AI never writes a price. Quote = module names with reasons; the portal computes prices (`lib/pricing.mjs`) and refuses any price-like field.
2. One profile per lead, research may re-run (Chuẩn LAI §8). A re-run only ADDS facts to the same profile, with source and version: agreeing facts raise confidence, conflicting ones are kept side by side for the lead owner to choose, never overwritten. Never keep a second copy of the client anywhere else.
3. No customer phone number or email anywhere: facts, prompts, outputs, job labels. Strip them before anything else. The server refuses them too.
4. Drafts only, labelled (Chuẩn LAI §7, soft review). Every output reaches the card at once marked "AI · not reviewed" with the profile version it read; an approver/admin removes the label on the portal (`.../outputs/<kind>/review`). A newer draft is "not reviewed" again automatically. This skill never reviews or publishes.
5. A follow-up already marked sent is never regenerated or changed.
6. Every generator in one run reads the same record version `V`, saved as `inputs.lead: V`.
7. The first person to claim a lead's job becomes its runner; later jobs of that lead are refused to anyone else (`409 runner_mismatch`). Report who the runner is and stop.

## Flow

1. **Claim.** `list_jobs {status: "open"}` → pick the job for `<slug>` (or let the person choose) → `claim_job {id}`.
   `409 job_taken`: someone else has it, stop. `409 runner_mismatch`: say who the runner is, stop.
2. **Load.** `get_lead {slug}` → keep `record.version` as `V`, `profile`, `stale`, `outputs`.
3. **Run by job kind** (below).
4. **Finish.** `complete_job {id}`; on any failure `fail_job {id, error}` with one line (validator message, missing scope, research blocked). Never save a draft that failed its validator. A claim left open goes back to the queue after 3 h.
5. **Open questions, then tell the person.** Never stop mid-run to ask (Chuẩn LAI §4, criterion 8): fill a gap with an assumption (an `assumed` fact or a quote `missing` key) and add a question to a list. At the end, save the list with `add_note {slug, command_id, label: "Open questions <date>", text: <one question per line, no phone or email>}` so it shows on the card. Stop to ask only when the run truly cannot go on (e.g. two companies with the same name). Then tell the person in a few lines: which drafts were saved (with versions, all "AI · not reviewed"), the open questions, and the next step for anything blocked, e.g. "Quote not computable: package missing. Neil records OOTB or Enterprise Core on the portal, or answer it in a meeting note."

### generate_all (New button)
The order matters (LEAD-V1-CONTRACT.md): **modules go before journey and KYC**, because the proposal reads `modules`; written after, they would make the KYC stale the moment it is saved.
0. `get_price_matrix` once; save it as `price-matrix.json` (module names = column 0, exact, case-sensitive).
1. **Research facts.** Run the `technext-sales-proposal` research phases (Phase 0 → Phase 1 → source-auditor), seeded from the form facts in `profile` → `audited-findings.json`. Then `node tools/findings-to-facts.mjs <audited-findings.json> --usable` → follow `docs/findings-picks-prompt.md` (at most one pick per key, `from` = finding indices; never `package`, never `modules` here) → `node tools/findings-to-facts.mjs <file> picks.json --by <name> --matrix price-matrix.json` → `add_facts {slug, command_id, facts}`. Research facts are `assumed`. (Only if the client's own words from a call are in a portal note may they be `confirmed`: pass `--note <id>`.) Formats the portal enforces (bad value = 400, nothing written): `users` digits only (`"6"`; prose goes in `client_words`); `addons` `"none"` or a comma list of `customization`, `training`, `migration`. Then `save_output {slug, command_id, kind: "research", body: <audited-findings>, inputs: {lead: V}}`.
2. **Modules.** Suggest the Odoo modules as ONE `add_facts` fact `{key: "modules", value: [<exact column-0 names>], grade: "assumed", source: {kind: "web", ref: <the finding URL or "research <date>">, at}}`. Never prices. Reload `get_lead`: its `record.version` is `V` for steps 3 and 4.
   **Package** (OOTB / Enterprise Core) is Neil's decision, not the AI's, and is never asked mid-run. Do not write it. Add the question "Which package: OOTB or Enterprise Core?" to the open questions; the quote stays "not computable: package" until a person records it on the portal (sign-in) or a meeting note states it (then `ingest_notes` writes it as a confirmed fact citing that note).
3. **Journey.** The `sales-journey` `kit.md` recipe with `profile` + `playbook.json` → `{kit, vars}`; check with `node lib/journey.mjs`. First run: `save_output {slug, command_id, kind: "journey", body: {kit, vars}, inputs: {lead: V, playbook}}`. When a journey already exists: `get_page {slug}`, then `patch_journey {slug, command_id, changes: [{path, from, to}]}` with paths under `kit.*` / `vars.*` only, `from` = the current value.
4. **KYC (the proposal page).** Build it with the `technext-sales-proposal` writing/assembly/validation phases from the record, then `upload_kyc {slug, command_id, html}`. The HTML must be ONE self-contained file (≤ 4 MB): inline CSS and JS only (no CDN, no external script or stylesheet), images and fonts only as `data:` URIs, no fetch/XHR/form posts, every link `target="_blank" rel="noopener"`, no service worker or web manifest, and **no customer phone number or email**. Its **Quotation section names the modules only — never a price, total, rate or currency**; the portal prices the quote.
5. **Quote draft (optional).** `save_output {slug, command_id, kind: "quote", body: {modules: [{module, reason}], missing?: [keys], label}, inputs: {lead: V, matrix}}`: no price fields of any kind. Fix any `warnings[]` (unknown module names) and save again with a new `command_id`.
6. `complete_job {id}`.

### ingest_notes (notes added on a card)
The job points at a portal note (`get_note {slug, id}` returns its text; contacts were already stripped by the portal, but treat it as if they were not). **Raw notes are never sent anywhere else or stored outside that note**: not in a fact, an output, a job, a prompt to another tool, or a kept file.
1. `stripContacts(text)` from the portal's `lib/notes.mjs` (`node -e` or a small script) BEFORE any extraction; work only on the stripped text.
2. Extract facts: `confirmed`, `source.kind` `call` or `meeting`, only FACT_KEYS; use `supersedes` when replacing an earlier fact of the same key.
3. `checkExtractedFacts(facts, {noteId, date, record, matrixModules})` from `lib/notes.mjs` BEFORE `add_facts`: every confirmed fact cites the note id as `source.ref` (the portal refuses confirmed facts from a token that cite anything else, and rejects the whole batch). Fix the facts on errors; never bypass it.
4. `add_facts {slug, command_id, facts}`, then `complete_job`. The portal recomputes `stale`; regenerate jobs follow.

### regenerate (stale outputs only)
Regenerate exactly the kinds listed in `get_lead`'s `stale`, nothing else (staleness comes from `staleOutputs`: an older `inputs.lead` alone is not stale).
- proposal: update, do not rebuild — `technext-meeting-to-proposal` with the new facts and the `research` output; same artifact link.
- journey: rerun the kit. Before saving any regenerated follow-up, read the lead's followup-state (`GET /api/v1/followup-state/<slug>`) and pass old drafts, new drafts and that state through `mergeFollowups` (`lib/followups.mjs`): sent drafts stay byte-for-byte (the saved sent text), changed unsent ones are labelled "Updated". Never rewrite a sent draft.
- quote: rerun the module suggestion.
Then write each with a new `command_id` and the new `V`: journey via `patch_journey` (only the changed `kit.*`/`vars.*` paths), proposal via `upload_kyc`, quote via `save_output`.

## How sales-journey reads a lead (draft, for its owner to adopt)
Replace `research.md` and the local `lead.json` profile with `get_lead {slug}` (or `GET /api/v1/leads/<slug>` with a `read` token): use `profile` for `{industry, size, location, regulatory, risks}` and `record.version` as `inputs.lead`. The sales-entered fields (`current_system`, `users`, `departments`, …) become facts through `add_facts` instead of living only in the page.
