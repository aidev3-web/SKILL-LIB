---
name: proposal-library-publish
description: Add or update a finished TechNext sales proposal's card in the TechNext Proposal Library (the internal, password-protected list of client proposals) over HTTPS, with nothing to install, no git, no GitHub account and no key. Used by technext-sales-proposal as its Phase 5 and by technext-meeting-to-proposal after a meeting update. Also use it when the person says "đưa proposal lên thư viện", "thêm vào Proposal Library", "cập nhật thẻ trong library", or asks why a card is missing or shows an Auto-added badge. It sends only the card text and the section list, never the proposal HTML; it does not build or edit a proposal and does not change who can open an artifact.
---

# Proposal Library publish

One script, `library_publish.py` in this folder (Python 3, standard library only), puts a proposal's card into the TechNext Proposal Library. The proposal itself stays a claude.ai artifact; the card only links to it.

## What it needs
- The proposal folder (`<slug>-proposal.html` and, if present, `<slug>-intake.json`, `company-identity.json`, `<slug>-checkpoint.json`).
- The artifact address of the published proposal (`https://claude.ai/artifact/<id>`). The caller publishes the artifact first; this script never publishes it. If there is no artifact yet, stop and say so: do not invent an address.
- The library address, in `library-endpoint.json` next to the script (`{"endpoint": "https://..."}`, shipped with this skill by the library owner). `PROPOSAL_LIBRARY_URL` or `~/.claude/proposal-library.json` (`"endpoint"`) override it.

## Run it
```
python <this skill's folder>/library_publish.py <proposal folder> --artifact-url <url> --summary "<one honest sentence, at most 240 characters>" --industry "<short phrase>" --by "<the person's name>"
```
Other options: `--country`, `--title`, `--status ready|followup|won|lost|archived` (a new card is `ready`; pass `followup` only when the person says the proposal was sent or discussed), `--dry-run` (shows the card, sends nothing), `--meeting-date` and `--next-followup` (YYYY-MM-DD), `--meeting-file`. Run `python library_publish.py --help` for the rest, including `extract-meeting`, `check-meeting`, `links` and `mark-link-used`, which `technext-sales-proposal` (Phase 5) and `technext-meeting-to-proposal` describe where they are used.

The card text never carries the proposal's contact details, prices or CRM fields. Write the summary honestly: if the proposal is unfinished or has open items (unconfirmed company identity, prices TBC), say so in it.

## What happens to the card
The library owner decides, in the library's own settings, what a card sent with no key does:
- **live** (the usual setting): the card appears in the library at once with an **Auto-added** badge, which only says nobody has checked it.
- **queue**: the card waits in a review queue and is not shown until the owner accepts it.
- **closed**: the library answers that it is not taking cards without a key; tell the person to ask the owner.
Sending the same proposal again refreshes the same card (the proposal checkpoint remembers what was sent, so a re-run keeps the summary, industry and status unless new ones are passed). A card that points at a different artifact never overwrites a live card. With an optional team key in the same settings, the card is written straight into the library, with the same badge.

## Settings file (optional)
`~/.claude/proposal-library.json`: `{"endpoint": "<https address>", "key": "<team key>", "repo": "<clone path>", "mode": "auto" | "ask" | "off", "name": "<who is updating>"}`.
- `auto` (default): send as soon as the caller says so.
- `ask`: the script stops with exit code 3 and prints the card; show it to the person and only if they say yes run it again with `--yes`.
- `off`: do nothing and say that library publishing is switched off.

## Rules
- Exit code 2 means nothing was sent and the script printed a one-line reason. Show it, leave the proposal as it is, and tell the person to run this again once fixed. A failure here never fails the proposal run.
- Never print, ask for or store a key or password. The address file holds no secret.
- Never send the proposal HTML or anything else to the library; never touch another repository; never force anything.
- Tell the person after sending: the artifact stays private until they press **Share** on its page and choose TechNext (this skill cannot change sharing), and the card shows an Auto-added badge until the owner clears it.
- A git clone is used only when one is named (`--repo`, `PROPOSAL_LIBRARY_REPO` or `"repo"` in the settings file); then it edits that clone's `registry.json`, rebuilds, runs the library's tests, and pushes with the person's own git login.
