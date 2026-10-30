---
name: technext-meeting-to-proposal
description: Send a meeting recording (video or audio) to TechNext's Minutes Studio over the office network, wait for the minutes, and write what the client said into an existing TechNext sales proposal (the Meeting Minutes section plus the related sections). Use when the user hands over a meeting recording file for a proposal they already have, says "gửi cuộc họp lên Minutes Studio", "cập nhật proposal từ cuộc họp", "đưa biên bản họp vào sales proposal", or offers a recording instead of pasted notes. ALSO use it when the notes are a link, not a recording, for example "cập nhật proposal từ link trong library", "đọc biên bản họp Google Docs", or the person pastes a Google Docs link to meeting notes or a quotation (path B, "Links from the library"). Does not build a proposal from nothing and does not email anything.
---

# Meeting recording → minutes → sales proposal

For **any TechNext user**. Nothing here belongs to one person: ask for the proposal folder, the person's email, and the server address every time they are not already known.

## Two input paths
- **A. A recording** (the default, steps 1 to 11 below): the recording goes to Minutes Studio.
- **B. Links from the library**: staff add links (a Google Docs meeting-notes link, quotation docs, other docs) to the client's card in the TechNext Proposal Library, or the person pastes such a link in chat. Follow "Path B" below; it reuses steps 7 to 11.
Ask which path if it is not clear. Path B needs no Minutes Studio address and sends nothing to Minutes Studio.

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
   **Follow-ups.** Once the minutes are fetched, also handle the `follow-ups` section (after `meeting-minutes`; owned by `tools-documents-agent`). If the proposal lacks it (older proposal), copy it from `assets/proposal-template.html` of `technext-sales-proposal` and list it as a new section in the approval list. Set `data-meeting-date="YYYY-MM-DD"` (the real meeting date from `--date`) on the `<section id="follow-ups">` tag, and replace the `[PLACEHOLDER ...]` draft texts (D0 thank you, D+1 summary, D+3 nudge, D+7 check-in, for WhatsApp, Viber and Email, with an email subject line) with drafts in the client's language built **only** from the minutes' decisions and action items: no invented commitment, price, date or promise, nothing the client did not say. Nothing is sent: the person copies each draft and ticks "Sent" themselves. The page computes the 4 planned dates: meeting date + 0, 1, 3 and 7 days, with Saturday and Sunday moved to Monday.
   Follow `checkpoint-manager` ("Section-level touch-ups"): one narrowly scoped `Agent` call per owning agent with the real template markup and `research-rules.md`. `meeting-minutes` is owned by `tools-documents-agent`. The bilingual markup contract is `assets/section-shell.md` (every string in `t-vi` and `t-en` spans). Patch `<slug>-proposal.html` **directly**, replacing only the approved `<section id="...">…</section>` blocks and leaving every other byte as it was. (The group draft files `p1-group*.html` are deleted when a proposal is finished, so the final file is the thing to edit. Keep a backup copy first, `<slug>-proposal.before-meeting.html`, and say where it is.)

9. **Check again.**
   Run Phase 4 only: `mechanical-validator` (`validate-proposal.py`), the `source-auditor` bind-check for any new citation, then `judgment-reviewer`. Add a `timeline` entry to `<slug>-checkpoint.json` for this task with its `session_id`. If a check fails, fix or restore from the backup and say so. Do not report done until the checks pass.

