---
name: technext-morning-plan
description: Build Nguyễn Thành Trung's morning work plan for TechNext Asia by reading yesterday's daily report from BOTH his local reports folder and Google Drive, cross-checking the two copies, and producing a bilingual (Vietnamese/English) branded HTML plan with a tickable progress checklist for today. Use this whenever Trung asks what he should do today, says "lên plan", "kế hoạch hôm nay", "morning plan", "hôm nay làm gì", "task hôm nay là gì", asks to pick up where yesterday's report left off, or asks to check today's progress against a plan. Also use it when a scheduled morning task fires asking for the daily plan. This is the morning counterpart to the technext-daily-report skill — that one writes the evening report, this one turns the previous report into today's plan and checklist.
---

# TechNext morning plan (bilingual, checklist-driven)

## What this is for

Trung writes a daily report every evening (see the `technext-daily-report` skill). That report already contains the two things a good morning plan needs: what was left unfinished ("Đang thực hiện" with its "Cần / Needs" lines) and what he intended to do next ("Kế hoạch ngày mai"). This skill closes that loop — it reads yesterday's report back, turns the intentions into a concrete plan laid out across the day, and gives him a checklist granular enough that he can see his own progress moving during the day instead of only discovering it at 18:30 when the report is due.

Two copies of every report exist (one on his computer, one on Drive) because the report skill saves to both. Reading both and comparing them is deliberate, not paranoid: if the two ever drift apart, one of the save steps silently failed, and planning off a stale copy would quietly drop work. Better to notice at 9am than a week later.

This skill only **builds the plan file**. It does not send email and does not write the evening report.

## Reference template

`assets/plan-template.html` is the exact, validated output format — read it before writing anything. Copy its structure, CSS, and script verbatim; replace only the content inside the placeholder spans. The CSS and script are tested and working — leave them alone.

It deliberately matches the daily report's visual language (same brand colors, same gradient cover, same inline-SVG logo, same VI/EN toggle) so the plan and the report read as one system. Structural facts worth knowing before editing it:

- **Bilingual pattern**: every user-visible string is duplicated in `<span class="t-vi">` and `<span class="t-en">` siblings, with a script + CSS pair showing only the active language. Write **both** versions of every sentence — the toggle has nothing to show otherwise. Translate faithfully into natural English, not word-for-word.
- **Placeholders drive the logic**: a span with `class="placeholder"` means "not filled in". The script uses that class to decide what to count and what to hide. So when you replace bracketed text with real content, **remove `placeholder` from both the `t-vi` and `t-en` span**. Leave it in place on any block you want hidden — that's how the mismatch warning box and the carry-over section disappear when they're not needed.
- **Stat tiles and progress bars are computed, never hand-typed.** The script counts real (non-placeholder) task cards and checkboxes, then updates the four tiles, each task's percentage bar, and the overall bar — live, as boxes get ticked. Do not type numbers into them.
- **Icons are inline SVG outlines** using `currentColor`, never emoji or raster images. Keep any new icon in that style; it keeps the file a few KB so it moves cleanly through email, Drive, and chat.
- **Checkbox state is in-memory on purpose** (no browser storage). Ticks are a within-the-day working aid; the durable record of what got done is the evening report. The template already tells the reader that reloading clears the ticks — don't add storage.
- All icons are inline SVG; no external assets, so the file works offline and as an email attachment.

## Step 1 — work out which report to read

Today's date sets everything. "Yesterday's report" means **the most recent working day's report**, not literally yesterday's calendar date: on a Monday, that's Friday's report; after a holiday or a day off, it's the last day he actually worked. Reports are only written on working days, so walk backwards from today until a report turns up (give up after about 5 days back and say so rather than guessing).

Two naming conventions are in play, and they use **different date orders** — this trips people up, so check twice:

- Folder on his computer: `reports/MM-DD-YYYY/` (month-day-year), e.g. `reports/08-19-2026/`
- File name inside it: `report_DD-MM-YYYY_NguyenThanhTrung.html` (day-month-year), e.g. `report_19-08-2026_NguyenThanhTrung.html`

