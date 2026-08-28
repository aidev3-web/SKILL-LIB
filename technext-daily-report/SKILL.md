---
name: technext-daily-report
description: Write Nguyễn Thành Trung's daily work report for TechNext Asia — a short, professional, bilingual (Vietnamese/English, toggle button) branded HTML report covering what he completed, what's in progress, blockers, and tomorrow's plan. Use this whenever Trung says he wants to write today's report, mentions "báo cáo ngày", "daily report", "viết báo cáo hôm nay", asks to summarize today's work into a report, or gives a rundown of what he did today expecting it turned into something sendable to his manager. Also use it to update/regenerate a report already in progress.
---

# TechNext daily report (concise, bilingual)

## What this is for

Trung reports to his manager (anthony@technext.asia) daily. This skill turns a quick rundown of what he did — messy notes, a spoken list, half-finished thoughts — into a short, clean, professional report in TechNext's brand style, with a working VI/EN language toggle so either he or his manager can read it in their preferred language. This skill only **writes the report file**. It does not send email or manage schedules — those are separate, deliberate steps Trung controls himself (or a separate automation asks him for).

## Reference template

`assets/report-template.html` is the exact, validated report format — read it before writing anything. Copy its structure, CSS, and scripts verbatim; only replace the content inside the four `<ul>` lists, the summary box, and the cover's date/meta fields. Do not modify the CSS, the scripts, or the overall page shell — they're already tested and working.

This is the "visually impressive" version of the report (v3): a gradient cover, four auto-computed KPI-style stat tiles, and each section rendered as a color-coded card with an icon, not a plain bulleted list. It replaced an earlier plainer version because Trung said the layout was fine but it read as too sparse — the structure below is deliberately richer, inspired by the visual-KPI / status-card / badge language of TechNext's own longer project reports (stat tiles, colored section headers, icon accents), just condensed to fit a short daily report.

Key structural facts about the template:

- **Logo is inline SVG, not an image file.** It's a small paper-plane icon plus a "Tech**Next**" wordmark, written directly as `<svg>` + text — deliberately not a base64-embedded raster image. Keep it that way; a raster logo bloats the file for no visual benefit and makes the file painful to move through tools (email attachments, Drive uploads, chat) reliably. Never re-introduce an `<img>`-based logo here. The same goes for every other icon in the template (stat tiles, section headers, the empty-state check) — they're all small inline `<svg>` outlines using `currentColor`, never emoji or raster images. If you add any new icon, keep it inline SVG in the same style.
- **Bilingual content pattern**: every piece of user-visible text is duplicated in two `<span>` elements, `class="t-vi"` for Vietnamese and `class="t-en"` for English, right next to each other. A tiny script + CSS rule (`body[data-lang="en"] .t-vi{display:none}` and the mirror rule) shows only the active language. When you write new content, you must always provide **both** the Vietnamese and English version of every sentence — the toggle button has nothing to show in the other language if you skip one.
- **Sections, in order**: cover (title, subtitle, meta: Người thực hiện/Reported by, Vị trí/Role, Ngày/Date) → a row of 4 stat tiles → a one-to-two-sentence summary box → four section cards — Đã hoàn thành/Completed, Đang thực hiện/In progress, Vướng mắc / cần hỗ trợ/Blockers, Kế hoạch ngày mai/Plan for tomorrow — each with a colored icon header and a `<ul>` of `<li>` bullets inside `.sect-body`.
- **Stat tiles are computed automatically, don't hand-edit their numbers.** The four tiles under the cover (Hoàn thành/Completed, Đang làm/In progress, Vướng mắc/Blockers, Kế hoạch/Planned) show a count. A script at the bottom of the page counts the real `<li>` items in each section (any `<li>` whose text still has the `placeholder` class is not counted) and fills the tile automatically on load. This means: **always remove the `placeholder` class from a span once you replace its bracketed text with real content** — if you leave the class on, that item silently won't be counted. You never need to type a number into the stat tiles yourself.
- **Blockers section has a built-in empty state.** If the Blockers list ends up with zero real (non-placeholder) items, the same script hides the empty `<ul>` and shows a small "Không có vướng mắc hôm nay / No blockers today" line with a checkmark instead — you don't need to write that yourself, just leave the placeholder `<li>` in place (with its `placeholder` classes) when there are no real blockers, exactly as before.
- **Two optional richer patterns exist in the CSS for when a plain bullet isn't enough** (Trung has asked for both at least once, so reach for them when they fit):
  - **Detailed progress line** (`.prog-title` / `.prog-row.done` / `.prog-row.need`) — use inside a `sect-progress` `<li>` when an in-progress item deserves more than one bullet: a bold title line, then a "Đã làm/Done so far" row and a "Cần/Needs" row, each with a small colored tag + bilingual `t-vi`/`t-en` text. Example shape for one `<li>`:
    ```html
    <li>
      <div class="prog-title"><span class="t-vi">Tên việc</span><span class="t-en">Task name</span></div>
      <div class="prog-row done"><span class="tag"><span class="t-vi">Đã làm</span><span class="t-en">Done</span></span><span class="txt"><span class="t-vi">...</span><span class="t-en">...</span></span></div>
      <div class="prog-row need"><span class="tag"><span class="t-vi">Cần</span><span class="t-en">Needs</span></span><span class="txt"><span class="t-vi">...</span><span class="t-en">...</span></span></div>
    </li>
    ```
    The tag itself must also use `t-vi`/`t-en` spans (as shown) — it's user-visible text like anything else, the toggle doesn't know to translate "Đã làm" → "Done" on its own.
  - **Workflow / roadmap** (`.roadmap` > `.road-step` with `.dot`/`.lbl`/`.sub`, connected by `.road-arrow` chevrons) — use in `sect-plan` when tomorrow's plan reads better as an ordered sequence of steps than a flat bullet list. Each `.road-step` is a gradient card with a numbered circle (`<div class="dot">1</div>`), a bold label, and an optional smaller subtitle, all bilingual; put a `.road-arrow` (a small inline chevron SVG — copy one from the template) between consecutive steps. It can replace the `<ul>` entirely, or sit alongside it — the stat-tile counting script counts `.road-step` elements as a fallback when a section's `<ul>` is empty, so either approach keeps the "Kế hoạch" tile's number accurate.
    - **Break the workflow down to the real remaining sub-steps, not just one vague "finish it" step.** When Trung says a workflow is what he wants, that means: take the "Cần/Needs" line from the matching `sect-progress` item and expand it into the actual sequence of concrete actions still left to do (3–5 steps is typical) — e.g. "needs to set up the automation" becomes create the schedule → write the self-contained prompt → run one manual test → confirm the send/save destinations all work. Don't pad with filler steps just to hit a count, but don't collapse a multi-part remaining task into a single step either.
    - Don't force a roadmap for a simple 1–2 item plan with no real sequence to it — plain bullets are fine there.
    - **If tomorrow's plan spans more than one distinct task/project, give each its own workflow — don't merge unrelated tasks into a single roadmap.** A shared roadmap implies the steps are sequential parts of *one* thing, which is misleading when they're actually two separate efforts running in parallel. Instead wrap each task's roadmap in its own `.plan-group`, with a `.plan-group-title` naming the task, one `plan-group` per task, stacked vertically:
      ```html
      <div class="plan-group">
        <div class="plan-group-title"><span class="t-vi">Tên việc/dự án</span><span class="t-en">Task/project name</span></div>
        <div class="roadmap"> ... road-steps for just this task ... </div>
      </div>
      <div class="plan-group">
        <div class="plan-group-title"><span class="t-vi">Việc khác</span><span class="t-en">Another task</span></div>
        <div class="roadmap"> ... road-steps for that other task ... </div>
      </div>
      ```
      This pairs naturally with the "Đang thực hiện" detail pattern above: each in-progress task's "Cần/Needs" row is usually exactly what tomorrow's mini-workflow for that same task should walk through.