10. **Update the artifact and the library card** (only after step 9 passed). Run "Phase 5" of `technext-sales-proposal` (its `SKILL.md`): republish the same artifact (address in `<slug>-checkpoint.json` under `library.artifact_url`, so the link stays the same) and run `library_publish.py` of the `proposal-library-publish` skill, which updates the same card and its "updated" date. After a real client meeting ask the person whether the card status should become `followup`, and pass `--status followup` only if they say yes. Phase 5 follows the person's setting in `~/.claude/proposal-library.json` (`auto`, `ask` or `off`); it never fails this task, it only reports why it did not run. If the proposal has no library record yet, Phase 5 creates one. Pass `--meeting-date <YYYY-MM-DD>` and `--next-followup <YYYY-MM-DD>` to `library_publish.py`: the second is the planned date of the next follow-up that has not been sent yet (D0, D+1, D+3, D+7 in that order, weekend moved to Monday; right after the meeting it is the first one on or after today; ask the person which ones they already sent, because the Sent ticks live only in their browser). Leave it out if all four are sent.
    **Minutes and drafts on the card.** Once step 9 passed, build the card's meeting data: `python <proposal-library-publish skill folder>/library_publish.py extract-meeting "<proposal folder>" --minutes "<proposal folder>/captures/meeting-<YYYY-MM-DD>/minutes.json"` (add `--confirmed` only if the person says they read and confirm the minutes). It saves `<proposal folder>/captures/library-meeting.json`: the meeting date, input table and the draft texts come from the proposal's `follow-ups` and `meeting-minutes` sections (drafts still holding `[PLACEHOLDER` are skipped and reported), the summary, decisions and next steps come from `minutes.json`. Show the person what it holds, then pass `--meeting-file "<proposal folder>/captures/library-meeting.json"` to `library_publish.py`. **Say it plainly at the approval:** the library shows these minutes and drafted messages to all staff signed in to the library (internal, password-gated), not only to the proposal's owner; if they would rather not, run without `--meeting-file`. A file that fails validation stops with exit 2 and sends nothing: fix the reported field and rerun.

11. **Report** in the person's language: the run and its `web_url`, **the folder where the PDFs were saved and their file names**, what changed (sections, files), the validator result, the QA issues from step 5, the library result from step 10, and what you could not verify.

## Path B: Links from the library

Trigger: "cập nhật proposal từ link trong library", "đọc biên bản họp Google Docs", or the person pastes a Google Docs link to meeting notes or a quotation. Needs an existing proposal folder (same files as step 1 of path A), the library set up with a team key (`library-endpoint.json` of `proposal-library-publish`, or `PROPOSAL_LIBRARY_URL` / `PROPOSAL_LIBRARY_KEY`), and python 3. `LIB` below means `python <proposal-library-publish skill folder>/library_publish.py`.

B1. **List the links.** `LIB links <slug>` prints JSON `{slug, count, links:[{id, url, kind, label, added_by, added_at, used_at}]}` and only the links not yet used (`--all` shows used ones too). Or take links the person pasted in chat (these have no id, so there is nothing to mark afterwards). Show the list (kind, label, who added it, when) and **get a yes before reading any of them**. Exit 2 means a refusal with a one-line reason (no key, wrong key, unreachable, odd answer): show it and stop. If the library says it has **no card for that client yet**, say so and suggest running `technext-sales-proposal` first; do not create a card silently.

B2. **Read each approved link.** Only Google Docs links (`docs.google.com/document/d/<id>/...`) are read automatically; for any other link, tell the person and ask what to do, do not guess.
   - First try the **Google Drive connector**: `read_file_content` with the doc id from the URL.
   - If it says not found or no access (the doc may be shared with a different Google account), use **Claude in Chrome** on the person's own logged-in browser. Read only: navigate to the URL and `get_page_text`. Never request access, never edit, never click Share, never sign in for them. If the browser has no account that can open it, say so and stop for that link.
   - A Google Meet "Notes by Gemini" doc has tabs "Quick notes", "Full notes" and "Transcript". Read Quick notes and Full notes. Use the Transcript only to check names and quotes.
   - Save a capture `<proposal folder>/captures/meeting-<YYYY-MM-DD>/gdoc-<doc id>.md` (date: the meeting date if the doc states it, else today; say which). First line: `<!-- source: <url> | captured <date> | by <email> -->`, then the text read (tab names as headings). Same style as the other captures.

