---
name: front-matter-writer
description: Writes the front-matter sections of a TechNext sales proposal — Overview, Executive Summary, Recommendations, and the 3 Proposed Solutions pitches — directly from Phase 1's 4 subagent digests, no extra research or agent call needed. Called by the technext-sales-proposal orchestrator skill's Phase 2, after all 4 Phase 1 subagents finish and source-auditor has written audited-findings.json.
---

# Front-matter writer — synthesis of Phase 1's findings, not new research

**Run order:** only after `source-auditor` (Phase 2.5) has written `audited-findings.json`
with an empty `blocking_issues`. Cite from `audited-findings.json`, never from the raw
per-group findings files. Write your own citations to `<client-slug>-findings-frontmatter.json`;
the orchestrator bind-checks that file with the same gate before `chart-data-analyst` runs.

`pre-meeting`, `overview`, `exec-summary`, `recommendations`, `solution-odoo-erp`, `solution-ai`, and
`solution-social-media` are synthesis of what Phase 1's four subagents already found
and returned (their short digests) — read `<client-slug>-p1-digests.json`, not the
full Phase 1 group HTML files. This is fast enough to do directly, without spawning
another agent — a fifth agent call here would just add another sequential wait for
no real benefit.

*Checkpoint resume: save output to `<client-slug>-p2-frontmatter.html` as a full
template copy of
`<skill-root>/assets/proposal-template.html` (like Phase
1's group files — openable/previewable, everything but the front matter left as
`placeholder-note`) and report `phase2: "done"` back to `checkpoint-manager`.*

## Overview + Executive Summary

Chart markup rules (validator check 14 fails the build otherwise): every `<canvas>` is the direct child of `<div class="chart-box" style="height:280px">` (260–400px), never a bare canvas in a `.card`; colours only via `PAL[i]` (alpha as `PAL[0]+'33'`), never hex/rgba literals; options through `baseOpts({...})` and `gridScale()`.

Also add the `cRevMix` (doughnut) + `cScorecard` (bar) charts while writing
`exec-summary`, via `regChart(() => mkChart(...))`.

- **Executive Summary ICP-fit table**: before the prose recommendation, a small
  `.tbl` scoring this client's fit — industry match, company size, likely buyer
  persona reached, timing signal — each cell **Strong / Moderate / Poor** with its
  evidence (`.cite`/`.assess`). Close with 2–3 concrete "why now" hooks from Phase
  1's findings, not generic value-prop language.
- **Executive Summary prose** (management-consulting communication style): lead with
  the answer/recommendation in the first sentence, then supporting evidence, then the
  roadmap and biggest risk — not a chronological recap. A reader who only reads this
  section should already know what TechNext recommends and why.

## Recommendations (`recommendations`, right after Executive Summary)

Boss feedback 2026-09-23: *"give recommendations on how it should be"* was flagged as
missing. This is the one section whose entire job is a direct, opinionated answer to
that: **what should this client's business/tech/marketing setup actually look like**,
stated plainly, not hedged.

- A short **`.lead` recommendation paragraph** — 3–5 concrete "the company should…"
  statements, each grounded in a Phase 1 finding (cite it), not generic advice that
  would apply to any company.
- **`cRisk`** (bubble, probability × impact) — pull the sharpest 4–8 risks out of the
  `research-ops-tech-agent`/`research-delivery-growth-agent` digests instead of a
  full separate Risk Register table.
- **`cKpi`** (bar) + **`cRoi`** (line) — a small set of baseline-vs-target KPIs and a
  cumulative cost/benefit curve, framed as *recommended* targets, not a delivery
  commitment (tag the whole block `.assess` — these are TechNext's modelled
  projections, not measured results).
- A short **Mutual Action Plan** `.tbl` — Step / Owner (TechNext or Client) / Target
  date (relative, e.g. "Week 1") / Done-when — the concrete path from "proposal
  delivered" to signature.
- Mechanically checked: `mechanical-validator` requires `.assess` presence here.

## Proposed Solutions (`solution-odoo-erp`/`solution-ai`/`solution-social-media`)

The pitch itself, placed right after Executive Summary + Recommendations, before Due
Diligence — what TechNext would actually do for this client in that service line, why
it fits Phase 1's findings, a rough scope/effort indication (detailed pricing stays in
`tool-quotation`, detailed architecture stays in the research subagents' technical
sections — this is the pitch, not the spec).

**Whitespace framing**: frame each as what the client already has vs. could have —
e.g. "has a Facebook page, no Instagram or content cadence" → the Social Media
whitespace; "spreadsheet-based inventory, no CRM" → the Odoo whitespace. Every one of
the three gets real content every time — TechNext's decision to always pitch all
three was made deliberately, don't second-guess it per client.


## `pre-meeting` (Read before the meeting)

Fill the 4 fixed parts, keeping their ids: `pm-company` (5–7 cited facts about the client),
`pm-person` (the person being met: confirmed role with links, stated priorities, unverified
career marked grade C, how to talk to them, meeting goal — public professional information
only), `pm-issues` (a table Issue | AS-IS | Competitors | TO-BE, one row per confirmed pain),
`pm-unknowns` (a table Unknown | Why AI couldn't get it | Question to ask). Leave `#mustRead`
empty — the template builds it from every section tagged `data-star="1"`. Never state as fact
something only inferred (e.g. a regulation "applies" to the client) — say "if…, to confirm".
