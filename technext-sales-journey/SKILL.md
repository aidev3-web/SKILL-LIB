---
name: technext-sales-journey
description: Builds a TechNext Sales Journey page for one lead (the 12-step sales playbook, a meeting kit with questions, objections and close checks, and follow-up messages) from the shared playbook. Claude researches the company and writes only JSON; bundled scripts check it and render the HTML page. Use when the user says "create a sales journey for <company>", "make a meeting kit for <company>", "update journey <slug>: <notes>", or in Vietnamese "tạo journey cho <công ty>", "cập nhật journey <slug>".
---
# TechNext Sales Journey for one lead

Claude writes data only: `intake.json`, facts, and `lead.json`. The scripts in this folder check that data and render the page.
Never hand-edit `journey.html`, `playbook/playbook.json` or `template/journey.html`.

## Paths and setup
- `<skill>` is the folder that holds this SKILL.md.
- `<leads>` is `~/sales-journey` (the `JOURNEY_LEADS` environment variable overrides it). Create it if it does not exist.
  Each lead lives in `<leads>/<slug>/`. A slug uses only a-z, 0-9 and `-`.
- Needs Node.js 18+ and Python 3. On Windows use `py` if `python` is not found.
- Quote paths that contain spaces. Run every command with full paths, from any folder.
- The two recipes, `<skill>/recipes/research.md` and `<skill>/recipes/kit.md`, are written in Vietnamese. Follow them exactly; they use the same `<skill>` and `<leads>`.
- Exit code 2 from a script means a setup problem (Node missing, files missing from `<skill>/tools/portal`), not bad lead data. Report it; do not change the lead to work around it.

## Create a sales journey for <company>
Ask nothing before you start, with one exception: if you do not know the user's first name (not in the request, not in `git config user.name`), ask for it once. It goes into the messages as the sales rep's name.

1. Write `<leads>/<slug>/intake.json`: `{"slug", "company", "website", "source", "owner", "sa", "contact_role", "notes"}`.
   - `owner` is the user's first name. `sa` is "Neil" unless the user names someone else.
   - `notes` is a short, filtered summary of what the user gave you. Remove every phone number and email address first.
2. Write the skeletons before any research:
   - `<leads>/<slug>/record.json`: `{"slug", "version": 0, "company": {"name", "short", "website", "country": "Philippines"}, "owner", "sa", "facts": [], "outputs": {}}`.
   - `<leads>/<slug>/lead.json`: every top-level key, `"version": 1`, `"playbook_version"` equal to `version` in `<skill>/playbook/playbook.json`, `"profile": {}`, `"vars": {}`, `"kit"` with all six blocks (`kyc`, `ask`, `qa`, `objections`, `close_checks`, `videos`) set to `[]`, `"versions": [{"ver": 1, "at": "<YYYY-MM-DD>", "by": "Claude", "reason": "New lead"}]` and `"runs": []`.
   - Do not write `profile` yourself: only `add-facts.mjs` writes it. Do not add a `demo` block.
3. Follow `<skill>/recipes/research.md`, then `<skill>/recipes/kit.md`. A complete example with made-up data: `<skill>/examples/lead-example.json`.
4. Check: `python "<skill>/tools/build.py" <slug> --check`. It prints `OK`, or the errors and exits 1 without writing anything. Fix the data once and check again; if it still fails, stop and show the errors.
   Only after `OK`, add to `runs[]`: `{"at", "recipes": {"research": 1, "kit": 1}, "sources": [...], "validate": "ok"}`.
5. Build: `python "<skill>/tools/build.py" <slug>`. It writes `<leads>/<slug>/journey.html`.
6. Share the page:
   - If you have a tool that publishes an HTML artifact, publish `journey.html` as a new artifact, then run `python "<skill>/tools/build.py" <slug> --url <artifact link>`. In `record.json` set `"outputs": {"journey": {"version": 1, "status": "published", "inputs": {"lead": <record.version>, "playbook": <playbook_version>}, "url": "<artifact link>"}}`.
   - Otherwise give the user the full path of `journey.html` to open in a browser, and set the same `outputs.journey` with `"status": "draft"` and no `url`.
7. Tell the user in a few lines: the link or file, the framework chosen (a, b or c) and the open questions in `kit.ask`.

## Update journey <slug>: <notes>
The user brings new information about a lead (meeting notes, a call, a transcript).
1. Turn the notes into facts in a temporary file outside `<leads>`: `[{key, value, grade, source: {kind, ref, at}, by}]`.
   - `key` is one of `industry`, `size`, `location`, `regulatory`, `risks`, `current_system`, `users`, `departments`, `client_words`, `next_step`, `decision_maker`, `modules`, `package`, `addons`. Drop anything that fits no key.
   - `grade` is `confirmed`; `source.kind` is `meeting` or `call`; `source.ref` names the session, for example "meeting 2026-11-05" (an `https://` URL or a plain label); `source.at` is the date; `by` is "Claude".
   - Remove every phone number and email address, in `value` and in `ref`.
   - `client_words` is the client's exact words. `current_system` is `manual`, `acct` or `erp`. `departments` is a list of `IT`, `Finance`, `Owner`, `Production`, `Sales`.
   - A fact that corrects an older one adds `"supersedes": "<old id, same key>"`. Never edit or delete old facts.
2. Run `node "<skill>/tools/add-facts.mjs" <slug> <facts file>`. It prints `{"version": n, "stale": [...]}`. Exit 1 means nothing was written: read the error, fix the facts (or `lead.json`), run again.
3. In `lead.json`: add 1 to `version` and append `{"ver", "at", "by": "Claude", "reason"}` to `versions[]`.
   - If `stale` contains `journey`: rebuild `vars` and `kit.kyc` from the current profile (steps 3–4 of `research.md`, no new web research), then redo the kit with `kit.md`. Set `outputs.journey.inputs.lead` in `record.json` to `n`.
   - Otherwise leave the kit alone; the reason is "new information".
   - In both cases set `outputs.journey.version` to the new `lead.json` version.
4. Run `python "<skill>/tools/build.py" <slug>`. Fields the rep never filled are pre-filled from the profile; what the rep typed, cleared or already sent stays as it is.
5. Publish again **on the same link**: take the slug's `url` from `<leads>/index.json` and update that artifact. Do not create a new one. With no artifact tool, give the file path again.

## Never
- State a fact without a source.
- Write prices or amounts of money.
- Greet by time of day ("Good morning").
- Store phone numbers or email addresses.
- Change the playbook or the template. Those changes come from Anthony or Neil and go through the source repo.
