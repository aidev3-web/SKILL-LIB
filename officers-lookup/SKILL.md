---
name: officers-lookup
description: Resolves a verified client's directors, officers and founders from official public registries — country-selected (Companies House for the UK, OpenCorporates for other jurisdictions, SEC EDGAR for US public companies) — supplemented by Wikidata and the company's own team/about page. Writes officers.json so the research subagents never have to guess a named person. Called by the technext-sales-proposal orchestrator right after company-verifier (and web-osint-scanner), before the 4 research subagents are dispatched.
---

# Officers lookup — who actually runs this company, from sources that can be checked

## What this solves

`founders-leadership` and `staff-org` are the two sections most likely to be filled
with plausible-sounding invention, because a company's own site rarely names more than
one or two leaders. The pipeline rule is explicit — *never invent a named person and
attach a fake-looking citation* — so the honest options were "write a thin section" or
"find a real, citable source for each name".

This skill is that source step, and it replaces the earlier plan to wire an Apollo MCP
server in for contact enrichment. Contact enrichment was the wrong answer: its value
is verified work emails and direct dials, which this pipeline never uses, and it sits
squarely across the personal-data line the skill draws (see "Ethics boundary" below).
Official registries are better on every axis that matters here — they are primary
sources, they are free, and every fact comes with a public URL the client can check.

## When to run it

Right after `company-verifier` has written `company-identity.json` (which gives you
the **country** that selects the registry) and `web-osint-scanner` has written
`web-scan.json` (which gives you the site/team-page links). Before the 4 research
subagents are dispatched, so `research-due-diligence-agent` can read the output
instead of searching for officers itself.

## Route by country — pick the registry, don't query all three

Read `country` from `company-identity.json`. Query **one primary registry**, then fall
back only if it returns nothing.

| Client country / type | Primary source | Endpoint shape | Cost |
|---|---|---|---|
| United Kingdom | **Companies House** | `https://api.company-information.service.gov.uk/company/{company_number}/officers` | Free, but needs a free registered API key (HTTP Basic, key as username) |
| United States — public company | **SEC EDGAR** | Full-text search `https://efts.sec.gov/LATEST/search-index?q=...&forms=DEF 14A`, filings index `https://data.sec.gov/submissions/CIK##########.json` | Free, no key — but send a descriptive `User-Agent` per SEC's access policy |
| Most other jurisdictions | **OpenCorporates** | `https://api.opencorporates.com/v0.4/companies/{jurisdiction}/{company_number}/officers` | Requires an API key; the free allowance is small, so spend it deliberately |
| Any country, company notable enough to have an entry | **Wikidata** | SPARQL, or `https://www.wikidata.org/w/api.php?action=wbgetentities&ids=...` | Free, no key |
| Any country | **The client's own team/about page** | fetched via Jina Reader (`https://r.jina.ai/<url>`) | Free, no key |

Wikidata and the team page are **always** worth doing — they are cheap, and they
cover the very common case where the company is a private SME that appears in no
registry at all.

Wikidata properties to read: `P112` founder, `P169` chief executive officer, `P108`
employer, `P39` position held. Team-page links come from `web-scan.json` — follow the
`About`/`Team`/`Contact`/`Press` links it already extracted rather than re-crawling
the site.

## Ethics boundary — professional-role public information only

This is a hard constraint, not a preference, and it is the reason the registries are
acceptable where a contact-enrichment database is not:

- Record **only** what the source publishes as part of that person's professional
  role: name, role/title, the organisation, appointment date, and the public URL that
  says so.
- Never record a personal email address, personal mobile number, home address, date of
  birth, family details, or anything else about the person outside their business
  role — even if a source happens to expose it.
- Never use a non-public collection method, and never use a data broker to *find*
  personal contact details for these sections. The proposal does not need them.
- If a registry exposes a person's partial date of birth (Companies House does, for
  directors), **do not carry it into the proposal** — it is not needed for the section
  and does not belong in a sales document.
- A person who is not a director/officer/founder and has no public professional
  presence should not be named at all.

## Confidence grading

Grade every entry the same way `research-rules.md` grades any other finding:

- **A** — an official registry or the person's own company page (Companies House, SEC
  EDGAR, OpenCorporates, the client's own team page).
- **B** — Wikidata or another reputable independent source.
- **C** — a single unverified mention (one press article, one directory listing).
- **D** — anything you could not confirm → becomes an `.assess` tag or a "to confirm"
  callout in the section, never a named person with a citation.

## Output

Write `officers.json` — an array, one object per person:

```json
[
  {
    "name": "…",
    "role": "Managing Director",
    "org": "<legal name from company-identity.json>",
    "appointed": "2019-04-02",
    "jurisdiction": "GB",
    "source_url": "https://find-and-update.company-information.service.gov.uk/company/…/officers",
    "grade": "A",
    "as_of": "2026-09-24"
  }
]
```

`source_url` is mandatory for grades A–C — a named person with no public URL does not
go in this file. Set `"grade": "D"` (or omit the person) rather than leaving
`source_url` null.

Also report back to the orchestrator, in plain language:

- which registry you queried and whether it returned a match;
- which people you could confirm, and at what grade;
- **explicitly, when you found nothing** — "GLEIF has no LEI for this company,
  Companies House does not apply (not a UK entity), OpenCorporates returned no
  officers, and the site's team page lists no names." An empty `officers.json` is a
  valid and useful result: it tells `research-due-diligence-agent` to write
  `founders-leadership` from what genuinely exists and to mark the rest as
  unverified, instead of inventing a plausible leadership team.

## What this skill is not

It is not a contact-enrichment step and must never grow into one. If a future
deliverable genuinely needs outreach contacts (emails, phone numbers) — for example a
campaign pushed into Odoo CRM — that is a separate, explicitly-scoped decision to be
put to the user, with its own privacy review. It does not belong in this pipeline's
research path.