## Writing the content

1. **Get today's rundown.** If Trung hasn't already described what he did, ask him — plainly, "hôm nay bạn đã làm gì?" It's fine if his answer is unstructured; sort it out yourself. Ask if he has any screenshots/images he wants referenced (see below for how to handle those).
2. **Sort into the four buckets**: finished work (with concrete results/numbers when he gives them), work still in progress (with current status), genuine blockers or things he needs help with (leave the placeholder `<li>` as-is if there are none — don't invent a blocker to fill space, and don't strip its `placeholder` class since that's what triggers the "no blockers" empty state), and what he plans to do next. For every real item you write, replace both the `t-vi` and `t-en` bracketed text **and** remove `class="placeholder"` from both spans — the stat-tile counts depend on that.
3. **Write the one-line summary** at the top: the single most important thing that happened today, not a recap of everything.
4. **Translate faithfully, not literally** — write natural English for the `t-en` spans, not a word-for-word gloss of the Vietnamese. Keep both versions equally concise.
5. **Images**: if Trung shares a screenshot, you can note its relevance in the relevant bullet's text (e.g. "kèm ảnh chụp log lỗi"), but don't try to embed an image inline as base64 in the body — that reintroduces the large-file problem the SVG-logo change was meant to avoid. If an image genuinely needs to be in the report, attach it as a separate file alongside the HTML rather than inlining it, and say so.
6. **Date fields**: use today's actual date for the `<title>`, the `<h1>` (both `Báo cáo ngày DD/MM/YYYY` and `Daily Report — MM/DD/YYYY`), and the meta grid's Ngày/Date field.

## Naming and saving

Name the file `report_DD-MM-YYYY_NguyenThanhTrung.html` (dashes between day/month/year — this is Trung's actual convention, confirmed from his existing files; do not drop the dashes).

Trung currently keeps copies in three places. Save to whichever of these are reachable in the current session — don't fail the whole task if one is unavailable, just note which ones you skipped and why:

- **Local folder**: a dated subfolder named `MM-DD-YYYY` (note: month-day-year here, unlike the dashes-in-filename which are day-month-year) inside his `reports` folder on his computer, e.g. `reports/08-19-2026/report_19-08-2026_NguyenThanhTrung.html`. Requires the device folder connection to his `reports` folder — request it if not already connected.
- **Google Drive**: the `AITechNext` folder inside `ThucTapDoanhNghiep` (folder ID `1n4ODPByUOST6MMVivxPQmJhbKF5gWfgf` as of this writing — if that ID no longer resolves, search Drive for a folder named `AITechNext` rather than guessing). When creating the file via the Drive connector, pass the HTML as `textContent` with `contentMimeType: text/html` and `disableConversionToGoogleType: true` — the file is small (a few KB, thanks to the SVG logo) so this works cleanly in one call.
- **This conversation**: always deliver the finished file so Trung can see and download it directly, regardless of whether the other two saves succeeded.

Do not send or draft any email as part of this skill, and don't ask to send one — report-writing and report-sending are deliberately separate. If Trung asks you to also email it, that's a normal action you can do in the moment (with his explicit go-ahead before actually sending, per standard policy), just not something this skill does automatically.

## Judgment calls

If what Trung describes is too thin for a real report (e.g. "hôm nay nghỉ, không làm gì"), say so rather than padding it out — a short honest report beats an invented one. If he corrects something after seeing the draft, apply the fix and don't re-litigate the rest of the report.
