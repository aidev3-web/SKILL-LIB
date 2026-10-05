---
name: technext-meeting-to-proposal
description: Send a meeting recording (video or audio) to TechNext's Minutes Studio over the office network, wait for the minutes, and write what the client said into an existing TechNext sales proposal (the Meeting Minutes section plus the related sections). Use when the user hands over a meeting recording file for a proposal they already have, says "gửi cuộc họp lên Minutes Studio", "cập nhật proposal từ cuộc họp", "đưa biên bản họp vào sales proposal", or offers a recording instead of pasted notes. Does not build a proposal from nothing and does not email anything.
---

# Meeting recording → minutes → sales proposal

For **any TechNext user**. Nothing here belongs to one person: ask for the proposal folder, the person's email, and the server address every time they are not already known.

## What it needs
- The Minutes Studio API address, for example `http://192.168.10.157:8502` (the administrator gives it): the `MINUTES_API_URL` environment variable, or a one-line file named `.minutes-api` in the project folder (or above), or the `DEFAULT_API_URL` set at the top of `scripts/minutes_client.py`. The script reads them in that order. If none gives an address, say so and stop; do not guess one.
- The person's **Claude account email** (it names them to the server and filters "my runs"). Use the email of the account in this session; if you cannot see one, ask once. There is no password: the email is self-declared and only the office network is trusted. Say this plainly if asked.
- An existing proposal folder holding `<slug>-proposal.html`, `<slug>-findings.json`, `<slug>-checkpoint.json` (and `<slug>-intake.json` if present). Read `~/.claude/skills/technext-sales-proposal/assets/research-rules.md` and `menu-structure.md` before touching it.
- Python 3 (the helper script uses only the standard library). The script is `scripts/minutes_client.py` in this skill's folder; below it is called `CLIENT`.

## Steps

1. **Collect and check, before any cost.**
   Ask for: the recording path, the proposal folder (slug), and optionally the client name, meeting type, subject and date. **Also ask who was in the meeting (first names and the company name) and any product or place names, and pass them all as `--terms`** (comma separated, for example `--terms "Minh,Linh,Tuan,Odoo,Zalo"`): without them the transcription often mishears names ("Minh" became "Min"). The date matters too: pass the real meeting date with `--date`, because the minutes turn "by Friday" into a calendar date from it.
   Check the recording exists and the proposal files are there. If a proposal file is missing, stop and say which: sending first would spend money transcribing a meeting that has nowhere to go.

2. **Tell the person where the audio goes, then get a yes.**
   Say: the recording is uploaded to the Minutes Studio on the office network, then its audio goes to the transcription service set on that server (Deepgram or AssemblyAI) and the text to Anthropic. Name the **file** and the **proposal** that will be changed. Wait for an explicit yes. A yes for one meeting is not a yes for the next.

3. **Send.**
   `python CLIENT send "<file>" --owner <email> --date YYYY-MM-DD --terms "names,products" [--client X --meeting-type Y --subject Z]`
   It prints `run_id` and `web_url`. Give the person the `web_url`: they can watch the run there.

4. **Wait.**
   `python CLIENT wait <run_id> --owner <email>` (progress on stderr). Long meetings take a while; run it in the background if your tool allows and report progress in a short line now and then. Exit codes:
   - `0` done → continue.
   - `2` a person must open the link: an unknown voice appeared and needs a name. Give the `web_url`, say what to do (listen, name the voice, press resume), and **stop**. Offer to continue when they say it is done (then run `wait` again).
   - `3` the run failed, `4` timed out: report `message` and the `web_url`; do not touch the proposal.
   - `1` the call failed (server unreachable, wrong email, someone else's run): show the message and stop.

5. **Fetch.** (When you read the minutes, check names, dates and weekdays against what the person told you; the server already flags a weekday that does not match its date.)
   `python CLIENT fetch <run_id> --owner <email> --out "<proposal folder>/captures/meeting-<YYYY-MM-DD>" --pdf`
   Always pass `--pdf`: it writes `minutes.json`, `transcript.json`, `status.json` **and downloads the PDFs** (the minutes PDF and the transcript PDFs) into that folder, so the person has them next to the proposal. Read `status.json` for `qa_issues` and report them.
   Also write `<proposal folder>/captures/meeting-<YYYY-MM-DD>.md`: a short readable note with a first-line comment `<!-- source: Minutes Studio run <run_id> | captured <date> | by <email> -->`, then the decisions and action items from `minutes.json` with their evidence times.

6. **Record the facts.**
   - Set `has_notes: true` in `<slug>-intake.json` (create the key if needed; do not drop other keys).
   - Facts the client said become `Confirmed — <meeting type>, <date>`, the highest trust grade, in `<slug>-findings.json`, following the existing findings format and `research-rules.md`. Keep only what the minutes actually evidence (each decision and action item carries an evidence time). Anything marked implied, as heard or TBC stays marked that way. Do not turn guesses into Confirmed.

7. **List what will change, and get approval.**
   Show the person: the `meeting-minutes` section, plus the **related sections** the Confirmed facts bear on (pick them from `menu-structure.md`: for example needs and pains, current operations, budget or timeline, recommendations). For each one say in a line what would change. Wait for approval of the list; the person may remove sections. Never change a section they did not approve.

8. **Rewrite the approved sections.**
   Follow `checkpoint-manager` ("Section-level touch-ups"): one narrowly scoped `Agent` call per owning agent with the real template markup and `research-rules.md`. `meeting-minutes` is owned by `tools-documents-agent`. The bilingual markup contract is `assets/section-shell.md` (every string in `t-vi` and `t-en` spans). Patch `<slug>-proposal.html` **directly**, replacing only the approved `<section id="...">…</section>` blocks and leaving every other byte as it was. (The group draft files `p1-group*.html` are deleted when a proposal is finished, so the final file is the thing to edit. Keep a backup copy first, `<slug>-proposal.before-meeting.html`, and say where it is.)

9. **Check again.**
   Run Phase 4 only: `mechanical-validator` (`validate-proposal.py`), the `source-auditor` bind-check for any new citation, then `judgment-reviewer`. Add a `timeline` entry to `<slug>-checkpoint.json` for this task with its `session_id`. If a check fails, fix or restore from the backup and say so. Do not report done until the checks pass.

10. **Report** in the person's language: the run and its `web_url`, **the folder where the PDFs were saved and their file names**, what changed (sections, files), the validator result, the QA issues from step 5, and what you could not verify.

## Rules
- Never put the email, run links or any key into the proposal HTML. Never print or store API keys.
- Never send, email, or publish anything. This skill only writes files in the proposal folder.
- If the person's recording is in Vietnamese or Taglish, say that transcription quality for those has not been measured yet and the minutes need a human read before the client sees them.
- If a run needs a person (exit `2`), the work is paused, not failed.
