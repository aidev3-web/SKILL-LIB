---
name: web-osint-scanner
description: Reads and understands the verified client's official website end to end via Jina Reader (no Firecrawl, no Crawl4AI), and extracts every related link (social media profiles, review/listing sites, news mentions, partner/customer pages) so the 4 research subagents know exactly which pages to check instead of guessing. Also does a light mechanical scan of the site's tech stack/traffic signal. Called by the technext-sales-proposal orchestrator right after company-verifier confirms the client's identity, before the 4 research subagents are dispatched.
---

# Web OSINT scanner — read the site, pull out every related link

## What this solves

Before this skill existed, each of the 4 research subagents had to independently
guess which social media profile, review site, or news mention actually belongs to
the client — duplicating the same "is this really their Facebook page?" work 4 times,
inconsistently. This skill does that discovery **once**, up front, and hands every
subagent the same verified link list.

## What to do

Given `company-identity.json` (from `company-verifier`) — its confirmed domain:

1. **Read the site's actual content**, not just its tech signature — using
   **Jina Reader**: prepend `r.jina.ai/` to the page URL (e.g.
   `https://r.jina.ai/https://clientdomain.com/about`) via any HTTP fetch tool
   (`WebFetch` on Claude Code; `curl` or `Invoke-WebRequest` in a shell).
   No API key needed for normal use, returns clean markdown, handles JS-rendered
   pages. Read the homepage plus any "About"/"Contact"/"Team" pages linked from it —
   one Jina Reader call per page, no crawling infrastructure needed.

   **Do not use Firecrawl** (needs a signup + has a monthly credit cap Jina Reader
   doesn't) **or Crawl4AI** (currently blocked on this machine — installing it pulls
   in a native `xxhash` DLL that this machine's Application Control policy refuses to
   load; this is a security-policy block, not a bug, and isn't something to work
   around — if a future machine needs whole-site crawling beyond what a handful of
   known-page Jina Reader calls covers, revisit Crawl4AI there, or ask IT to allowlist
   the DLL).

   This is reading for **understanding**, not just scraping raw HTML — summarize
   what the company actually does, in your own words, as a short paragraph (this
   becomes part of `web-scan.json`, saving the research subagents from re-reading
   the homepage from scratch).
2. **Extract every related link found on the site** — don't just take the footer's
   social icons at face value, also check for links buried in body text, the
   "Contact"/"Press"/"Team" pages, and any embedded widgets (an embedded Google
   Reviews widget, an embedded Instagram feed, etc. all count as a link source).
   Categorize what you find:
   - Social media profiles (Facebook, Instagram, LinkedIn, TikTok, X/Twitter, YouTube
     — whichever actually exist; don't invent ones that aren't linked)
   - Review/listing platforms (Google Business Profile, TripAdvisor, industry-specific
     directories)
   - News/press mentions (an actual "As featured in" link or press-page link — not a
     guess at what press *might* exist)
   - Partner/customer logos or case-study pages, if linked
3. **Light mechanical scan of the domain itself** (no judgment needed, just facts):
   tech stack/CMS in use if detectable from page source, roughly how long the domain
   has existed, whether it serves over HTTPS. Skip anything you can't determine
   directly — don't guess a tech stack from vibes.
4. **Identify 2-4 likely competitors** — one `WebSearch` for "<client's industry/
   niche> <client's city/region> alternatives" or "vs <client name>" is usually
   enough. This is a real step, not a guess left to the orchestrator later — without
   it, nothing in this pipeline actually knows who the competitors are, and the
   `competitor-research-worker` dispatch in Phase 0.9 has nothing concrete to run
   against. A name found this way is a *candidate*, not yet verified — mark each
   with how confident you are (a company explicitly named in an industry roundup vs.
   a same-category business found nearby); `competitor-research-worker` does the
   real research on each once dispatched.
5. **Write `web-scan.json`**:
   ```json
   {
     "summary": "One paragraph in your own words of what this company actually does",
     "links": {
       "social": [{ "platform": "facebook", "url": "..." }],
       "reviews": [{ "platform": "google", "url": "..." }],
       "press": ["..."],
       "other": ["..."]
     },
     "tech": { "cms": "...", "https": true, "domain_age_estimate": "..." },
     "competitors": [
       { "name": "Competitor Name", "url": "https://...", "confidence": "found in an industry roundup article, cited" }
     ]
   }
   ```
   Every entry in `links` must be a URL you actually found on the site — never invent
   a plausible-looking social handle. If a platform you'd expect (e.g. Instagram) has
   no link on the site, that's a real, useful finding (absence itself is data for
   `digital-web`'s "obvious gaps" callout) — record it as absent, don't search for one
   independently and guess it belongs to them. If genuinely no competitor could be
   found (a very obscure/local business), leave `competitors` as an empty array and
   say so plainly — Phase 0.9 then dispatches zero `competitor-research-worker` calls
   rather than inventing names to fill the slot.

## Phase 0.8 — pre-fetch every discovered URL once, for the whole pipeline

Once `web-scan.json` is written, **fetch every URL it lists** (client site pages,
every `links.social`/`links.reviews`/`links.press`/`links.other` entry, plus every
competitor URL identified so far) through Jina Reader, **in parallel**, and save each
page's clean text to `captures/<sha1-of-url>.md`. Write a manifest,
`captures/manifest.json`:
```json
{ "https://example.com/about": { "file": "captures/3f9a2b1c....md", "fetched_at": "2026-09-24T04:00:00Z" } }
```
This exists to solve a real measured problem: without this pre-fetch, all 4 Phase 1
groups (plus the competitor-research workers) independently re-fetch the same ~39
pages live via Jina, one page at a time each — that live-fetch fan-out alone measured
~29 minutes on a real run. Fetching everything once here, in parallel, takes ~1-2
minutes for the same ~39 pages; every downstream reader (Phase 1 groups,
`competitor-research-worker`, `source-auditor`'s `bind_check.py --from-cache`) reads
`captures/*.md` instead of hitting the network again for a URL already captured.
Only fetch live for a URL that genuinely isn't in the manifest (found later, mid-run).

## Output

Two things: `web-scan.json` (the categorized link list + summary, as above), and
`captures/manifest.json` + `captures/*.md` (every discovered URL's page text,
pre-fetched once). The 4 research subagents and `competitor-research-worker` read
both before starting their own work — `research-due-diligence-agent` in particular
should follow the `links.social` and `links.reviews` entries directly instead of
re-discovering them, use the `summary` as a starting point rather than re-reading the
homepage cold, and read `captures/*.md` instead of live-fetching a URL that's already
captured.