B3. **Record the facts, by kind.**
   - `minutes` (meeting notes): "Notes by Gemini" are **AI-generated notes**. A fact the client stated becomes `Confirmed — <meeting type>, <date> (Gemini notes)` **only when the notes attribute it to a named client person**. Anything unattributed, vague or machine-summarised stays "as heard / TBC". Check names, dates and weekdays against the Transcript tab and against what the person told you. Set `has_notes: true` in `<slug>-intake.json` (do not drop other keys) and write the facts into `<slug>-findings.json` as in step 6.
   - `quotation`: this is TechNext's **own** document. Its numbers may go into the Quotation section, shown with the quotation number and its validity date. Never change a number, never round, never add a line it does not have. If the doc has no number or validity date, say so and mark it TBC. Keep the brand rules of `research-rules.md` and `technext-sales-proposal/SKILL.md`: no "certified", no claim of BIR accreditation or any other accreditation the doc does not prove.
   - `document` (other): read it and use only what it plainly states, graded like a client-supplied document; if unsure how to grade, ask.
   Never invent a fact. A link that adds nothing usable is reported as such and left unused.

B3b. **Write the minutes record** (only when real meeting notes were read; path B has no Minutes Studio `minutes.json`). Write `<proposal folder>/captures/meeting-<YYYY-MM-DD>/minutes-record.json`, one JSON object in the library `minutes` shape: `date` (YYYY-MM-DD), `channel`, `signer`, `language`, `source`, `confirmed`, `summary`, `decisions`, `next_steps` (`[{what, who, due}]`). Rules: `source` is "Google Meet notes by Gemini" or "Google Doc"; `confirmed` is `false` unless the person says they read and confirm it; `summary` at most 2000 characters; `decisions` (each at most 300 characters, at most 20) and `next_steps` come **only from what the notes say**; `due` is a date only when the notes give a full date, otherwise `null`; leave out `channel`, `signer` or `language` when the notes do not say. Invent nothing.

B4. **Then reuse the existing steps:** list the changed sections **and show the `minutes-record.json`** in that approval list (step 7; the card shows it to all signed-in library staff), patch them with a backup (step 8; touch `meeting-minutes` and `follow-ups` only when real meeting notes were read, and the meeting date for `follow-ups` must be the real one), Phase 4 checks (step 9), then Phase 5 publish (step 10), building the card data with `extract-meeting "<proposal folder>" --minutes-record "<proposal folder>/captures/meeting-<YYYY-MM-DD>/minutes-record.json"` (instead of `--minutes`; add `--confirmed` only if the person confirms), then `--meeting-file` as in step 10. The follow-ups still come from the proposal HTML. An invalid record stops with exit 2: fix the reported field and rerun. Without a record the card gets no summary, decisions or next steps; do not make them up.

B5. **Mark the links used.** Only after the publish succeeded, and after asking ("mark these links as used?"): for each link that was **actually folded in**, run `LIB mark-link-used <slug> <id>` (`--dry-run` shows the request without sending). A link that was read but changed nothing, or that failed, stays unused. Links pasted in chat have no id and are not marked.

B6. **Report** as in step 11: which links were read and how (Drive connector or the browser), how the facts were graded, which sections changed, the validator result, the library result, which links were marked used, and what you could not verify.

## Rules
- Never put the email, run links or any key into the proposal HTML. Never print or store API keys.
- Never send or email anything. The only thing this skill publishes is the proposal's own artifact and library card, through Phase 5 of `technext-sales-proposal` (step 10), and it follows the person's `auto` / `ask` / `off` setting there. Everything else it does is write files in the proposal folder.
- If the person's recording is in Vietnamese or Taglish, say that transcription quality for those has not been measured yet and the minutes need a human read before the client sees them.
- If a run needs a person (exit `2`), the work is paused, not failed.
- Path B is read-only on Google: never request access, share, comment, edit or sign in. Never print or store the team key. The doc text goes only into the proposal folder's captures and the approved sections.
- Never mark a link used before the proposal was patched, checked and published, and never without asking.
