---
name: checkpoint-manager
description: Decides which phase(s)/group(s)/section(s) of the technext-sales-proposal pipeline actually need to run, and reads/writes the client's checkpoint file so a run can resume from where it left off instead of always rebuilding from scratch. Called by the technext-sales-proposal orchestrator skill at the start of every invocation, and again after each phase completes.
---

# Checkpoint manager — run one phase at a time instead of the whole pipeline

Running the full Phase 1→4 pipeline in one go is the default, but it's also the
slowest/most expensive path — if the user only wants to re-run Group B after a bad
first pass, or just wants Phase 4's validator re-checked after a manual edit, they
shouldn't be forced through everything again.

## What to do when called

1. **Read `<client-slug>-checkpoint.json`** if it exists — a small file tracking
   what's done:
   ```json
   { "phase1_groupA": "done", "phase1_groupB": "done", "phase1_groupC": "pending", "phase1_groupD": "pending", "phase2": "pending", "phase3": "pending", "phase4": "pending" }
   ```
   If it doesn't exist yet, this is a fresh run — everything is `"pending"`.
2. **Ask the orchestrator's caller (via the orchestrator), right after the client is
   confirmed**: *"Chạy toàn bộ pipeline luôn, hay chỉ chạy 1 phase cụ thể?"* Report
   back which phases/groups are already `"done"` vs. `"pending"` so the orchestrator
   can decide (or ask the user) what to actually dispatch this run.
3. **After each phase/group completes**, update the checkpoint file and report what
   just ran — e.g. *"Đã chạy xong Phase 1 Group A + B (2 agent). Group C, D, Phase
   2-4 vẫn đang pending."* This tracks **how many `Agent` calls were made**, a rough
   proxy for cost — not an exact token/dollar count.

## Also log a timeline — and one rule that makes cost reporting work for ANY agent

This pipeline may run under Claude Code, or under a different coding agent entirely
(Codex, Gemini CLI, ...) — this skill's own instructions don't change based on that,
but the cost-reporting mechanism only works if one rule is followed:

1. **A dispatched task — a Phase 1 group, a section-level touch-up, anything run as
   its own `Agent` call or its own separate agent invocation — must run in its own
   isolated session/process.** Then "this task's cost" is exactly "this session's
   cost": one task = one session = one row, no guessing.
2. **A task that genuinely runs inline in the orchestrator's own session (no separate
   `Agent` call) must still record a `session_id` — the orchestrator's own — and set
   `"shared_session": true`.** Do not write `null` there. Several inline tasks may
   carry the same id; the cost script then reports that session **once**, labelled
   `shared-session: <task> + <task>`, so the run's total stays correct. Writing `null`
   instead leaves those phases with no cost row at all and the run's total silently
   under-reports.

Both cases work because `ccusage` already reads 18+ agents' local logs, tagging each
session with which agent produced it, so no timestamp inference is ever needed
regardless of which agent ran the task.

Record a `timeline` array in `<client-slug>-checkpoint.json` alongside the phase
statuses:

```json
"timeline": [
  { "task": "phase0_verification", "started": "2026-09-24T02:40:00Z", "ended": "2026-09-24T02:48:00Z", "session_id": "11111111-2222-4333-8444-555555555555", "agent": "claude" },
  { "task": "phase1_groupA", "started": "2026-09-24T02:49:00Z", "ended": "2026-09-24T03:15:00Z", "session_id": "a5249cf5-b07d-8064-5xxx", "agent": "claude" },
  { "task": "phase2_5_source_audit", "started": "2026-09-24T03:16:00Z", "ended": "2026-09-24T03:30:00Z", "session_id": "11111111-2222-4333-8444-555555555555", "agent": "claude", "shared_session": true, "note": "ran inline in the orchestrator session — same session_id as phase0_verification above, so the cost script reports that session once for both" }
]
```

**`session_id` is mandatory for every entry** — the exact session/conversation id
that task's own agent reports for itself (for a Claude Code `Agent` call, this is the
id the Task tool's own run is recorded under; ask the dispatching mechanism for its
own session id rather than guessing it from a file path). **`agent`** names which
coding agent ran it (`"claude"`, `"codex"`, etc.) — optional but recommended, since it
disambiguates in the rare case two different agents ever produced the same-looking id.
**`session_id` is mandatory for every entry, including inline ones** — an inline task
records the *orchestrator's* id (see rule 2 above), never `null`. A task with no
`session_id` recorded cannot be cost-reported at all: the script says so explicitly
rather than guessing, so don't skip this field to save a step.

## Report that task's cost immediately, not just at the end

