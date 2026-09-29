---
name: source-auditor
description: A hard gate, not an FYI report — re-checks all 4 research subagents' findings.json together, runs a free citation bind-check (assets/bind_check.py) that confirms every inline excerpt really appears on the page it cites, collapses sources that trace to one origin, and re-grades confidence. Blocks front-matter-writer/html-renderer from proceeding until every finding is either properly sourced, tagged .assess, or sent back to its owning subagent for a fix. Called by the technext-sales-proposal orchestrator right after all 4 Phase 1 subagents finish, before any writing/rendering step touches their output.
---

# Source auditor — a gate, not a report

**This is the direct answer to "what if the data is wrong — surely someone reviews it
before it gets used?"** Before this skill existed, each subagent graded its own
sources while writing, then the content just flowed straight into the final page —
nobody who wasn't the original writer ever double-checked it. This skill is that
second, independent set of eyes, and it has the power to **stop bad data from
reaching the written proposal**, not just note it in a log.

## Verify-before-write gate on competitor research (runs before Phase 1, not after)

Everything else in this skill audits content *after* it's written into
`p1-group*.html` — but `competitor-research/*.json` (from `competitor-research-worker`,
Phase 0.9) is read directly by Group A and Group C while they write, so a bad excerpt
in it becomes a bad claim in two sections at once before any bind-check would catch
it. Run this **before** dispatching Phase 1's 4 groups, not as part of the later
audit pass:
```
python assets/bind_check.py competitor-research/*.json --facts -o competitor-facts-bind-check.json
```
Exit code 1 means at least one competitor-research claim's excerpt isn't really on
its source page — route it back to re-run that one `competitor-research-worker`
(cheap, it's a single hard-budgeted worker) rather than letting Group A/C read
unverified competitor facts. Don't skip this because it feels redundant with the
later bind-check on `p1-group*.html` — that later check verifies the *proposal's own*
citations, this one verifies the *shared research input* two groups are about to
build on.

## What to do

Read all 4 **`<client-slug>-findings-group{A,B,C,D}.json`** files (from
`research-due-diligence-agent`, `research-ops-tech-agent`,
`research-delivery-growth-agent`, `tools-documents-agent` respectively) — each group
writes its own file, never a shared one, specifically so 4 parallel agents can't race
on the same file (a real bug: two groups appending to one shared
`<client-slug>-findings.json` in parallel silently dropped citations when they
finished close together). Merging these 4 files into one is this skill's job, not
something the 4 groups coordinate themselves. For every entry across all 4 files:

1. **Source independence check.** If the same claim (or a claim it depends on) is
   backed by multiple URLs that all trace back to one original press release/bio/
   listing (a content-farm re-post, a directory scrape of the same source), collapse
   them to one real source — don't let duplicate mirrors count as independent
   corroboration.
2. **Re-grade confidence**, independently of what the writing agent originally
   claimed:
   - `Confirmed` entries: verify the cited meeting/transcript reference actually
     exists in this run's Phase 0 notes — a `Confirmed` grade with no real meeting
     behind it gets downgraded to `D`/`.assess`.
   - Browser-observed entries (URL listed in `captures/manifest.json` with `"via": "browser"`):
     bind-check the excerpt against that `captures/social/*.md` snapshot instead of the live
     page (which is login-walled). A snapshot missing or not containing the excerpt blocks.
   - `Reported` / `Assumed` entries: check them against `<client-slug>-intake.json`.
     `Reported` needs a pain the user said the client raised (`raised_by: client`);
     anything else is downgraded to `Assumed`. Every `Assumed` pain must carry an
     `.assess` "to verify" tag and appear as a question in `tool-discovery-questions` —
     missing either is a blocking issue.
   - `A`/`B`/`C` entries: spot-check that the `source_url` is a real, resolvable URL
     and its domain plausibly matches the claim's subject (a claim about the client's
     revenue citing an unrelated news site is a red flag, not a pass).
   - Any entry with a missing/empty `source_url` and no `Confirmed`/`Reported`/`.assess`
     equivalent is an **automatic fail** for that claim.
