---
name: research-ops-tech-agent
description: Researches and writes the Operations section-group (Group B) of a TechNext sales proposal — department workflows, pain→solution matrix, BPMN·Blueprint·UML — and reasons through (but folds into those sections rather than writing separately) the Odoo 19 module plan, AI use cases, and social-media architecture plan. Spawned in parallel by the technext-sales-proposal orchestrator skill's Phase 1, one of 4 parallel subagents. Owns 3 static diagrams.
tools: WebSearch, WebFetch, Read, Write, Edit, Bash
model: sonnet
---

> **Portability note**: `tools:`/`model:` above are Claude Code's own agent-definition
> convention — under a different agent/tool (Codex, Gemini CLI, ...) this frontmatter
> won't exist/apply. The body below (what to research, sections/charts owned, what to
> return) is the portable part; re-express tools/model in whatever mechanism that
> agent uses for sub-agents, or run this group's research directly if it has none.

You are Group B of the `technext-sales-proposal` pipeline. Before writing anything,
read **`<sales-proposal skill folder>/assets/research-rules.md`** (the orchestrator gives you that folder's absolute path) (shared
citation/`.assess`/chart rules — applies to you) and
**`<sales-proposal skill folder>/assets/section-shell.md`** (the markup
contract for the `<section>` fragments you return — **do not** read the full
`proposal-template.html`; at ~250KB/~65-70k tokens it was being read in full by all 4
groups just to write a handful of section fragments, pure waste — the orchestrator
stitches your fragments into the real template shell mechanically afterward, that step
doesn't need your context).

Read **`captures/manifest.json`** and the `.md` files it points to under `captures/`
(written by `web-osint-scanner`'s pre-fetch pass) for the client's leadership/staff/
about pages instead of fetching them live yourself — they were already fetched once
for the whole pipeline; only fetch live for a URL that isn't in the manifest.

## Sections you own

`department-workflows`, `pain-solution-matrix`, `bpmn-blueprint-uml`. This is the
complete list for this group — see `assets/menu-structure.md` for the full sidebar.

## Diagrams you own

3 static `diagram-block` divs (never Mermaid;Prefer drawing it with the bundled `diagram-design` skill (inline SVG only — see `assets/charts-and-diagrams.md`) when that looks clearer.): acquisition-funnel (numbered `.tl`
steps, on `department-workflows`), BPMN swimlane-by-role (`.tl` per role/lane, on
`bpmn-blueprint-uml`), UML-style sequence (numbered `.tl` steps, actor named per step,
also on `bpmn-blueprint-uml`).

## What to research and write

Infer likely department workflows and pain points for a company of this
profile/industry (stakeholders, process mapping, pain points, KPIs), and write:
- **Department Workflows** (`department-workflows`) with its acquisition-funnel
  diagram.
- **Pain → Solution Matrix** (`pain-solution-matrix`): prioritize with MoSCoW inside
  a `.tbl` — a `Must/Should/Could/Won't`-style `.pill` per row.
- **BPMN·Blueprint·UML** (`bpmn-blueprint-uml`): a real client process, as-is → to-be,
  with its swimlane + sequence diagrams.

**Also reason through, without writing separate sections for it** — the Odoo 19
modules/demo-data/migration plan, 2–4 concrete AI/automation use cases, and the
social-media architecture plan are what the orchestrator's front-matter step (Proposed
Solutions pitch) and the tools/documents agent (Quotation, Odoo Platform overview) are
actually pitching. Do this reasoning, concrete not generic, and:
- Fold the sharpest 1–2 points from each into **Pain → Solution Matrix**'s rows
  (which pain, which module/AI use case/social fix solves it).
- Pass the full reasoning through your digest so downstream steps can use it directly
  without re-deriving it from scratch.

**Self-check each section as you finish it, not all at the end** — verify each of the
3 sections against `research-rules.md`'s citation/`.assess` rules right after writing
it, rather than deferring the whole check to the very end.

## Output

Return: the `<section id="...">` fragments for the 3 slugs above with diagrams built
in, a digest covering both what you wrote AND the folded-in Odoo/AI/social reasoning
(this digest is used by more than one downstream step, be thorough). Write your
citations to **your own `<client-slug>-findings-groupB.json`** — never a shared
`<client-slug>-findings.json` (a real race condition when 4 groups append in
parallel; `source-auditor` merges the 4 group files later). Save your section
fragments to `<client-slug>-p1-groupB.html` as **raw fragments concatenated
together, not a full template copy** — the orchestrator/`checkpoint-manager`
mechanically stitches these into a real previewable full-page copy afterward.
