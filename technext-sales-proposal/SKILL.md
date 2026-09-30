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

**Execution order after Phase 1:** 2.5 source audit → 2 front matter (reads
`audited-findings.json`) → re-run `bind_check.py` on the front matter's own findings
(same gate, merged into `audited-findings.json`) → 2.6 chart data → 3 assembly → 4.
The phase numbers are labels kept for continuity; this order is what to run.

**Note on Phase 1's input cost.** Group agents no longer read the full
`proposal-template.html` (~250KB/~65-70k tokens each, ×4 groups = ~260k tokens before
any actual research happened, for output that's just a handful of `<section>`
fragments) — they read `assets/section-shell.md` (~5KB) instead, and return raw
fragments rather than a full-page copy. `checkpoint-manager` stitches those fragments
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
`competitor-research-worker`. Some install routes (e.g. SKILL-LIB via mcp-skill-lib)
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
4. **Sub-skills.** The sub-skills the pipeline calls by name are listed in
   **`dependencies.json`** next to this file (`requires` and `optional`; today 11
   required plus `diagram-design`). Look in the skills directory that holds this skill
   (its parent folder) for each of them:
   - **Required:** the `requires` list.
   - **Optional:** the `optional` list — `diagram-design` gives nicer SVG diagrams;
     without it the 4 diagram blocks fall back to plain HTML `.tl` markup (still
     passes the validator).

   `mcp-skill-lib` reads that same file, so a skill installed with it already brings
   these along; this check is for installs that did not (a plain folder copy, an older
   `mcp-skill-lib`).

   If any is missing, tell the user in **one** message which ones, and offer to install
   them — never install silently:
   > *"Thiếu skill con: <danh sách>. Mình cài giúp từ SKILL-LIB (aidev3-web/SKILL-LIB)
   > nhé? (có / không)"* — add *"diagram-design không bắt buộc, thiếu thì sơ đồ vẽ bằng
   > HTML thường"* when only that one is missing.

   On **yes**: if the `mcp-skill-lib` tools are available, run `pull_skill` then
   `deploy_skill` for each missing one from `aidev3-web/SKILL-LIB`; otherwise give the
   user the GitHub installer command (`install.ps1` / `install.sh`). Remind them to
   restart the host so the new skills are picked up. On **no** (or install fails):
   continue — a missing **optional** skill just uses the fallback; a missing
   **required** one means doing that step's work directly from its description in the
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
| Notes / transcript pasted | Facts from it are `Confirmed — <meeting type>, <date>`, the highest trust grade, above anything web-researched; quote them in `meeting-minutes`. |
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