Right after writing a timeline entry's `ended`/`session_id`, run:
```
python <path-to-judgment-reviewer-skill>/assets/ccusage_to_csv.py --task "<task-name>" <client-slug>-checkpoint.json
```
`<path-to-judgment-reviewer-skill>` is wherever the `judgment-reviewer` skill is
actually installed on this machine/agent (when the skills ship together this is
`<skill-root>/skills/judgment-reviewer`, but skill install locations differ by
agent/tool — resolve it from however this run located `judgment-reviewer` in the
first place, don't hardcode a Claude-specific path). Show the user the result along with your normal "Đã chạy xong Phase X" message — e.g.
*"Đã chạy xong Phase 1 Group A. Chi phí: $0.44 (model nhỏ), chạy mất 25m."* This is the
whole point of logging the timeline: knowing exactly what each stage cost **as it
finishes**, not only from one lump report at the very end of the pipeline. If the
command prints a "⚠ CẢNH BÁO" line about a non-Claude model showing up inside a
`"agent": "claude"` session, surface that warning to the user too — it means an
internal tool (e.g. an MCP call) routed through a different provider mid-session,
which needs a manual look before trusting the total (see `judgment-reviewer` for the
full explanation).

## Stitch Phase 1 fragments — mechanical, not the group agent's job

Each Phase 1 group agent (A/B/C/D) now returns **raw `<section>` fragments only**
(per `assets/section-shell.md`) — it never reads or copies the full
`proposal-template.html` itself (that was ~65-70k tokens read for nothing per group,
since the checkpoint only ever needed the fragments). Run the actual script for
this, don't do it by hand or ask an agent to hold the whole template in context:
```
python <path-to-technext-sales-proposal-skill>/assets/stitch_group.py \
  <path-to-technext-sales-proposal-skill>/assets/proposal-template.html \
  <group's-returned-fragments.html> \
  <client-slug>-p1-groupA.html
```
It finds each fragment's `section id="..."` and replaces that exact section in a
fresh template copy, failing loudly (exit 1) if a fragment's id doesn't exist in the
template — a real bug (typo, or a section this group doesn't actually own), not
something to silently skip.

## Rules for what counts as a valid checkpoint file

- **Every intermediate file must be a real, directly-openable HTML page — never a
  bare `<section>` fragment saved on its own.** A fragment can't be previewed in a
  browser, which is exactly when you most want to look at it. So
  `<client-slug>-p1-groupA.html` (and B/C/D) must be a **full copy of
  `<skill-root>/assets/proposal-template.html`** (see
  "Stitch Phase 1 fragments" above for how — this is `checkpoint-manager`'s own step,
  not the group agent's) with that group's real sections filled in and every other
  section left as its original `placeholder-note` — openable and previewable on its
  own, exactly like the final deliverable, just with most sections still empty.
- A shared `<client-slug>-p1-digests.json` holds each group's 3–5-point digest (kept
  separate since the `front-matter-writer` skill only needs the digests, not full
  HTML).
- **Phase 2** (`front-matter-writer` skill) saves its own preview the same way — a
  full template copy with just the front-matter sections filled in — to
  `<client-slug>-p2-frontmatter.html`.
- **Phase 3 (`assembler` skill)** requires all of Phase 1 (4 groups) + Phase 2 to be
  `"done"` — if any are still `"pending"`, say so and stop rather than assembling
  with gaps.
- **Phase 4 (`mechanical-validator` + `judgment-reviewer` skills)** only needs Phase
  3's `<client-slug>-proposal.html` to exist — it can be re-run alone any time (e.g.
  right after a manual fix) without touching Phases 1–3.

## Clean up superseded intermediate files — after Phase 4 passes

Once `judgment-reviewer` reports the proposal passed and is ready to hand over, delete
the intermediate files Phase 3/4 already fully consumed — don't leave them to pile up
across runs. See `<skill-root>/SKILL.md`'s "Clean up after
yourself" section for the exact keep/delete list. In short: delete
`<client-slug>-p1-group{A,B,C,D}.html`, `<client-slug>-findings-group{A,B,C,D}.json`,
`<client-slug>-p1-digests.json`, `<client-slug>-p2-frontmatter.html`,
`chart-manifest.json`, and — the largest one — `captures/*.md` + `captures/manifest.json`
(the Phase 0.8 fetch cache; keeping ~39 full pages of text around after the run is
exactly the pileup this rule exists to prevent). Keep the final `-proposal.html`,
`-findings.json`, `audited-findings.json`, `-checkpoint.json`, `-cost-report.csv`,
`web-scan.json`, `officers.json`, `competitor-research/*.json`, `bind-check-report.json`,
and `competitor-facts-bind-check.json`. Do this automatically by default — only skip it
if the user has explicitly said they want the intermediates kept for a future
incremental re-run.

Also check for stray scratch/preview files a subagent left in the **project
directory** instead of its session scratchpad (this happens when a dispatch
instruction forgot to say "write scratch files to the scratchpad only") — delete those
too as part of the same pass, and note in your report to the orchestrator which
subagent's dispatch instructions should be fixed so it doesn't happen again next run.

## Section-level touch-ups — smaller than a whole group

A group is 6–14 sidebar sections bundled into one `Agent` call — if the user only
wants one specific section redone (e.g. "chỉ nghiên cứu lại phần Digital & Web
Presence thôi" — that's one section inside Group A, not all of Group A), don't
re-run the whole group:
1. Identify which subagent owns that section (match the section name against
   `<skill-root>/assets/menu-structure.md`, or check
   which of the 4 `<skill-root>/agents/*.md` subagent definitions lists it).
2. Have the orchestrator spawn a single, narrowly-scoped `Agent` call for **just that
   one section** (still give it the real template contents + `research-rules.md` —
   a smaller scope doesn't mean a lower quality bar).
3. Open the group's existing `<client-slug>-p1-group<X>.html`, find that section's
   `<section id="...">...</section>` block, and replace only that block in place —
   every other section stays untouched, byte for byte.
4. The group's checkpoint status stays whatever it already was (this is an in-place
   patch, not a new phase) — no new checkpoint field needed.

If the user doesn't know which group owns a section, they don't need to — just name
the section (as it appears in the sidebar) and resolve the mapping yourself.
