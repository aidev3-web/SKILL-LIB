# Shared research/writing rules — read this before writing any section

Applies to every Phase 1 subagent (`research-due-diligence-agent`,
`research-ops-tech-agent`, `research-delivery-growth-agent`, `tools-documents-agent`).
These are the rules that make a section trustworthy, not just plausible-sounding —
follow them exactly, they're checked both mechanically (`mechanical-validator` skill)
and by judgment review (`judgment-reviewer` skill) afterward.

## Start from `web-scan.json`, don't rediscover it

Before searching anything yourself, read `web-scan.json` (written by the
`web-osint-scanner` skill, right after `company-verifier` confirms the client). It
already contains: a plain-language summary of what the company does, and every
social media/review/press link actually found on their site — categorized. **Follow
those exact links first** instead of independently guessing a social handle or
review-site URL — this is the same discovery step every one of the 4 subagents would
otherwise redo separately, inconsistently.

## Research playbook — a concrete checklist, not "look into it generally"

For each social/review link in `web-scan.json`, actually visit it and extract
specifics, not a vague impression:
- **Social profiles**: how long has the account existed, posting cadence (active
  weekly? gone quiet for months?), follower count if visible, the tone/topics of the
  last several posts, obvious engagement level (real comments vs. none).
- **Review platforms**: overall rating, number of reviews, read the actual text of a
  handful of the most recent + most critical reviews — pull specific recurring praise
  and specific recurring complaints, not "reviews are mostly positive."