The local reports root is `C:\Users\nguye\OneDrive\Máy tính\AITechNext.asia\reports` (request folder access if it isn't connected yet). A dated folder may hold **several variants** — `report_19-08-2026_NguyenThanhTrung.html`, `..._1.html`, `..._2.html` — from revisions during the evening. The highest-numbered / most recently modified file is the final version, so use that one and mention which file you read; the plan is only as good as its source, so being explicit about the source is part of the output.

## Step 2 — read both copies and compare them

Read the local copy, then look for the same report on Google Drive in the `AITechNext` folder inside `ThucTapDoanhNghiep` (folder ID `1n4ODPByUOST6MMVivxPQmJhbKF5gWfgf`; if that ID no longer resolves, search Drive for a folder named `AITechNext` rather than guessing).

Compare the two **by meaning, not byte-for-byte**. Whitespace, attribute order, or a re-exported file will differ harmlessly; what matters is whether the four content buckets agree — Đã hoàn thành, Đang thực hiện (including each item's Done/Needs lines), Vướng mắc, Kế hoạch ngày mai. Differences worth reporting look like: a task present in one copy and absent in the other, a different status or "Needs" line for the same task, or a different plan for today.

Then fill the source-check strip at the top of the plan honestly, in one of three states:

- **Both found and they agree** → both `.src-item` rows marked found, badge `match` ("2 bản khớp nhau"), and leave the mismatch box's `<li>` as a placeholder so it stays hidden.
- **Both found but they differ** → badge `diff`, and fill the mismatch box with one bullet per real difference, naming which copy has what. Then **still build the plan** — Trung's call: use the newer copy (later modification time; if that's unclear, the local one, since that's where the report skill writes first) as the basis and carry on. A plan with a flagged caveat is more useful at 9am than no plan.
- **Only one copy reachable** (Drive permission declined, device offline, file missing on one side) → mark the missing row `miss` by swapping its check icon for a neutral dash and adding `class="src-item miss"`, badge `single`, and note in one line which source was skipped and why. This is normal, not a failure — proceed with the copy you have.

Do not block on the unreachable source. This skill often runs unattended at 9am with nobody around to grant a permission prompt, so a missing source is a footnote in the output, not a reason to stop.

**The local folder is normally unreachable on a scheduled run, and that is expected.** A scheduled morning task runs in a cloud session that has no bridge to Trung's laptop at all — not a permissions problem, just what that kind of session is. So the realistic split is: a scheduled 9am run is **Drive-only** and should say so calmly (badge `single`, one line naming Drive as the only source read), while a run Trung starts himself from Claude Desktop can reach both and does the real cross-check. Never report the missing laptop copy as a failure or a discrepancy on a scheduled run — there is no second copy to disagree with, and phrasing it as an error trains him to ignore a warning that fires every single morning. Save the `diff` badge for a genuine content difference between two copies you actually read.

A consequence worth keeping in mind: on Drive-only mornings, the Drive copy is the *entire* basis for the plan. If it looks wrong — placeholder text still in it, suspiciously small, an older layout than the report skill currently produces, or a filename that breaks the `report_DD-MM-YYYY_...` convention — say so prominently instead of planning off it. A blank or stale Drive copy means the evening report's upload step failed, and that is worth interrupting the morning for; building a confident-looking plan on top of an empty report is the worst possible outcome.

## Step 3 — build today's plan

The raw material, in order of importance:

1. **Yesterday's "Kế hoạch ngày mai"** — his own stated intention for today. This is the backbone; don't quietly replace it with your own idea of what he should do.
2. **The "Cần / Needs" line of each in-progress item** — the concrete remaining work, and usually the best source of checklist steps.
3. **Yesterday's blockers** — anything unresolved still needs a slot, or at least a step to chase the person who can unblock it.
4. **Anything finished yesterday** — mostly to *avoid* re-planning it. If a task appears in Đã hoàn thành, it's done; don't resurrect it.

Then lay the work across the day. Two sessions (Buổi sáng ~09:00–12:00, Buổi chiều ~13:30–17:30) is the right granularity — enough structure to be useful, not so much that a 20-minute overrun invalidates the plan. Sequence with judgment rather than a fixed rule, and write the reason into each session's `.sess-note`, because the reason is what lets him deviate intelligently when the day doesn't cooperate:

- Work that is nearly finished usually belongs in the morning — finishing it clears it off the list and off his mind, and half-done work left overnight tends to cost re-learning time.
- Work needing deep focus or a big uninterrupted block belongs where his day actually has that block; if that's the morning, put the nearly-finished item second rather than fighting over the same slot.
- Anything whose next step depends on a result from earlier in the day has to come after it — a decision that can't be made until a prototype runs is an afternoon item by nature.
- Leave the last part of the afternoon lighter. The evening report has to get written, and a plan packed to 17:30 is a plan that gets abandoned at 16:00.

If two genuinely separate projects are in play, keep them visibly separate rather than blending them into one narrative — mixing them makes it look like one thing with many steps, which misrepresents how the day will actually feel.

Also write the **Trọng tâm hôm nay** box: one or two sentences naming the single most important thing to push through today and why. Not a recap of the plan — the plan is right below it. If everything on the list is equally routine, say that plainly instead of inflating something into a priority.

The **Chuyển tiếp từ hôm qua** section is where the linkage to yesterday shows: one bullet per unfinished item, with its status on the first line and its "Cần" line as the smaller `.cf` sub-line. If genuinely nothing carried over (everything closed out yesterday), leave those placeholders in place — the section hides itself.

## Step 4 — build the checklist

This is the part Trung specifically asked for, so it deserves care. One `.task-card` per task or project; inside it, the real remaining sub-steps as checkboxes.

What makes a checklist step good:

- **Concrete enough to tick.** "Dựng thử module WhatsApp trên bản Community" can be finished and ticked; "làm việc với Odoo" cannot. If a step can't be judged done, it won't get ticked and the progress bar becomes decoration.
- **Roughly 3–5 steps per task.** That's usually what a real "Cần / Needs" line expands to. Fewer and the bar jumps in useless leaps; many more and ticking becomes bookkeeping. Don't pad to hit a number, and don't collapse a genuinely multi-part task into one step either — a task with a single checkbox tells him nothing during the day.
- **Ordered the way he'll actually do them**, so the checklist doubles as a sequence and he doesn't have to re-derive the order.

Expand each "Cần" line into its real sub-steps. For example, "cần tạo lịch chạy tự động và test thử" isn't one step — it's: write the self-contained prompt → create the schedule → run one manual test → confirm the save/send destinations work. That expansion is the whole value of the checklist; a checklist that just restates the report's bullets adds nothing.

Include a step for writing the evening report if that's part of the day. It's real work, it's easy to forget at 17:30, and ticking it is how the day actually closes.

## Naming and saving

Name the file `plan_DD-MM-YYYY_NguyenThanhTrung.html` — day-month-year, matching the report file convention (`report_DD-MM-YYYY_...`) so the two sort together in the same folder.

Save to whichever destinations are reachable, and don't fail the whole task over one that isn't — just note which you skipped and why:

- **Local folder**: today's dated subfolder `MM-DD-YYYY` (month-day-year) inside his `reports` folder, e.g. `reports/08-20-2026/plan_20-08-2026_NguyenThanhTrung.html`. Create the folder if today's doesn't exist yet. Keeping the plan next to the day's report means one folder holds the whole day.
- **Google Drive**: the `AITechNext` folder (see Step 2 for the ID). Pass the HTML as `textContent` with `contentMimeType: text/html` and `disableConversionToGoogleType: true` — the file is a few KB, so one call is enough.
- **This conversation**: always deliver the finished file so he can open, read, and tick it immediately, regardless of whether the other saves worked.

Don't send or draft email here. Planning and sending are separate; if he asks for an email, that's a normal request to handle in the moment with his explicit go-ahead, not something this skill does on its own.

## Judgment calls

**When it runs unattended.** At 9am on a schedule there may be nobody to answer a question. Make the most reasonable call, state the assumption in one line at the top of your reply, and produce the plan. Don't stall waiting for input.

**When yesterday's plan was "nghỉ" / a day off.** Then there is no stated intention to work from. Fall back to the still-open "Cần" lines and blockers from the last real working day, and say plainly that you're doing so. Don't invent tasks to fill the page.

**When no report can be found at all.** Say so directly and ask what he's working on, rather than producing a plausible-looking plan built on nothing. A wrong plan costs more than a missing one.

**When the report is thin.** A one-line report yields a short plan. That's the honest output — a two-item checklist that matches reality beats eight invented steps.

**After he sees it.** If he corrects something, fix that and leave the rest alone; don't re-argue the plan he just adjusted.