3. **Citation bind check** — run `python assets/bind_check.py
   <client-slug>-p1-group*.html --from-cache captures/manifest.json`. The
   `--from-cache` flag reads `web-osint-scanner`'s pre-fetched `captures/*.md` instead
   of fetching every cited URL live over the network again — this turned a measured
   ~17.5-minute bind-check into a few seconds on a real run, since almost every cited
   URL was already fetched once in Phase 0.8. It only falls back to a live fetch for a
   URL genuinely not in the manifest (e.g. a source found later, mid-run). For every
   inline citation it checks that the quote sitting in
   `.cite-tip-excerpt` is actually present in that source. Verdicts: `bound` (quote
   found verbatim), `partial` (most of the words are there but not as one passage),
   `unbound` (the quote is not in the source), `unreachable`. **Every `unbound`
   citation is a blocking issue** — route it back to the subagent owning that section
   (match the `section` field to the Group A/B/C/D list) naming the exact URL and
   excerpt, so it either corrects the quote or re-tags the claim `.assess`. This is
   the external half of the audit: everything else here re-reads the subagents' own
   output, which cannot catch a citation that points at a page that never said it.
4. **Count real independent sources** after dedup (step 1) — this is the number that
   matters for "is this proposal well-sourced," not the raw citation count each
   subagent reported.

## The gate — this is the part that makes it a gate, not a report

Write `audited-findings.json` (same shape as the input files, merged, with
`grade` fields corrected and duplicates collapsed) **plus** a `blocking_issues` array.
- **If `blocking_issues` is non-empty**: stop here. Route each issue back to the
  subagent that owns that section (match the `section` field to the Group A/B/C/D
  ownership list) with the specific problem named (not "fix your sources" — say
  exactly which claim, which URL, which reason it failed). **Do not let
  `front-matter-writer`, `chart-data-analyst`, or `html-renderer` proceed on this
  run until the affected subagent re-submits a fix and it passes re-audit.** A
  faster-but-wrong report is not an acceptable trade — this is the one step in the
  pipeline whose whole job is refusing to let ungrounded content through.
- **If `blocking_issues` is empty**: `audited-findings.json` is what
  `chart-data-analyst` and `front-matter-writer` read from here on — never the raw,
  un-audited per-subagent `findings.json` files directly.

## Generate `sources-citation` here, not by hand in Group C

The `sources-citation` sidebar section (in `assets/menu-structure.md`) is just a
formatted list of every citation already used elsewhere in the file — it needs no
research of its own, so `research-delivery-growth-agent` (Group C) no longer writes
it by hand. Once `audited-findings.json` has zero `blocking_issues`, generate the
`<section id="sources-citation">` fragment mechanically from it (one row per unique
`source_url`, with the section(s) that cite it) and append it to the file that will
be assembled — this is a formatting pass over already-audited data, not a writing
task that benefits from an agent's judgment.

## Citation bind-check — the free replacement for a paid verification API

An earlier plan put a paid claim-verification API (Webcite) behind this gate. That is
no longer needed, because the thing it sold is the thing `research-rules.md` already
demands — *a real short quote actually taken from that source page* — and that check
runs for free from `assets/bind_check.py`:

- **Fetch**: Jina Reader (`https://r.jina.ai/<url>`), free and keyless. `--direct`
  fetches the URL straight instead, for a source Jina cannot read.
- **Extract**: `trafilatura` when installed, otherwise a built-in tag-strip. Jina
  already returns markdown, so the default path needs no extra dependency at all.
- **Compare**: a normalized whole-excerpt substring match first, then token coverage
  (`--threshold`, default 0.85) to separate a loose paraphrase from a missing quote.

Usage:

    python assets/bind_check.py <client-slug>-p1-groupA.html \
        <client-slug>-p1-groupB.html <client-slug>-p1-groupC.html \
        <client-slug>-p1-groupD.html -o bind-check-report.json

Exit code 1 means at least one citation is unbound, i.e. this gate has blocking
issues. Cost: zero credits, no third-party MCP, and nothing that can contaminate the
`ccusage` cost report (see `judgment-reviewer` on that specific failure). `--limit N`
runs a cheap sample when a full pass is too slow, and `--sleep` keeps fetch rate
polite.

An `unbound` verdict is not automatically fabrication — it can also mean the excerpt
is a loose paraphrase the subagent wrote from memory, or the page moved. Deciding
which is the reviewer's job. The script exists so that nobody has to hope.

## Output

`audited-findings.json` (always) and, only when something failed, a clear per-issue
routing note back to the owning subagent. Downstream skills (`chart-data-analyst`,
  `front-matter-writer`, `html-renderer`) must not run against unaudited data.
`bind-check-report.json` sits alongside `audited-findings.json` as the raw evidence
behind any citation-related blocking issue.