- **Press/news mentions**: what specifically was said, when, is it still accurate
  (a 3-year-old article about a since-closed program isn't current fact).
- **If `web-scan.json` shows a platform is absent** (e.g. no Instagram link found),
  that absence is itself a finding for `digital-web`'s "obvious gaps" — don't go
  searching for one independently and guess it's theirs.

## Every claim must be verifiable

- Any claim from a real source gets a citation marker right next to it — see
  "Citation markup" below. The source preview appears on hover/focus, not only on
  click.
- Any claim that is TechNext's own inference/estimate/opinion must be labeled as such
  with `.assess` (see template CSS) — never presented with the same visual weight as a
  sourced fact.
- Never invent a number, quote, review, or named person and attach a fake-looking
  citation to it. If something can't be found or verified, say so instead of guessing
  confidently.
- Attach a source URL to every claim (**the exact page**, not just the domain), and
  mark clearly which findings you could *not* verify. A claim with no URL and no
  "unverified"/`.assess` flag is not usable — treat it as if it weren't written.

## Citation markup — Wikipedia-style hover card, not click-to-see

Every citation is a `.cite-wrap` span (already styled in
`assets/proposal-template.html`) wrapping the `.cite` link plus a `.cite-tip` card
shown on hover/focus, with the actual excerpt up top and the source's domain + a
link-out affordance in a footer row at the bottom:

```html
<span class="cite-wrap" tabindex="0">
  <a class="cite" href="https://client-delta.example/" target="_blank" rel="noopener">[2]</a>
  <span class="cite-tip">
    <span class="cite-tip-excerpt">"24/7/365 service availability with 100% spare parts stock, 18 in-house technicians committed to a 24-hour response time."</span>
    <span class="cite-tip-foot">
      <a class="cite-tip-domain" href="https://client-delta.example/" target="_blank" rel="noopener">client-delta.example</a>
      <span class="cite-tip-icon">↗</span>
    </span>
  </span>
</span>
```

- `.cite-tip-excerpt` is a **real short quote or close paraphrase actually taken from
  that source page** supporting this exact claim (1–2 sentences) — not a restatement
  of the claim itself. If you can't produce a real excerpt for a claim, that's a
  signal the source may not actually support it — re-check it rather than inventing
  filler text.
- `.cite-tip-domain` is a **real clickable `<a href="...">`** (same URL as `.cite`
  above it), showing just the bare domain.
- Never emit a bare `<a class="cite" href="...">[n]</a>` with no `.cite-wrap`/
  `.cite-tip` around it, and never leave `.cite-tip-excerpt` empty — both are checked
  mechanically. The tap-to-preview mobile fallback is already wired into the shared
  template `<script>` — don't re-implement it per section.

## Source independence

A fact copy-pasted across ten content-farm/aggregator sites that all trace back to
the same original bio or press release is **one source, not ten** — matters most for
Founders & Leadership, Staff & Org, and Reviews & Reputation. Trace a claim back
toward its original source rather than counting duplicates as independent
confirmation.

## Confidence grading

Alongside the URL, each finding gets a rough confidence grade:
- **Confirmed** — stated directly by the client themselves in meeting notes/transcript
  the user pasted at Phase 0. Not "higher than A" — a **different kind of source**.
  Never render it as a `.cite` link — use a `.grade.confirmed` badge instead, with a
  short note of what it's from, e.g. "Confirmed — discovery call 18/06".
- **Reported** — the TechNext user says the **client** raised it in a call/meeting, but
  no notes/transcript were pasted (from `<client-slug>-intake.json`). Render as a
  `.grade` badge "Reported — TechNext sales, <date>", never as a `.cite` link. Weaker
  than Confirmed; stronger than a web source for the client's own pains.
- **Assumed** — a pain TechNext expects but the client has not voiced (contact status
  "not contacted yet", or the user said it was their own guess). Always an `.assess`
  tag reading "Assumed — to verify in the meeting", and it must appear as a question in
  `tool-discovery-questions` / `pm-unknowns`. Never promote it to Confirmed or Reported.
- **Browser-observed** (from `social-browser-scan`) — a post/review read in the user's
  logged-in browser. Grade **B** when it is the company's own official account, **C** for a
  single review/comment. Cite it like any source (`.cite` + hover excerpt), pointing at the
  page URL, with the label "Quan sát trực tiếp qua trình duyệt, <ngày>"; the excerpt must be
  verbatim in its `captures/social/*.md` snapshot. Never include reviewer/commenter names.
- **A** — primary/official source (company site, filing, direct quote).
- **B** — reputable independent secondary source (established press, industry report).
- **C** — single unverified or user-generated source (one review, one social post).
- **D** — unverifiable / TechNext inference — this becomes an `.assess` tag, never a
  `.cite` link.

## "To confirm" gaps — a third state, not the same as `.assess`

When pasted meeting notes/transcript **raise** a topic but don't actually answer it,
that's a known gap with a clear next action, not a sourced fact or a TechNext
inference. Flag it with a `.callout warn`: *"Chưa xác nhận được X trong buổi họp — cần
hỏi lại khách trước khi [ví dụ: chốt số liệu demo]."* Don't silently drop it, and
don't disguise it as an `.assess` estimate.

## Structured findings file

In addition to your HTML section(s), write **your own**
`<client-slug>-findings-group<X>.json` (`X` = A/B/C/D — never a shared
`<client-slug>-findings.json`, which is a real race condition when 4 groups append in
parallel; `source-auditor` merges the 4 group files afterward): an array of
`{ "claim": "...", "section": "<sidebar slug>", "source_url": "...", "grade": "Confirmed|Reported|Assumed|A|B|C|D", "excerpt": "..." }`
objects, one per citation you actually used (`source_url` omitted/null for
`Confirmed` entries — cite the meeting instead). See `assets/section-shell.md` for the
full markup contract this pairs with.

## Charts & diagrams — build them yourself, in the same call

Don't hand-roll chart configs — use `assets/proposal-template.html`'s ported helper
functions (`regChart`, `mkChart`, `PAL`, `baseOpts`, `gridScale`, `inkColors`), see
`SKILL.md`'s "Charts & diagrams" section in the orchestrator skill for the exact
manifest (which canvas ids/diagram slots you own). Key mechanical rules:
- **Chart labels/dataset labels are always plain strings, never HTML** — Chart.js
  renders them as literal canvas text.
- **Tooltips on any chart plotting percentages must say so** — add a
  `tooltip.callbacks.label` formatter appending `%`.
- **Diagrams are static HTML, never Mermaid** — wrap each in
  `<div class="diagram-block">`, build the inside with `.tl`/`.tbl`/`.quad`/`.acc`
  components.

## Reference file

Work from the **literal contents** of `assets/proposal-template.html` — its
`#sidenav`/`buildNav()` mechanism, its single sliding `.tb-btn` VI/EN switch, its
`#progress` bar, its component classes. Return only the `<section id="...">`
fragment(s) for your owned slugs, never a full `<html>` document. Also return a short
plain-text digest of your 3–5 most important findings — the `front-matter-writer`
skill uses these digests instead of re-reading your full section HTML.
