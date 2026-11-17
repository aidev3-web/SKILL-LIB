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

The AI worker sends `Run the open TechNext sales job <job id> for lead <slug>: use the technext-sales skill.` plus some of these lines (only then do these rules apply):
- A job id in the first line: claim only that job (`claim_job {id: <job id>}`), never another one.
- `This job is already claimed by you: do not claim it again; continue from the checkpoint.`: skip the claim step; go on from the outputs already saved for that job.
- `Use command_id prefix: P (append facts|research|journey|kyc|quote|note).`: copy `P` exactly as given (e.g. `wghijabcdklmnopef-`: the worker writes the job id without digits, since the portal refuses ids that look like a phone number); every write uses `command_id` = `P` + that suffix (e.g. `P` + `facts` for `add_facts`, `P` + `kyc` for the KYC upload or `save_kyc_brief`, `P` + `note` for the open questions note). Ids are per job: the same id on every resume; a skipped step keeps its number. A second write of the same kind in a job adds `-2`, `-3`, ... (the modules fact in generate_all step 2 is `P` + `facts-2`; a quote saved again after `warnings[]` is `P` + `quote-2`).
- With a prefix, a write that returns `replayed: true` or `409 command_reused` was already done: treat that step as finished and go on.

## Setup (once per machine, once per person)
**Portal address (the only place it is written):** `PORTAL = https://proposal-library-blue.vercel.app`, MCP endpoint `PORTAL/api/v1/mcp`.

**Helper kit (`KIT`):** the `kit/` folder next to this SKILL.md (for example `~/.claude/skills/technext-sales/kit`). It holds the portal's own helper scripts and data (`tools/findings-to-facts.mjs`, `lib/lead/notes.mjs`, `lib/journey/journey.mjs`, `data/playbook.json`, `docs/findings-picks-prompt.md`), copied from the portal repo by `node tools/build-skill-kit.mjs` (see `kit/KIT.json` for the portal commit). They need Node 18+ only, no install and no portal checkout, so this skill runs on any machine. Never edit files in `kit/` by hand: rebuild it from the portal repo.

**`save_output` shape:** the MCP tool takes `{slug, kind, body}` and sends `body` to the portal as it is, so `command_id` and `inputs` go INSIDE `body`, next to the output itself: `save_output {slug, kind, body: {command_id, body: <output>, inputs: {lead: V, ...}}}`.
This is the **production** address.

