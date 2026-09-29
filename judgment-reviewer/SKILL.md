---
name: judgment-reviewer
description: Judgment-based review pass over an assembled sales-proposal HTML — citation-content spot-check, devil's-advocate review of the architecture/roadmap/recommendations, thin-section detection — then reports the run's real per-task token/cost via ccusage, agent-agnostic (Claude Code, Codex, or any other coding agent). Called by the technext-sales-proposal orchestrator skill after mechanical-validator passes, as the final step before delivery.
---

# Judgment reviewer — the checks a script can't do, then a cost report

*Only `<client-slug>-proposal.html` needs to exist — safe to re-run any time (e.g.
right after a manual fix) without touching earlier phases.*

This is a judgment-based review pass over the assembled file — a `fork` works well
here since it benefits from this conversation's full context of what was researched.
`mechanical-validator` already confirmed the objectively-countable stuff (no orphaned
citations, right chart/diagram counts, no leftover placeholders) — this pass checks
what still requires reading and judging content, not just counting it.

## Content review

- Every section has real, specific content — grep the file for `placeholder-note` or
  generic filler phrases; there should be none left.
- Every visible string has both a `t-vi` and a `t-en` span filled in — spot-check
  several sections, not just the first few.
- Any section that reads thin (a couple of generic sentences instead of grounded
  detail) gets re-sent to its owning Phase 1 subagent with a "go deeper, more specific
  to this client" instruction — don't pad thin sections by hand with filler.
- Cross-check internal consistency: the pain-solution matrix's module/AI choices
  should match what `research-ops-tech-agent` actually found; the quotation should
  match that same module plan's scope.

## Citation content check

The mechanical validator already confirmed the *links* aren't orphaned — this checks
whether they're actually right. Spot-check a sample of cited pages and confirm each
one really supports the claim it's attached to, don't just trust that a URL resolves.
Any sentence stating a specific fact (a number, a date, a quote, a review, a named
person) with neither a `.cite` link nor an `.assess` tag is a gap — go back to the
owning subagent and either find the source or mark it as an assessment.

If Phase 0 had meeting notes/transcript pasted in: confirm every fact actually stated
there made it in with a `.grade.confirmed` badge (not silently downgraded to
`.assess`), and every topic the notes *raised but didn't answer* has an explicit
`.callout warn` "to confirm" note rather than being quietly dropped.

## Devil's-advocate review

Before calling the proposal done, argue against the `recommendations` section and the
BPMN·Blueprint·UML process specifically — the parts a real client's IT lead or ops
manager would push back on hardest: Is any recommended module choice unjustified by
the actual pain points found? Does the recommended plan assume dependencies that were
never confirmed (e.g. data export access from a legacy system nobody verified
exists)? Fix what a skeptical reader would flag, rather than presenting the first
draft as final.

## Cost report — run after the content review, every time

Once the review above is done and the proposal is ready to hand over, export the real
cost report, don't just print numbers to the terminal:

```
python assets/ccusage_to_csv.py <client-slug>-cost-report.csv <client-slug>-checkpoint.json
```

That command writes **only the CSV**. It deliberately does not generate any HTML —
presentation is not this script's job, and a per-run HTML file meant one more artifact
to regenerate, go stale, and reconcile against the CSV it was built from.

To *view* cost, open **`assets/cost-dashboard.html`** — a single static page, built
once, that takes any number of `*-cost-report.csv` files (pick the whole `_runs`
folder) and renders them as one table with per-run subtotals, a grand total, and the
missing-task warnings. It is inline-CSS/JS only, no CDN, no network — it opens
straight from `file://`. If it also finds the matching `*-checkpoint.json` files, it
cross-checks them against the CSVs, which is the only way a task with **no** cost row
can be spotted at all (a CSV cannot record its own absences) — so when handing the
dashboard to someone, tell them to load the checkpoints alongside the CSVs.

**This works no matter which coding agent ran the pipeline** (Claude Code, Codex,
Gemini CLI, ...) — a requirement for a skill the whole company uses, since not every
machine/run uses the same agent. The mechanism: `ccusage` already auto-detects and
reads 18+ coding agents' local session logs (no API key, no network call), and its
unified `session --json` command tags every row with which agent produced it
(`"agent": "claude"` / `"codex"` / ...). This script calls that once and matches each
timeline task back to its own session by the `session_id` `checkpoint-manager`
recorded for it — **not** by guessing from timestamps.

**Why not just filter by timestamp**: a raw `ccusage session --json` row is a whole
session's total — it has no idea which task inside that session cost what. Splitting
that by matching timestamps is a guess, and that guess breaks the moment two tasks
share a session, or an unrelated concurrent session overlaps in time (both happened
once in this project). The fix isn't a smarter guess — it's removing the need to
guess: `checkpoint-manager`'s rule that a dispatched task runs in **its own isolated
session** means "this task's cost" is always exactly "this session's cost," found by
exact `session_id` match, for whichever agent ran it. For the handful of phases that
really do run inline in the orchestrator's own session, `checkpoint-manager` records
that session's id with `"shared_session": true` — and this script then writes that
session **once**, labelled `shared-session: <task> + <task>`. It never writes one row
per task for a shared session: that would add the same session's cost to the run total
once for every task it hosted, which is precisely the multiplication this design
removes. A steady `TỔNG` therefore stays the real cost of the run.

Output columns:

| Column | What it is |
|---|---|
| `task_label` | the checkpoint timeline's task name; `shared-session: a + b` when one session hosted several inline tasks (that session appears once, not once per task) |
| `task_duration` | that task's own started→ended span |
| `agent` | which coding agent ran it (`claude`, `codex`, ...) — from `ccusage`'s own tag |
| `session_id` | the exact session id matched — traceable back to `ccusage`'s own log |
| `model_name` | exact model id used inside that session |
| `input_tokens` / `output_tokens` / `cache_creation_tokens` / `cache_read_tokens` | real token counts, as `ccusage` computed them |
| `cost_usd` | `ccusage`'s own computed cost for that model/session — not re-derived here |

**If a task's timeline entry has no `session_id`** (an inline task recorded as `null`
instead of the orchestrator's id — see `checkpoint-manager` rule 2), or `ccusage`
can't find a session matching it, that task gets **no row** in the CSV — the script lists exactly which
tasks are missing and why (`no-session_id-recorded` / `session-not-found-in-ccusage` /
`ambiguous-multiple-sessions-matched`) rather than silently reporting $0 or folding it
into another task's total. Always state that gap explicitly when reporting totals to
the user — never imply the CSV covers the whole pipeline if it doesn't.

**Known anomaly to still watch for**: if a model that clearly isn't Claude shows up
inside a session tagged `"agent": "claude"` (e.g. a `deepseek-*`/`gpt-*` model name),
that's a real internal-tool-routing anomaly (likely an MCP call that routed through a
different provider mid-session) — `--task` mode prints a `⚠ CẢNH BÁO` for this.
Never fold that model's cost into the reported total silently — flag it and treat the
total as possibly inflated until manually confirmed.

Open the CSV with `Read` and summarize the total for the user (e.g. *"Chạy xong hết
pipeline, chi phí thật của lần chạy này là $X — chủ yếu từ Y token ở Phase 1
Group A, xem chi tiết trong `<client-slug>-cost-report.csv`"*), and hand over **both**
files alongside the proposal — the CSV and the HTML table, since a recipient may open
one and not the other — so cost stays visible and re-checkable per task, not just a
number quoted once in chat. If `ccusage`/Node isn't available on the machine, say so
plainly and skip — don't block delivery on it, it's a reporting step, not a gate.
