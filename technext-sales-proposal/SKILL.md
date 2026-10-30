---
name: technext-sales-proposal
description: Turn a prospective TechNext client (a company name, website, or short brief) into one comprehensive, bilingual (VI/EN toggle) HTML sales proposal website (all CSS/JS/charts inline, no CDN — opens correctly via file:// with no network) covering all three TechNext service lines — Odoo ERP implementation, AI Solutions, and Social Media Marketing — deep web/social research, a fixed sidebar covering Due Diligence, Strategic Analysis (competitors/market), Operations, a Recommendations section, and a Tools & Documents section (AI Build Playbook, Profit Estimator, Quotation, Meeting Minutes, Discovery Questions, etc). Use when asked to research a client and build a sales proposal / due-diligence site, "làm sales proposal", "nghiên cứu khách hàng làm đề xuất", or when the request matches the client-research-to-proposal workflow (spin up agents, research a company, produce a growth plan with a big sidebar).
---

# Sales proposal skill — client research → TechNext sales proposal site (Odoo ERP · AI · Social Media)

**This file is the orchestrator's map, not the full instructions.** Each phase below
now lives in its own skill or subagent file — read the linked file when you actually
run that phase, don't try to hold the whole pipeline in this one file. This split
happened because the file had grown past 800 lines; each piece is now independently
readable, testable, and editable.

## What this is for

TechNext sells three service lines: **Odoo ERP implementation, AI Solutions, and
Social Media Marketing** — not just Odoo. Before pitching a prospective client, the
salesperson researches them thoroughly and produces one big HTML "site" that doubles as a
due-diligence report and a sales proposal: who the client is, their market and
competitors, and a concrete plan across all three TechNext service lines for them.

**Every proposal always pitches all three service lines**, grounded in this specific
client's own research, never a generic three-service pitch copy-pasted across clients.
Don't ask the user which service(s) to include — that decision was already made.

**Output**: one `.html` file, `<client-slug>-proposal.html`, with a fixed ~40-item
sidebar (client-side JS nav, no page reloads), a VI/EN language toggle, and a
light/dark theme toggle. Its CSS and JS (including Chart.js, embedded inline — no
CDN) are fully inside that one file, so it opens correctly via `file://` with no
network needed for the page's own content or its 18 charts. It is **not** fully
standalone, though: the 4 PWA companion files (`manifest.webmanifest`, `sw.js`,
`icon-192.png`, `icon-512.png`) are separate files needed only if the Install-as-app
feature matters — the page itself renders and every chart still works with just the
single `.html` file if those 4 aren't deployed alongside it (see `assets/reference-files.md`).

**Every factual claim must be verifiable, not just plausible-sounding.** Any claim
from a real source gets a hover-card citation; any TechNext inference/estimate gets an
`.assess` tag. Never invent a number, quote, or named person with a fake-looking
citation. Full rules: `assets/research-rules.md` in this skill's folder.

## Reference map — read the linked file before doing that phase's work

| Phase | What it does | Read this |
|---|---|---|
| 0 — Intake | Get client identifier, disambiguate, ask about checkpoint resume | Below on this page |
| 0.5 — Company verification | Confirm the exact legal entity via GLEIF (free, no key) before research starts | Skill: `company-verifier` |
| 0.6 — Officers lookup | Resolve directors/officers/founders from official public registries (Companies House/OpenCorporates/SEC EDGAR + Wikidata + team page) before research starts — writes `officers.json`, replaces Apollo | Skill: `officers-lookup` |
| 0.7 — Web/OSINT scan | Scan the client's own site + socials, categorize links (social/reviews/press), light tech scan — writes `web-scan.json`, the starting point every Phase 1 subagent reads first | Skill: `web-osint-scanner` |
| 0.75 — Social browser scan | Read the client's and ≤3 competitors' Facebook, LinkedIn, Instagram, Google Maps, YouTube, X and TikTok through the user's own logged-in Chrome (Claude in Chrome MCP), starting from the links on the client's website; keep only posts/reviews relevant to the proposal; save text snapshots to `captures/social/` — writes `social-scan.json`. Asks the user to log in themselves; read-only; skipped with a note when no browser tool exists | Skill: `social-browser-scan` |
| Checkpointing | Decide which phase/group/section actually needs to run; resume logic; timeline/session_id bookkeeping for cost reporting; post-Phase-4 cleanup | Skill: `checkpoint-manager` |
| 0.9 — Competitor research | 1 worker per identified competitor (hard-budgeted: ≤8 fetches, ≤8 min each), dispatched in parallel — the single shared source both Group A's `competitor-deep-dive` and Group C's `top3-competitor-deep-dive` read from. Immediately followed by `source-auditor`'s `bind_check.py --facts` gate on the resulting JSON, **before** Phase 1 is dispatched — a bad excerpt here would otherwise land in two sections at once | Agent named `competitor-research-worker`, dispatched once per competitor in `web-scan.json`'s new `competitors` array (written by `web-osint-scanner`'s own competitor-identification step) |
| 1 — Research fan-out | 4 parallel subagents, each researches + writes its own section group + charts, reading `captures/*.md`/`officers.json`/`competitor-research/*.json` first (not live web fetches for anything already captured) | Agents named `research-due-diligence-agent`, `research-ops-tech-agent`, `research-delivery-growth-agent`, `tools-documents-agent` — find each one wherever this agent/tool keeps its own agent definitions (Claude Code: `~/.claude/agents/<name>.md`; a different tool may have no such file at all — see note below) — shared markup contract in `assets/section-shell.md` (not the full template — see note below), citation rules in `assets/research-rules.md` |
| Charts & diagrams manifest | Exact canvas ids/diagram slots, ownership; diagrams drawn with the bundled `diagram-design` skill (installed together with this skill) | `assets/charts-and-diagrams.md` + Skill: `diagram-design` |
| Template/validator reference | The shell you must build from, the per-client palette rule, what `validate-proposal.py` checks | `assets/reference-files.md` |
| 2.5 — Source audit (hard gate) — **runs before Phase 2** | Confirm every Phase 1 citation's excerpt is really on its source page (`bind_check.py`) and write `audited-findings.json` — a blocking gate, not an FYI | Skill: `source-auditor` |
| 2 — Front matter — **runs after 2.5** | Overview/Executive Summary/Recommendations/3 Proposed Solutions, written directly (no agent) from the digests + `audited-findings.json`; its own new citations are then bind-checked with the same gate before 2.6 | Skill: `front-matter-writer` |
| 2.6 — Chart data | Build the final `chart-manifest.json` from audited findings — only runs after `source-auditor` passes with an empty `blocking_issues` array | Skill: `chart-data-analyst` |
| 3 — Assembly | Extract sections from Phase 1 previews, drop into the template in fixed order | Skill: `assembler` |
| 4a — Mechanical validation | Run `validate-proposal.py`'s 13 hard checks (incl. no-CDN gate) | Skill: `mechanical-validator` |
| 4b — Judgment review | Content/citation spot-check, devil's-advocate pass, then a per-task `ccusage` cost report | Skill: `judgment-reviewer` |
| 5 — Library (automatic) | After Phase 4 passes: publish the proposal as a private claude.ai artifact and add or update its card in the TechNext Proposal Library with the sibling skill `proposal-library-publish` (the card is sent over HTTPS to the library: no git, no GitHub account, no key) | "Phase 5" below |

**Execution order after Phase 1:** 2.5 source audit → 2 front matter (reads
`audited-findings.json`) → re-run `bind_check.py` on the front matter's own findings
(same gate, merged into `audited-findings.json`) → 2.6 chart data → 3 assembly → 4.
The phase numbers are labels kept for continuity; this order is what to run.

**Note on Phase 1's input cost.** Group agents no longer read the full
`proposal-template.html` (~250KB/~65-70k tokens each, ×4 groups = ~260k tokens before
any actual research happened, for output that's just a handful of `<section>`
fragments) — they read `assets/section-shell.md` (~5KB) instead, and return raw
fragments rather than a full-page copy. `assets/section-shell.md` also documents the `.g5-flow` five-step flow and the "What's updated" change log (`#changelog-data`) that the template now carries, so do not hand-roll either. `checkpoint-manager` stitches those fragments
into a real previewable `<client-slug>-p1-group{A,B,C,D}.html` mechanically (a
find/replace against the template, not something needing an agent's own context) —
see `checkpoint-manager`'s "Stitch Phase 1 fragments" section.

**Portability note on the 4 research subagents.** Their definition files use `tools:`
and `model:` frontmatter, which is Claude Code's own agent-definition convention —
those two fields don't exist under Codex/Gemini CLI/other agents, which each have
their own (different) mechanism for defining a sub-agent's toolset/model. Under a
different agent/tool, don't expect that file format to exist or work as-is: read the
*body* of each research subagent's instructions (what to research, which sections/
charts it owns, what to return) as the portable part, and re-express the
tools/model choice using whatever that agent's own sub-agent mechanism is — or, if
that tool has no sub-agent concept at all, run all 4 groups' research directly in
sequence instead of in parallel, clearly noting in the checkpoint that this run
didn't fan out.

## Phase 0 — Intake

**Paths.** This skill can live in `~/.claude/skills/`, in a project's `.claude/skills/`, or
in another agent's skills folder. Never assume `~/.claude/skills`: resolve this skill's own
folder (the folder holding this `SKILL.md`) once, and pass that absolute path to every
subagent as `<sales-proposal skill folder>`; sibling sub-skills are in its parent folder.

### Setup check — the 5 research agents (runs first, silently when all is fine)

Phase 1 dispatches 5 agents by name: `research-due-diligence-agent`,
`research-ops-tech-agent`, `research-delivery-growth-agent`, `tools-documents-agent`,
`competitor-research-worker`. Some install routes (e.g. SKILL-LIB via technext-mcp-skill-lib)
copy only skill folders, leaving the agent files in this skill's own `agents/` folder
where the host does not look. Check and self-heal before anything else:

1. **Claude Code:** list `~/.claude/agents/`. For each of the 5 files that is missing,
   copy it from `<this skill's folder>/agents/<name>.md` into `~/.claude/agents/`
   (create the folder if needed; never overwrite an existing file there — if one exists
   but differs, tell the user and leave it). Report in one line, e.g.
   *"Đã cài thêm 5 agent nghiên cứu vào ~/.claude/agents/ — lần sau khởi động lại Claude Code để dùng bản chính thức."*
2. **This run still fans out.** A host only registers new agent files on restart, so
   for any agent that was missing at the start of this run, dispatch a
   **`general-purpose`** subagent instead and put the full body of
   `<this skill's folder>/agents/<name>.md` (below its frontmatter) at the top of that
   subagent's prompt, followed by the run-specific inputs. Same parallelism, same
   outputs — never fall back to doing all 4 groups yourself in this session just
   because the named agents are not registered yet.
3. **Other hosts** (Codex, Gemini CLI…): skip step 1; use step 2 with whatever
   sub-agent mechanism the host has, or run the groups in sequence and say so in the
   checkpoint.
4. **Sub-skills.** The sub-skills this skill installs with are listed in
   **`dependencies.json`** next to this file (`requires` and `optional`; today 14
   required, none optional). Look in the skills directory that holds this skill
   (its parent folder) for each of them:
   - **Required:** the `requires` list. Two of them are not steps of the pipeline but
     always come along: `diagram-design` (MANDATORY: all 4 diagram blocks must be drawn with it as inline
     SVG; plain `.tl` markup is no longer accepted and the validator fails it) and
     `technext-meeting-to-proposal` (sends a meeting recording to TechNext's Minutes
     Studio and writes the minutes into a finished proposal; the pipeline never calls
     it).
   - **Optional:** the `optional` list (empty today).

   `technext-mcp-skill-lib` reads that same file, so a skill installed with it already brings
   these along; this check is for installs that did not (a plain folder copy, an older
   `technext-mcp-skill-lib`).

   If any is missing, tell the user in **one** message which ones, and offer to install
   them — never install silently:
   > *"Thiếu skill con: <danh sách>. Mình cài giúp từ SKILL-LIB (aidev3-web/SKILL-LIB)
   > nhé? (có / không)"* — add *"diagram-design là BẮT BUỘC: thiếu thì không vẽ được 4 sơ đồ và
   > proposal không qua kiểm tra; technext-meeting-to-proposal thiếu thì chỉ không gửi được ghi âm cuộc họp"* when only those are missing.
   Do not start Phase 1 until `diagram-design` is installed.

   On **yes**: if the `technext-mcp-skill-lib` tools are available, run `pull_skill` then
   `deploy_skill` for each missing one from `aidev3-web/SKILL-LIB`; otherwise give the
   user the GitHub installer command (`install.ps1` / `install.sh`). Remind them to
   restart the host so the new skills are picked up. On **no** (or install fails):
   continue — a missing **optional** skill just uses the fallback, but a missing
   `diagram-design` blocks the run (the 4 diagrams cannot be drawn without it); any other missing **required** one means doing that step's work directly from its description in the
   reference map above, and saying so in the checkpoint.

Get the client identifier: company name, plus any URL/socials the user already gives.
If all you have is a bare name, do one round of web search to find their site/socials
yourself rather than stopping to ask — only ask the user directly if the name is too
ambiguous to search confidently. Confirm the client name you'll use in the page
`<title>`: `"<Client> · Strategic Due Diligence & Growth Blueprint (Odoo ERP · AI · Social Media) · Technext"`.

### Confirm what the user gave you — one short message, before any research

Send **one** message (never a series of back-and-forth questions) that restates what the
user provided and asks only what is still unknown. Skip any question the user already
answered in their request. Keep it to **at most 4 numbered questions**:

1. **Contact status** — *"Bạn đã gặp/họp với khách hàng này chưa? (chưa liên hệ / đã gọi
   điện hoặc họp online / đã gặp trực tiếp) — nếu rồi thì ngày nào, gặp ai (vai trò)?"*
2. **The problems they raised** — only if the user named any pain/problem. Restate each one
   in one line and ask to confirm or sharpen it: who raised it (the client or TechNext's own
   guess), and any detail or number known (e.g. *"Vấn đề 1: hóa đơn kế toán bị chậm — đây là
   khách tự nói hay mình đoán? Chậm khoảng bao nhiêu ngày, ở khâu nào?"*). Do not invent new
   problems here; just clarify the ones given.
3. **Meeting content** — *"Bạn có ghi chú, nội dung cuộc họp hoặc transcript không? Nếu có,
   dán vào đây."*
4. **Colour theme** — *"Proposal mở bằng màu nào? Chọn 1 trong 8 màu (Xanh ngọc, Cam kem,
   Xanh TechNext, Tím, Xanh lá, Đỏ rượu vang, Xám than, Vàng hổ phách) hoặc gửi mã màu riêng
   (ví dụ #e8734a)."*

End the message with *"Trả lời ngắn cũng được; câu nào chưa biết cứ bỏ qua."* If the user
skips a question, use the default below and move on — never ask the same thing twice.

**How the answers change the proposal:**

| Answer | Effect |
|---|---|
| Not contacted yet | Every pain is `Assumed — to verify in the first meeting`, never `Confirmed`. `pre-meeting` is written as a first-meeting brief; `tool-discovery-questions` leads with questions that validate the assumed pains. |
| Called / met, no notes | Pains the user says the **client** raised are `Reported by TechNext sales, <date>` (between Confirmed and web-sourced). Pains that were TechNext's guess stay `Assumed`. |
| Notes / transcript pasted | Facts from it are `Confirmed — <meeting type>, <date>`, the highest trust grade, above anything web-researched; quote them in `meeting-minutes`. The `follow-ups` section (after `meeting-minutes`, optional for older proposals) holds the 4 drafted follow-up messages; its dates come from the meeting date. |
| Problem clarified with detail/number | Use the user's detail verbatim as the starting point for that pain's charts/ROI defaults, labelled with its source. |
| Colour | Set `data-palette-default="<key>"` on `<html>` (`teal`, `orange`, `blue`, `purple`, `green`, `wine`, `charcoal`, `amber`); for a custom hex keep `teal` and add `data-palette-custom="#rrggbb"`. No answer → `teal`. Viewers can still change it with the 🎨 button. |

Record the answers in `<client-slug>-intake.json` (`contact_status`, `contact_date`,
`contact_person_role`, `pains[]` with `{text, raised_by, detail}`, `has_notes`, `palette`)
so every later phase reads the same facts instead of re-asking.

Then run the `company-verifier` skill (GLEIF check), then the `checkpoint-manager`
skill (decide what actually needs to run this invocation — full pipeline, or resume
one phase/group/section) before dispatching anything else.

**Research depth.** Always a full "Standard" pass — there is no "Quick" mode. If a
client genuinely has very little public footprint, say so plainly in the relevant
sections rather than switching to a thinner research pass.

**Scope & ethics boundary.** Research stays limited to information a company and its
leadership have made public in a business capacity. Never pursue private/personal
information about individuals unrelated to their business role, and never use
non-public collection methods. If a request pushes past this line, decline that part
and say why.

## Delivery

Save as `<client-slug>-proposal.html` plus its companion `<client-slug>-findings.json`
and hand both to the user directly, along with the 4 PWA companion files
(`manifest.webmanifest`, `sw.js`, `icon-192.png`, `icon-512.png`) copied unchanged from
`assets/` — mention that the Install button only works if all four are deployed
alongside the HTML at a real static path, not when the HTML is opened alone via
`file://` (see `assets/reference-files.md`). Note in your summary which research areas
came back thin or unverifiable, and include `judgment-reviewer`'s `ccusage` cost
report for this run.

## Phase 5 — Publish the artifact and add the card to the Proposal Library (automatic)

Runs by itself **after Phase 4 has passed** (both `mechanical-validator` and `judgment-reviewer`). If Phase 4 did not pass, skip
Phase 5 and say so. It is the same step on a first run and on every re-run or update (for example after
`technext-meeting-to-proposal`): the card is keyed by the client slug, so it is updated, never duplicated.

The script, its settings and its own instructions live in the sibling skill `proposal-library-publish` (in the same skills folder as this one); read its `SKILL.md` before running it.

**What it does, in order**
1. **Publish the artifact** (only when the `Artifact` tool exists in this session; under another agent skip to "No artifact tool").
   First make the page's `<title>` a short name, `<Client short name> Proposal` (two to four words, in the file itself, not the long
   template title). Publish `<client-slug>-proposal.html` with `Artifact` (icon `proposal`, one-sentence `description`). On a re-run
   pass the saved address as `url` (checkpoint field `library.artifact_url`) so the link stays the same. It is private by default.
2. **Write the card text** (never the proposal's contact details, prices or CRM fields):
   - `--summary`: one honest sentence, at most 240 characters, from the Executive Summary. If the proposal is unfinished or has open
     items, say so in it (for example "company identity and prices not confirmed yet").
   - `--industry`: a short phrase. `--country`: if the intake has it. `--status`: only when the person said so (new cards default to
     `ready`; after a meeting update ask whether it should become `followup`).
3. **Run the script** (from anywhere):
   `python <proposal-library-publish skill folder>/library_publish.py <proposal folder> --artifact-url <url> --summary "<sentence>" --industry "<phrase>" --by "<the person's name>"`
   After a meeting, also pass `--meeting-date YYYY-MM-DD` (the meeting date) and `--next-followup YYYY-MM-DD` (the planned date of the next follow-up not yet sent, from the proposal's `follow-ups` section; Saturday/Sunday move to Monday). Both are optional, validated, and sent to the library as `meeting_date` / `next_followup`; leave them out when there is no meeting yet.
   **Meeting minutes and follow-up drafts on the card (when the proposal has had a meeting).** If the `meeting-minutes` section is filled and
   the `follow-ups` section has `data-meeting-date` set, build the card's meeting data first and pass it:
   `python <proposal-library-publish skill folder>/library_publish.py extract-meeting <proposal folder> [--confirmed]` writes
   `<proposal folder>/captures/library-meeting.json` (`{minutes, followups}`); then add `--meeting-file <proposal folder>/captures/library-meeting.json`
   to the command above. Where the data comes from: the meeting date, the input table (channel, signer, language, source) and the draft texts
   (WhatsApp, Viber, email subject and body; English text; any draft still containing `[PLACEHOLDER` is skipped, nothing is invented) are read from the
   proposal HTML; the summary, decisions and next steps come from `captures/meeting-<date>/minutes.json` (Minutes Studio), because the minutes prose
   in the HTML is free-form. Pass `--confirmed` only if the person has said they read the minutes and confirm them. The file is validated with
   the library's limits and refused (exit 2, nothing sent) when invalid; `check-meeting <file>` validates alone, `--dry-run` shows the record without sending.
   **Tell the person, in the step where they approve the publish** (in `ask` mode, when you show the record; in `auto` mode, in the line before you
   run it): the library shows these minutes and the drafted messages to **all staff signed in to the library** (internal, password-gated, but not
   limited to the proposal's owner). If they do not want that, run without `--meeting-file`; a card published earlier keeps the minutes it already has.
   It sends the card to the library over HTTPS, to the address in the `library-endpoint.json` of the `proposal-library-publish` skill (made by the library owner and shipped
   with the skill; `PROPOSAL_LIBRARY_URL` or the settings file work too). Nothing to install and no key to enter: no git, no GitHub
   account. With no key the card goes into the library's suggestion box: in the owner's usual setting it appears in the library **at
   once with an Auto-added badge** (no review step); in the queue setting it waits for the owner to accept it. Running Phase 5 again
   refreshes the same card (the checkpoint remembers what was sent, so a re-run keeps the summary, industry and status unless you
   pass new ones). (If the owner shipped an optional team key in the same file, the card is written straight into the library with
   the same badge.) The script records `library: {artifact_url, transport, action, pending}` in
   `<client-slug>-checkpoint.json`.
   Only when a git clone is named (`--repo`, `PROPOSAL_LIBRARY_REPO` or `"repo"` in the settings file) does it use git instead: it edits
   that clone's `registry.json`, rebuilds `site/`, runs the library's Python tests, commits and pushes `main` with the person's own git
   login (add `--trailer "<the Co-Authored-By line from the session's attribution reminder>"` in that case).
   **Meeting links.** Staff can add links (a Google Docs meeting-notes link, quotation docs, other docs) to a client's card in the library. `technext-meeting-to-proposal` (path B, "Links from the library") picks them up: it lists them with `library_publish.py links <slug>` (only the unused ones; `--all` for every link), reads them after the person says yes, updates the proposal, and then marks each folded-in link with `library_publish.py mark-link-used <slug> <id>`. Both commands need the team key and the client's card to exist already (so run this skill first for a new client).
4. **Report** in the person's language: that the card is in the library (marked Auto-added, because nobody has checked it) or, if the
   script said it waits in a queue, that the owner has to accept it first; the artifact link, and these reminders: the artifact is private until they press **Share** and choose TechNext (the tool cannot
   change sharing; say exactly where to click), and what the proposal still has unverified.

**Settings** (`~/.claude/proposal-library.json`, optional): `{"endpoint": "<https address>", "key": "<team key>", "repo": "<clone path>", "mode": "auto" | "ask" | "off", "name": "<who is updating>"}`.
- `auto` (the default when the file is missing): publish as soon as the checks pass, without asking.
- `ask`: the script stops with exit code 3 and prints the record; show it to the person, and only if they say yes run it again with `--yes`.
- `off`: do nothing and say that library publishing is switched off.

**Rules**
- A failure here never fails the proposal run. If the script exits 2 it has pushed nothing: show its one-line reason, keep the
  proposal as delivered, and tell the person to run Phase 5 again once fixed. Typical reasons: `library-endpoint.json` missing, the owner has closed the suggestion box (it answers that it is not taking
  cards without a key), the library is unreachable, a rejected card field, the queue is full; in git mode also no GitHub login that can read `aidev3-web/proposal-library` or uncommitted
  changes in the clone.
- It never forces a push, never touches another repo, never asks the person for a token or password (there is none: at most an optional team key
  in a file shipped with the skill, never printed, never written into a proposal), and never sends the proposal HTML anywhere (only the card text and the section
  list reach the library).
- **No artifact tool** (another agent, or publishing refused): do not invent an address. Say the card was not created, give the
  one command to run once the person has an artifact link, and finish normally.
- The script needs Python 3 (standard library only). Git is needed only in git mode. Node is not needed.

## Clean up after yourself — don't leave a pile of scratch files behind

Every phase/subagent creates intermediate files (group previews, digests, chart
manifests, scratch drafts). Left alone across several runs these accumulate fast and
nobody can tell which ones still matter. Once Phase 4 passes and the file is handed
over, **default to deleting superseded intermediates automatically** — don't wait to
be asked, that's exactly how they pile up. Only skip the delete if the user has
explicitly said they want to keep them for a future incremental re-run.

**Always keep** (the real deliverable + audit trail):
- `<client-slug>-proposal.html` (final output)
- `<client-slug>-findings.json` (citation source list — needed to answer "where did
  this claim come from" later)
- `<client-slug>-checkpoint.json` (resume + audit history)
- `<client-slug>-cost-report.csv`
- `web-scan.json`, `officers.json`, `competitor-research/*.json` (the raw research
  inputs everything else cites back to — cheap to keep, expensive to re-derive)
- `captures/social/*.md` (the only copy of login-walled social pages that browser-observed
  citations bind to - they cannot be re-fetched without the user's login)
- `bind-check-report.json`, `competitor-facts-bind-check.json` (the citation
  bind-check's own audit trail, for both gates)
- `audited-findings.json` (the merged, re-graded findings `chart-data-analyst` and
  `front-matter-writer` actually built from — this is the real audit trail behind
  the final file's citations, `<client-slug>-findings.json` alone doesn't show what
  `source-auditor` corrected)

**Delete once Phase 4 passes** (fully superseded by the final file, keeping them adds
no value):
- `<client-slug>-p1-group{A,B,C,D}.html` (merged into the final file by `assembler`)
- `<client-slug>-p1-digests.json` (only `front-matter-writer` needed this, already consumed)
- `<client-slug>-p2-frontmatter.html` (merged into the final file)
- `<client-slug>-findings-group{A,B,C,D}.json` (already merged into
  `audited-findings.json`/`<client-slug>-findings.json` by `source-auditor` — the
  per-group files themselves are superseded once merged)
- `chart-manifest.json` (validated already, not needed once the final file has the charts)
- **`captures/*.md`** - top level only, never `captures/social/` (the full page-text cache from `web-osint-scanner`'s Phase 0.8
  pre-fetch — this is a fetch cache, not a citable record; it's the largest
  intermediate by far (~39 full pages of text) and keeping it around across runs is
  exactly the pileup this cleanup rule exists to prevent). Keep `captures/manifest.json`
  itself deleted too — it's meaningless without the `.md` files it points to. If the
  user explicitly wants a fast incremental re-run later (skip re-fetching), that's the
  one case to ask before deleting this specific directory, same as any other
  keep-for-resume exception.
- any one-off scratch/preview file a subagent wrote outside the session's own
  scratchpad directory (e.g. a `*-preview.html` used mid-touch-up) — these should have
  been written to the scratchpad in the first place; if one turns up in the project
  directory instead, delete it as part of this same cleanup rather than leaving it.

Every subagent (Group A–D, section-level touch-ups) should be told explicitly, as part
of its dispatch instructions, to write its own scratch/preview files only under the
session's scratchpad directory — never the project directory — so this cleanup step
never has to go hunting for stragglers.

## Judgment calls

- **Client has very little public presence** (small/local business) — say so plainly
  rather than inventing specifics; keep every framework grounded in what's actually
  knowable, note assumptions explicitly.
- **User wants fewer sections for a quick draft** — you can trim scope if they
  explicitly ask, but the default always produces the full sidebar from
  `assets/menu-structure.md`.
- **Odoo version other than 19 mentioned** — ask; the fixed instruction set here
  assumes Odoo 19, but a client conversation may specify differently.