1. **Install this skill**: copy `skills/technext-sales/` to `~/.claude/skills/technext-sales/` (Windows: `%USERPROFILE%\.claude\skills\`), or `pull_skill` it from the TechNext skill library. The research and proposal steps also need `technext-sales-proposal` (with its sub-skills) and `technext-meeting-to-proposal` installed.
2. **Connect the portal MCP**: open the portal, press **Connect MCP** in the tab row (Leads, Changes, Costing, ...), copy the prompt and paste it into Claude Code. It removes old portal servers and adds `technext-proposal-portal` (production; on the preview site it adds `preview-proposal-portal`). Quit Claude Code completely, open it again, run `/mcp`, choose the server, press **Authenticate** and sign in with your TechNext Google account. No token is needed and none is ever written to a file.
3. **Test** in Claude Code: ask for `list_leads` or `get_price_matrix`. A `401` means you are not signed in (run `/mcp` → Authenticate again); `403 token_scope` names the missing scope. Do not retry until it is fixed.
4. The portal's **Open Claude Code** button needs Claude Code installed and run once on that machine (it registers the `claude-cli://` link). If nothing opens, use **Copy command** and paste it into Claude Code.

## Model: Claude Sonnet 5.5 only (check first)
Before claiming any job, check which model you are running as (it is stated in your system prompt).
- Allowed: **Claude Sonnet 5.5** (model id `claude-sonnet-5-5`), and only that.
- Also allowed: any model id listed in env `TECHNEXT_ALLOWED_MODELS` (comma-separated). Read it with `node -e "console.log(process.env.TECHNEXT_ALLOWED_MODELS||'')"` (works in every shell). Compare it with the model id stated in your system prompt; ids that differ only by a bracket suffix like `[1m]` are equal. `producer.model` is always the model you actually run as.
- Anything else (Opus, Haiku, Fable, an older Sonnet, or an unknown model) not allowed above: do NOT claim the job. Tell the person in one line: "This skill runs only on Sonnet 5.5. Type `/model sonnet`, check it says Sonnet 5.5, then run the same command again." (With a job id in the prompt, nobody can type `/model`: say in one line which model you run as and that it is not allowed.) Then stop. Nothing has been claimed, so the job stays open for the next run.
- Every subagent or Agent call this run starts (for example the research agents of `technext-sales-proposal`) is started with `model: "sonnet"` too. Never pass `opus`, `haiku` or `fable`.
- Put the model you run as in the end-of-run summary (e.g. "Model: Sonnet 5.5").

## Progress updates: at least every 3 minutes
A run takes about 30 minutes and the research alone can take 20. Never go quiet. People read silence as "it is stuck".
- **At least once every 3 minutes of work**, and at the end of every step, write ONE short line in the chat:
  `[mm:ss] <step k/6> <what just finished> · <what was saved on the portal, with version> · next: <what comes now>`
  e.g. `[06:10] 1/6 research: 3 of 4 research groups done · nothing saved yet · next: group D, then facts`
  e.g. `[19:40] 2/6 facts saved (version 4, 11 facts) · next: modules`
- Count the time from the claim. During a long step (research, KYC build), write a line when each sub-part finishes (each research group, each section batch) even if it is under 3 minutes, and a "still working on <what>" line if 3 minutes pass with nothing new.
- Say what changed on the portal in each line: facts added (version), output saved (kind + version), KYC uploaded, rejected (400) and fixed. A rejected save is reported, not hidden.
- Keep it to one line each: no tables, no repeats of earlier lines. The full summary comes once, at the end.
- **Worker mode** (a tool named `save_kyc_brief` is available): `k/6` is the portal's progress bar step, written when that step starts: **1/6 Verify** (company identity: legal name, website, country), **2/6 Research** (web, social, competitors), **3/6 Source check** (source-auditor: every citation is on its source page), **4/6 Facts** (`add_facts`, the research output, modules), **5/6 Drafts** (journey, the `kyc.brief.v1` brief, the quote draft), **6/6 Save** (`save_kyc_brief`, the open questions note, `complete_job`). Never call `report_progress`: the worker reads these lines and reports progress itself. Write the `6/6 Save` line BEFORE `complete_job`: after the job is closed the portal no longer accepts a step.

## Every write (LEAD-V1-CONTRACT.md)
- Every write carries a `command_id` (`^[A-Za-z0-9_-]{8,64}$`; a UUID works). Make one per logical write and keep it: on a timeout or network error, retry with the **same** `command_id` (the server returns the first result and writes nothing twice). A new attempt at a different change gets a new id. For `upload_kyc` it is the `command_id` argument (the server sends it as the `Command-Id` header).
- **Producer (who made this output).** Every `upload_kyc` and every `save_output` sends `producer: {skill, commit, model}`: `skill` = `technext-sales`; `commit` = the first 7 characters of the `commit` field in the `.source.json` file of this skill folder; `model` = the model name you are running as. If there is no `.source.json` file, omit `producer` entirely: never invent a commit or a model. The portal rejects a malformed value with 400 `invalid_producer` (it names the field, never the value); fix the value and retry with the same `command_id`.
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

0. **Model check** (section above). Not an allowed model: stop before claiming. Then write the first progress line: `[00:00] 0/6 starting job for <slug>`.
1. **Claim.** `list_jobs {status: "open"}` → pick the job for `<slug>` (or let the person choose) → `claim_job {id}`. With a job id in the prompt, claim that job only; with "already claimed by you", skip this step (see Entry).
   `409 job_taken`: someone else has it, stop. `409 runner_mismatch`: say who the runner is, stop.
2. **Load.** `get_lead {slug}` → keep `record.version` as `V`, `profile`, `stale`, `outputs`.
3. **Run by job kind** (below).
4. **Finish.** `complete_job {id}`; on any failure `fail_job {id, error}` with one line (validator message, missing scope, research blocked). Never save a draft that failed its validator. A claim left open goes back to the queue after 3 h.
5. **Open questions, then tell the person.** Never stop mid-run to ask (Chuẩn LAI §4, criterion 8): fill a gap with an assumption (an `assumed` fact or a quote `missing` key) and add a question to a list. At the end, save the list with `add_note {slug, command_id, label: "Open questions <date>", text: <one question per line, no phone or email>}` so it shows on the card. The portal queues an `ingest_notes` job for every new note, and this note holds your own questions, not client words: the reply is `{id, job}`, and when `job` carries an `id`, close that job at once with `claim_job {id: job.id}` then `complete_job {id: job.id}` (nothing to extract; a job left open keeps the lead page on "Waiting for the AI"). When `job` is `null` the portal queued nothing, so do nothing. If that `complete_job` answers with `regenerate`, leave the new job in the queue. Stop to ask only when the run truly cannot go on (e.g. two companies with the same name). Then tell the person in a few lines: which drafts were saved (with versions, all "AI · not reviewed"), the open questions, and the next step for anything blocked, e.g. "Quote not computable: package missing. Neil records OOTB or Enterprise Core on the portal, or answer it in a meeting note."

### generate_all (New button)
The order matters (LEAD-V1-CONTRACT.md): **modules go before journey and KYC**, because the proposal reads `modules`; written after, they would make the KYC stale the moment it is saved.
0. `get_price_matrix` once; save it as `price-matrix.json` (module names = column 0, exact, case-sensitive).
0b. **Notes from lead creation.** When the job's `ref.note` is set (the person typed notes on the Create lead form), `get_note {slug, id: ref.note}` and `stripContacts(text)` from `KIT/lib/lead/notes.mjs` before reading it, as in `ingest_notes`. The raw note is never copied anywhere else (no fact, output, prompt to another tool or kept file). Read it as four kinds of input:
   - **Company notes** (what the person knows about the company): steer Phase 0 and Phase 1 (where to look, which names, products, sites). They are hints, not facts.
   - **Things to verify**: each becomes a check in research. Verified: a fact with its web source. Not verified: an open question.
   - **A past meeting or call** (date, who, what the client said): only the client's own words from that meeting may become `confirmed` facts, `source.kind` `meeting` or `call` citing the note (`findings-to-facts.mjs ... --note <ref.note>`, then `checkExtractedFacts` with `noteId`). Everything else stays `assumed`. In the KYC, `meeting-minutes` records that meeting (date, attendees by role, what was said, agreed next steps) instead of "no meeting yet", and `pre-meeting` does not say the client has not been contacted.
   - **Links to minutes or documents**: read each with web fetch (a Google Doc must be shared for viewing). A readable one counts as that meeting's notes, under the same rules. One that cannot be opened becomes the open question "Link <host> needs view access", and the run goes on.
   With no `ref.note`, skip this step.
1. **Research facts.** Run the `technext-sales-proposal` research phases (Phase 0 → Phase 1 → source-auditor), seeded from the form facts in `profile` → `audited-findings.json`. Then `node KIT/tools/findings-to-facts.mjs <audited-findings.json> --usable` → follow `KIT/docs/findings-picks-prompt.md` (at most one pick per key, `from` = finding indices; never `package`, never `modules` here) → `node KIT/tools/findings-to-facts.mjs <file> picks.json --by <name> --matrix price-matrix.json` → `add_facts {slug, command_id, facts}`. Research facts are `assumed`. (Only if the client's own words from a call are in a portal note may they be `confirmed`: pass `--note <id>`.) Formats the portal enforces (bad value = 400, nothing written): `users` digits only (`"6"`; prose goes in `client_words`); `addons` `"none"` or a comma list of `customization`, `training`, `migration`. Then `save_output {slug, kind: "research", body: {command_id, body: <audited-findings>, inputs: {lead: V}}}`.
2. **Modules.** Suggest the Odoo modules as ONE `add_facts` fact `{key: "modules", value: [<exact column-0 names>], grade: "assumed", source: {kind: "web", ref: <the finding URL or "research <date>">, at}}`. Never prices. Reload `get_lead`: its `record.version` is `V` for steps 3 and 4.
   **Package** (OOTB / Enterprise Core) is Neil's decision, not the AI's, and is never asked mid-run. Do not write it. Add the question "Which package: OOTB or Enterprise Core?" to the open questions; the quote stays "not computable: package" until a person records it on the portal (sign-in) or a meeting note states it (then `ingest_notes` writes it as a confirmed fact citing that note).
3. **Journey.** The `sales-journey` `kit.md` recipe with `profile` + `KIT/data/playbook.json` → `{kit, vars}`; check with `node KIT/lib/journey/journey.mjs`. First run: `save_output {slug, kind: "journey", body: {command_id, body: {kit, vars}, inputs: {lead: V, playbook}}}`. When a journey already exists: `get_page {slug}`, then `patch_journey {slug, command_id, changes: [{path, from, to}]}` with paths under `kit.*` / `vars.*` only, `from` = the current value.
4. **KYC (the proposal page).**
   **Worker mode** (a tool named `save_kyc_brief` is available): the KYC is the brief only; the portal renders the 42-section page from it. Do NOT build the HTML page and do NOT call `upload_kyc`. Instead:
   1. Build `kyc.brief.v1` from the audited findings and the record so the portal renders it like the approved 42-section page. **Copy the shape of `kyc.brief.v1.valid.template.json`**, in the same folder as the example named in the prompt (if only `kyc.brief.v1.valid.json` is there, the portal is older: use that example's plain `body` form). The schema next to it is what the portal checks. Write it to `kyc.brief.draft.json`.
      - **Sections:** only the listed ids, each once, no `sources-citation` (the portal builds Sources). Each section has `id`, `title` and `blocks` (not `body`); add `tag` only where the example has one.
      - **Blocks**, in reading order: `heading`, `text` (`style` lead / muted / small), `callout` (`tone: "warn"` for an assumption to check), `list`, `table` (`head` + `rows`), `cards`, `compare` (two boxes: `weak` = today, `strong` = with TechNext), `columns` (one level, e.g. two charts side by side), `chart {slot}`, `diagram {id}`, `must-read` (pre-meeting only), `roi` (tool-profit-estimator only). Match the example's mix per section: tables where it has tables, cards where it has cards, so the page does not turn into paragraphs.
      - **Both languages:** every text is `{en, vi}` (proper Vietnamese, not a word-for-word copy). A plain string only for names, codes and numbers that read the same in both.
      - **Citations sit in the sentence:** rich text is an array of runs, e.g. `[{en, vi}, {cite: "f3", quote: "<exact words from the page>"}, ". "]`. Put the cite right after the claim it supports. `quote` is the excerpt shown on hover (at most 600 characters). Mark TechNext estimates with `{assess: {en, vi}}` and fit levels with `{pill: {en, vi}, tone: green|amber|red|teal|muted}`.
      - **Findings:** ids `f1`, `f2`…; every `cite` names one of them; `url` is the page read.
      - **Charts:** the 18 fixed slots, each placed once with a `chart` block in its section. Line and bar data may hold `null` for a gap.
      - **Diagrams:** `org` (staff-org) as `groups [{title, text}]` (three function cards) or `nodes` + `edges`; `steps` (department-workflows) as `steps [{label, note}]`; BPMN `swimlane` (bpmn-blueprint-uml) drawn with `lanes [{id, name}]`, `nodes [{id, lane, col, kind: start|end|task|gateway, label, note?, focal?}]`, `flows [{from, to, label?, style?: dashed|accent}]` (`col` 0, 1, 2… left to right; `
` breaks a label line); UML `sequence` (bpmn-blueprint-uml) with `actors [{id, label, focal?}]` and `messages [{from, to, label, style?}]`. Each also has `id`, `section`, `type`, `title`, and is placed once with a `diagram` block.
      - **Never** a price, amount, rate or currency figure (the quotation table has no money column; the ROI tool's money fields stay empty: only `roi.defaults` days, percentages and hours), no phone, email or contact link, not even inside a `quote`, no raw HTML. Titles at most 120 characters, each section's blocks at most 60 KB, the whole brief at most 1 MB.
   2. Call `save_kyc_brief {path: "kyc.brief.draft.json", command_id: P + kyc, lead_version: V}`. It checks the brief, then saves it on the portal.
   3. Read the reply:
      - `already saved` (also on a resumed run, replayed or `409 command_reused`): the step is done, go on.
      - Errors (its own check or the portal's 400 `errors[].field`): fix exactly those fields and call it again with the next id (`P` + `kyc-2`, then `P` + `kyc-3`). Only these count: at most 3.
      - `lead changed` (409 `ahead_of_record` / `conflict`): `get_lead`, use the new `record.version` as `lead_version`, call again with the same `command_id`.
      - `temporary portal error`: stop the run here. Do NOT call `fail_job` or `complete_job`; the worker keeps the job claimed and resumes it.
   4. Still rejected after 3 counted calls: add the error fields (without values) to the open questions, save that note, then `fail_job {id, error: "kyc brief rejected: <first field>"}` instead of `complete_job`.
   **Otherwise** (the portal button path, unchanged):
   Build it with the `technext-sales-proposal` writing/assembly/validation phases from the record and save it to a local file. **Never paste the page into a tool call** (it is hundreds of KB; the call gets cut off and the page arrives broken or not at all). Upload it in two steps:
   1. `upload_kyc {slug, command_id, lead_version: V, producer}` **without `html`** → `{upload_url, expires_at, how}` (the link works for 15 minutes).
   2. Run the `how` command with your file, e.g. `curl -sS -X PUT -H 'Content-Type: text/html; charset=utf-8' --data-binary @kyc.html '<upload_url>'`. The answer is the same JSON as a direct upload (`{ok, version, ...}`, or 400 `contact_not_allowed` + `where`, 413 `too_large`). Fix and re-run with the same link; if it expired (401 `upload_link_expired`), call step 1 again with the same `command_id`. Report the stored `version`.
   The HTML must be ONE self-contained file (≤ 4 MB): inline CSS and JS only (no CDN, no external script or stylesheet), images and fonts only as `data:` URIs, no fetch/XHR/form posts, every link `target="_blank" rel="noopener"`, no service worker or web manifest, and **no customer phone number or email**. Its **Quotation section names the modules only — never a price, total, rate or currency**; the portal prices the quote.
5. **Quote draft (optional).** `save_output {slug, kind: "quote", body: {command_id, body: {modules: [{module, reason}], missing?: [keys], label}, inputs: {lead: V, matrix}}}`: no price fields of any kind. Fix any `warnings[]` (unknown module names) and save again with a new `command_id`.
6. `complete_job {id}` (worker mode: only after `save_kyc_brief` saved the brief).

### ingest_notes (notes added on a card)
The job points at a portal note (`get_note {slug, id}` returns its text; contacts were already stripped by the portal, but treat it as if they were not). **Raw notes are never sent anywhere else or stored outside that note**: not in a fact, an output, a job, a prompt to another tool, or a kept file.
0. **A run's own question list is not a meeting note.** When the note was added by an AI run (`via: "agent"`) and its label starts with `Open questions`, extract nothing: `complete_job` and stop.
1. `stripContacts(text)` from `KIT/lib/lead/notes.mjs` (`node -e` or a small script) BEFORE any extraction; work only on the stripped text.
2. Extract facts: `confirmed`, `source.kind` `call` or `meeting`, only FACT_KEYS; use `supersedes` when replacing an earlier fact of the same key.
3. `checkExtractedFacts(facts, {noteId, date, record, matrixModules})` from `KIT/lib/lead/notes.mjs` BEFORE `add_facts`: every confirmed fact cites the note id as `source.ref` (the portal refuses confirmed facts from a token that cite anything else, and rejects the whole batch). Fix the facts on errors; never bypass it.
4. `add_facts {slug, command_id, facts}`, then `complete_job`. The portal recomputes `stale`; regenerate jobs follow.

### regenerate (stale outputs only)
Regenerate exactly the kinds listed in `get_lead`'s `stale`, nothing else (staleness comes from `staleOutputs`: an older `inputs.lead` alone is not stale).
- proposal: update, do not rebuild — `technext-meeting-to-proposal` with the new facts and the `research` output; same artifact link.
- journey: rerun the kit. Before saving any regenerated follow-up, read the lead's followup-state (`GET /api/v1/followup-state/<slug>`) and pass old drafts, new drafts and that state through `mergeFollowups` (`lib/followups.mjs`): sent drafts stay byte-for-byte (the saved sent text), changed unsent ones are labelled "Updated". Never rewrite a sent draft.
- quote: rerun the module suggestion.
Then write each with a new `command_id` and the new `V`: journey via `patch_journey` (only the changed `kit.*`/`vars.*` paths), proposal via `upload_kyc` without html + curl to the upload link (step 4 of generate_all), quote via `save_output`.

## How sales-journey reads a lead (draft, for its owner to adopt)
Replace `research.md` and the local `lead.json` profile with `get_lead {slug}` (or `GET /api/v1/leads/<slug>` with a `read` token): use `profile` for `{industry, size, location, regulatory, risks}` and `record.version` as `inputs.lead`. The sales-entered fields (`current_system`, `users`, `departments`, …) become facts through `add_facts` instead of living only in the page.
