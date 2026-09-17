---
name: ba-skill
description: Turn a user scenario into exactly ONE self-contained HTML business-analysis report with a working VI/EN language toggle AND a separate dark/light theme toggle — a project overview table (AS-IS, TO-BE, actors, fully-spelled-out FR/NFR with no unexplained abbreviations, main use cases), one BPMN-style process diagram with its SVG inlined directly into the report (no second file, every diagram label bilingual and toggle-driven, not hardcoded to one language), and an Epic → Feature → User Story → Task → Subtask backlog table, styled as an austere technical playbook (serif body, uppercase mono labels, pill badges, no dashboard chrome). Use when the user pastes or describes a user scenario / kịch bản người dùng and asks for requirements analysis, an AS-IS/TO-BE writeup, a BPMN diagram, or a full backlog breakdown from a feature idea. Trigger phrases include "phân tích nghiệp vụ", "kịch bản người dùng", "AS-IS TO-BE", "vẽ BPMN", "phân rã Epic", "from requirements to backlog", "báo cáo BA".
---

# BA Skill — scenario in, one HTML report out

Turns one input — a user scenario — into three deliverables, assembled into a single
self-contained HTML report — **one file, nothing to send alongside it** — in a fixed
order: **Table 1** (project overview: AS-IS/TO-BE/actors/FR/NFR/use cases) → **one
BPMN-style diagram** (drawn by the `diagram-design` skill, its SVG inlined directly
into the report) → **Table 2** (Epic → Feature → User Story → Task → Subtask). The
whole report has a working VI/EN toggle.

This is a custom skill built by combining three real sources, kept honest about which
part comes from where — see **Credits** at the bottom. Nothing here should be taken as
those projects' own documentation.

## Input

**Works best with:** a user scenario (kịch bản người dùng) — a short narrative of who
does what today, e.g. *"Bệnh nhân gọi điện đặt lịch khám, lễ tân ghi sổ giấy, gọi lại
xác nhận, hôm sau gọi nhắc"*. Vietnamese or English, either is fine — the tables below
are always written in both.

**Arriving thin?** ("thêm tính năng đặt lịch cho phòng khám", no process detail) — ask
the two or three questions that unblock Table 1 (who are the actors today, what
triggers the process, what breaks) rather than inventing an AS-IS that was never
described. Don't stall on questions that don't change the outcome — see Judgment calls.

## Phase 1 — Discovery (from `business-analyst`'s checklist)

Before writing anything, make sure you actually have:
- **Actors** — who touches this process today (borrowed directly from
  `business-analyst`'s "Stakeholder identification" + "Process mapping" discovery
  priorities).
- **AS-IS** — the current process, step by step, in the order it really happens, not
  the order it should happen.
- **Pain points** — where it breaks (manual step, no data, single point of failure).
- **TO-BE intent** — what the user scenario implies should change.

If the scenario already contains all four, skip straight to Table 1. If any is missing,
ask — one question per gap, not a questionnaire.

## Phase 2 — Table 1: Project Overview, as three separate tables

Splitting AS-IS/TO-BE, Actors, and everything else into three tables — instead of one
table with a row per field — is deliberate: a comparison reads left-to-right per row,
not buried inside one wide "AS-IS" cell next to one wide "TO-BE" cell three rows apart.

### Table 1A — AS-IS vs TO-BE (side by side, one row per comparable step)

| # | AS-IS | TO-BE | Thay đổi / Change |
|---|---|---|---|
| 1 | <bước hiện tại> | <bước tương ứng, hoặc "—" nếu bước này biến mất> | pill: MỚI / THAY ĐỔI / LOẠI BỎ |

Build it so each row is a real comparison, not two independent lists stapled together:
- Walk the AS-IS steps in order; for each one, put what replaces it in the TO-BE
  column on the same row (`.pill.warn` "THAY ĐỔI / CHANGED" if it's the same step done
  differently, `.pill.bad` "LOẠI BỎ / REMOVED" if TO-BE simply drops it — leave that
  cell "—").
- Any TO-BE step with no AS-IS counterpart (OTP confirmation, automatic reminders —
  things that didn't exist before) gets its own row, AS-IS column "—", `.pill.ok`
  "MỚI / NEW".
- This table **is** the traceability source for FR: every "THAY ĐỔI" or "MỚI" row is
  where an FR comes from in Table 1C. If a row has no pill and no visible change,
  question whether it belongs in the table at all.

### Table 1B — Actors & Actions

| Actor | Hành động chính / Main actions |
|---|---|
| <tên actor> | <danh sách hành động, mỗi hành động 1 dòng, dùng động từ rõ ràng> |

One row per actor, not one paragraph per actor buried in a wider table — this is a
scan target ("who does what"), so keep each action short (verb + object) and let a
reader find an actor's row in under two seconds.

### Table 1C — Requirements & Use Cases

| Trường / Field | Nội dung |
|---|---|
| Tên dự án / Project name | — |
| FR (Functional Requirements) | Đánh số FR1, FR2... — mỗi FR trỏ về đúng 1 dòng "MỚI"/"THAY ĐỔI" ở Bảng 1A |
| NFR (Non-Functional Requirements) | Hiệu năng, bảo mật, khả dụng — chỉ ghi cái TO-BE thực sự đòi hỏi, không liệt kê cho đủ |
| Use case chính / Main use cases | 3–6 use case tên theo mẫu "Actor + động từ + đối tượng" |

**How FR/NFR get derived, not invented:** every FR traces back to a specific "MỚI" or
"THAY ĐỔI" row in Table 1A — that pill is what makes a requirement real instead of
invented. A pain point that says "lễ tân quên nhắc" becomes the "MỚI" row "Hệ thống tự
động gửi nhắc lịch trước 24h và 2h" in Table 1A, and FR text in Table 1C cites that
row. This is the same traceability principle `business-analyst`'s checklist calls out
("Requirements traceability 100% maintained"). If a requirement doesn't trace to a
pilled row in Table 1A, cut it.

**Write FR/NFR out in full — no abbreviations a stranger wouldn't recognize.** Each
FR/NFR is a complete sentence a reader outside this project can understand with no
extra context: "Hệ thống xác thực người dùng bằng mã dùng một lần gửi qua tin nhắn
SMS, có hiệu lực 5 phút" — not "Auth via OTP, TTL 5m." Spell out every acronym on
first use inside the table, even ones that feel obvious in the domain (EMR → "hệ thống
quản lý hồ sơ bệnh án (EMR)", NFR → don't just say "NFR3: <90s" — say what response,
under what condition, in what unit). If a term must stay short for space, define it
once in the FR/NFR field's own text, not by assuming the reader already knows the
project's shorthand.

## Phase 3 — The BPMN-style diagram

### Step 3a — sketch it in ASCII first, always

Before calling `diagram-design`, draw the swimlane as **plain-text ASCII art** — boxes
and arrows, one lane per row band, laid out left-to-right in the order steps actually
happen. This is not optional and not thrown away: it's where every connector's source,
target, and direction gets decided and checked *before* any SVG exists, which is what
keeps arrows from crossing, doubling back, or pointing at the wrong node once
`diagram-design` renders them for real.

**This step has been skipped in practice** — a run of this skill went straight to SVG
and only admitted skipping it when asked directly. Skipping it is not a shortcut that
happens to work; it just means nobody checked the routing before rendering, and the
next scenario might not be as forgiving as the last one. The Pre-delivery checklist at
the end of Phase 5 requires pasting this actual sketch into your reply — if you reach
that checklist with no real sketch to paste, this step did not happen and the run is
not done yet.

**Use real BPMN shape vocabulary, not one box shape for everything.** A plain
rectangle for both "an activity happens" and "a decision splits the flow" is exactly
what makes a diagram unreadable — a reader can't tell a step from a fork at a glance.
Four shapes, each meaning one specific thing:

| Shape | Name (VI / EN) | Draws as | Meaning |
|---|---|---|---|
| ○ | Sự kiện bắt đầu / Start event | thin-line circle | where the process is triggered — one per diagram, usually leftmost |
| ◎ | Sự kiện kết thúc / End event | thick-line circle | where the process ends — can be more than one (success end, reject end...) |
| ▭ (rounded) | Hoạt động / Activity, Task | rounded rectangle | one actor or the system does one concrete thing — this is what most nodes are |
| ◇ | Cổng loại trừ / Exclusive gateway (XOR) | diamond, **empty or marked ×** | the flow splits and **exactly one** outgoing path is taken, chosen by a condition — label every outgoing arrow with its condition ("OTP đúng" / "OTP sai") |
| ◈ | Cổng song song / Parallel gateway (AND) | diamond, **marked +** | the flow splits and **every** outgoing path runs at once, no condition needed (e.g. "gửi SMS" and "ghi log" both happen from the same point) |

A gateway is not optional decoration — if the ASCII sketch has a branch (two arrows
leaving one point with different conditions, or one point that fans out into parallel
work), that point **must** be a diamond, not a rectangle with two arrows leaving it.
Rectangles never branch; only gateways do.

Example shape (lane label top-left in small caps; a real Exclusive Gateway shown
where the flow actually decides something — OTP correct or not — not just a rounded
box with two outgoing arrows; a Parallel Gateway shown where two things happen at
once; one highlighted "money step" activity; optional/exception paths drawn with a
dashed box + dashed arrow; a legend row at the bottom naming every shape used, not
just color):

```
 LANE                                        ◇──cond:sai──▶┌──────────┐  ┄┄┄┄┄┄┄┄┄┐
 Bệnh nhân   ○──▶┌───────────────┐        ┌─────────────┐  │Nhập lại  │            ┊ Huỷ/đổi
                 │ Chọn chuyên   │───────▶│ Chọn giờ &  │─▶│OTP đúng? │            ┊ (tuỳ chọn)┊
                 │ khoa & bác sĩ │        │ xác nhận OTP│  │cond:đúng │            ┄┄┄┄┄┄┄┄┄┄┄┄┘
                 └───────────────┘        └──────┬──────┘  └────┬─────┘
                                                  │ xác nhận       │ OTP đúng
 ─────────────────────────────────────────────────┼────────────────┼──────────────────
 LANE                                    ┌────────▼───────┐  ┌─────▼──────┐
 Hệ thống      ┌───────────────┐         │ Hiển thị       │  │ Xác thực   │
                │ Kiểm tra slot│◀────────│ khung giờ      │  │ OTP, khoá  │──▶◈(+)──┬──▶ ghi log
                │ còn trống    │  real   │ trống          │  │ slot       │        │
                └───────────────┘  time  └────────────────┘  └────────────┘        └──▶ gửi SMS xác nhận
 ─────────────────────────────────────────────────┼──────────────────────────────────
 LANE                                              │ sinh
 Lễ tân                                     ┌───────▼───────┐   ┄┄┄┄┄┄┄┄┄┄┄┐
                                            │ Xem lịch trong │   ┊ Hỗ trợ    ┊
                                            │ ngày           │   ┊ ngoại lệ  ┊
                                            └────────┬───────┘   ┄┄┄┄┄┄┄┄┄┄┄┘
                                                     ▼
                                                     ◎

 LEGEND   ○ Bắt đầu   ◎ Kết thúc   ▭ Hoạt động   ◇ Cổng loại trừ (1 nhánh)
          ◈+ Cổng song song (mọi nhánh)   ▣ Bước lõi (highlight)   ┄ Nhánh tuỳ chọn/ngoại lệ
```

Check the sketch against these before moving on: every arrow has exactly one source
and one target node (no arrow trailing off into nothing), no two arrows cross inside a
lane if a re-route avoids it, every optional/exception path is visibly dashed, and
every point where the flow actually branches or forks is a diamond gateway, not a
rectangle with multiple arrows leaving it.

### Step 3b — hand the sketch to `diagram-design`, in both languages

The diagram must switch language with the same VI/EN toggle as the rest of the report
(see Phase 5) — it is not allowed to stay stuck in one language while every table
around it swaps. Draw the labels for **both languages up front**, not English-only and
not Vietnamese-only:

> "Draw a **swimlane** (or **process**, if there's only one actor lane) diagram of this
> TO-BE flow — nodes, lanes, and connectors exactly as sketched: [paste the ASCII
> sketch]. Use real BPMN notation: rounded rectangles for activities, diamonds for
> gateways (draw the exclusive/XOR gateway plain or with a × mark, the parallel/AND
> gateway with a + mark — never render a branch point as a rectangle), circles for
> start/end events. Highlight [the core step] as the key business action; draw [the
> optional/exception steps] as dashed. Label every lane and every node in **both
> Vietnamese and English** (two short labels per node, not one translated gloss in
> parentheses). Include a legend explaining every shape used (event/activity/gateway
> type), not just the highlight color. Detail: balanced. Format: html."

Three things to get right before calling it:
- **Every branch point is a gateway diamond, not a rectangle with two arrows out of
  it.** If your ASCII sketch has a rectangle that splits into two or more paths, that
  is the sketch telling you a gateway belongs there — fix the sketch before sending
  it, don't let `diagram-design` (or yourself) improvise the shape at render time.
- **Pick swimlane over process when ≥2 actors hand off work to each other** —
  `diagram-design`'s own spec draws this distinction ("Cross-functional process with
  handoffs" vs "Multi-actor sequential process with data handoffs"); a single-actor
  TO-BE doesn't need lanes.
- **If TO-BE has more than ~9 steps**, say so before calling it and ask for an
  overview + detail split — `diagram-design` enforces a density target itself
  (complexity budget, "above 9 nodes, split into overview + detail"), so a big TO-BE
  handed over without warning gets silently split in a way you didn't plan for. Fold
  steps in the ASCII sketch first so the sketch itself already respects the budget.

The result is inline SVG markup (self-contained, no CDN) — **keep it as markup, don't
save it to its own `.html` file.** Phase 5 pastes this SVG directly into the report;
the whole point of Phase 5 is that nothing gets sent as a second file.

## Phase 4 — Table 2: Epic → Feature → User Story → Task → Subtask

**Not a single flat 5-column table.** A flat table with one row per Subtask and
`rowspan` merging Epic/Feature/Story cells looks fine with short text, but once AC
text wraps to 4-6 lines, the merged cell drifts visually away from the row it belongs
to — a reader can no longer tell which Subtask sits under which Epic. This is a real,
observed failure, not a hypothetical: a wide rowspan table with long wrapped cells is
the wrong shape for this content.

Use **nested sections instead of one grid** — one block per Epic, headings carry the
grouping instead of merged cells:

```html
<section class="epic-block">
  <h3><span class="pill sea">EPIC-1</span>
    <span class="t-vi">...tên Epic...</span><span class="t-en">...Epic name...</span></h3>

  <div class="feature-block">
    <h4><span class="t-vi">Feature: ...</span><span class="t-en">Feature: ...</span></h4>

    <div class="story-card">
      <p class="story-text">
        <b>US1.1</b> —
        <span class="t-vi">Là &lt;actor&gt;, tôi muốn...</span>
        <span class="t-en">As a &lt;actor&gt;, I want...</span>
        <span class="pill warn">FR2, FR3</span>
      </p>
      <ul class="ac-list">
        <li><span class="t-vi">AC: Given..., When..., Then...</span><span class="t-en">AC: Given..., When..., Then...</span></li>
      </ul>
      <table class="task-table">
        <thead><tr>
          <th><span class="t-vi">Task</span><span class="t-en">Task</span></th>
          <th><span class="t-vi">Subtask</span><span class="t-en">Subtask</span></th>
        </tr></thead>
        <tbody>
          <tr>
            <td><span class="t-vi">...</span><span class="t-en">...</span></td>
            <td><ul>
              <li><span class="t-vi">...</span><span class="t-en">...</span></li>
            </ul></td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- one .story-card per User Story in this Feature -->
  </div>
  <!-- one .feature-block per Feature in this Epic -->
</section>
<!-- one .epic-block per Epic — no table spans this whole section -->
```

Add these tokens to the CSS block from Phase 5 (same palette, no new colors):

```css
.epic-block{margin:28px 0;padding-top:20px;border-top:2px solid var(--ink)}
.epic-block h3{display:flex;align-items:center;gap:10px;font-size:19px;margin:0 0 14px}
.feature-block{margin:16px 0 16px 4px;padding-left:16px;border-left:2px solid var(--line)}
.feature-block h4{font-family:var(--display);font-size:14px;color:var(--ink-2);margin:0 0 10px}
.story-card{margin:0 0 20px}
.story-text{margin:0 0 6px}
.ac-list{margin:0 0 10px;padding-left:20px;font-size:14px;color:var(--ink-2)}
.task-table{width:100%;font-size:13.5px}
.task-table ul{margin:0;padding-left:16px}
```

This drops `rowspan` entirely — grouping is now the DOM structure (a Subtask is
visually inside its Task's row, inside its Story's card, inside its Feature's block,
inside its Epic's section), not a merged cell that can drift from its row.

Build the content top-down, each level with its own real method — not the same
technique stretched across five levels:

**Epic** — one per main use case from Table 1. Name it as a business outcome, not a
feature list item.

**Feature** — group the FRs from Table 1 that serve one Epic. A Feature is "what the
system does"; keep it at that altitude, don't write user stories yet.

**User Story** — this is where a Feature gets *split*, and it's the one step with a
real, named method (from `epic-breakdown-advisor` + `user-story-splitting`, both built
on Richard Lawrence's Humanizing Work patterns):

1. **INVEST pre-check first.** Before splitting a Feature into stories, check it's
   *Valuable* — does it deliver observable value to an actor? If not, don't split it;
   fold it into a related story instead. This is the one hard stop in the whole
   method: skipping it produces technical tasks disguised as stories.
2. **Apply split patterns in order, stop at the first that fits**: workflow steps →
   CRUD operations → business-rule variations → data variations → data-entry method
   (simple UI first) → major-effort split → simple/complex → defer performance →
   spike out genuine unknowns.
3. **Every story stays a vertical slice.** Never split into a "front-end story" +
   "back-end story" — each story must be independently releasable and touch whatever
   layers it needs to deliver real behavior. This is the anti-pattern both source
   skills name explicitly as the most common mistake.
4. Write 2–4 acceptance criteria per story (Given/When/Then), the same shape Table 1's
   FRs were traced from — a story's AC should read like a testable instance of its
   parent FR.

**Task** — technical breakdown of one User Story (e.g. schema/migration, API
endpoint, UI component, integration). **This level has no equivalent in any of the
three source skills** — all three stop at the User Story. Built here from ordinary
engineering decomposition: one Task per distinct technical surface a story touches
(data, API, UI, integration), not one Task per file.

**Subtask** — the concrete steps inside one Task, small enough that each is either
done or not (a schema change, a test, an error-handling branch). Same custom-built
level as Task, same reasoning: split until further splitting would just be listing
lines of code.

## Phase 5 — Assemble one HTML report

Package Table 1, the diagram, and Table 2 into **one self-contained `.html` file** —
never three separate pieces pasted into a chat reply. Order is fixed: Table 1 → diagram
→ Table 2. Table 2's Epics must be traceable to Table 1's use cases, and its User Story
ACs must be traceable to Table 1's FRs — if a reviewer can't walk backward from a
Subtask to the FR it serves, something in the middle was invented rather than derived.

**Style: "Casa Edge Playbook" register** — austere technical-editorial, not a
dashboard. Use these tokens verbatim (real values, not approximations — extracted
from the source page's own CSS):

```css
:root{
  --bg:#f5f7f6; --paper:#ffffff; --ink:#132129; --ink-2:#3f5059; --ink-3:#6c7c84;
  --line:#d8dfe0; --line-2:#e6ebec;
  --ok:#1b6b4a; --ok-soft:#e3f3ea; --warn:#8a5a17; --warn-soft:#f7ecd9;
  --bad:#8a2c22; --bad-soft:#f7e1de; --sea:#1e5f74; --sea-soft:#e2eef1;
  --sand:#efe6d3; --sand-ink:#4a3f28;
  --display:"Bricolage Grotesque",ui-sans-serif,system-ui,"Segoe UI",Helvetica,Arial,sans-serif;
  --body:"Source Serif 4",Georgia,"Times New Roman",serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0f171b; --paper:#15202600; --ink:#e8eeef; --ink-2:#b8c5ca; --ink-3:#86969d;
    --line:#2a3940; --line-2:#1f2c32;
  }
}
:root[data-theme="dark"]{
  --bg:#0f171b; --paper:#15202600; --ink:#e8eeef; --ink-2:#b8c5ca; --ink-3:#86969d;
  --line:#2a3940; --line-2:#1f2c32;
}
:root[data-theme="light"]{
  --bg:#f5f7f6; --paper:#ffffff; --ink:#132129; --ink-2:#3f5059; --ink-3:#6c7c84;
  --line:#d8dfe0; --line-2:#e6ebec;
}

body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);
  font-size:17px;line-height:1.5;padding-inline:clamp(16px,4vw,48px);padding-block:0 96px}
h1,h2,th{font-family:var(--display)}
h2 small{display:block;font-family:var(--mono);font-size:12px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--ink-3);margin-bottom:8px}
header .tag{display:inline-block;font-family:var(--mono);font-size:12px;
  letter-spacing:.12em;text-transform:uppercase;color:var(--sea);border:1px solid var(--sea);
  padding:3px 8px;margin-bottom:18px}
header .lede{font-size:20px;line-height:1.45;color:var(--ink-2);max-width:56ch;margin-top:16px}
header .meta{font-family:var(--mono);font-size:13px;color:var(--ink-3);margin-top:14px}
.tldr{border:2px solid var(--ink);padding:20px 24px;margin-top:32px;background:var(--paper)}
table{border-collapse:collapse;width:100%;font-size:14.5px;margin:16px 0}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line-2);vertical-align:top}
th{font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--ink-3);
  font-weight:700;border-bottom:1px solid var(--line)}
td.num,th.num{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums;
  font-size:13px;white-space:nowrap}
.pill{display:inline-block;font-family:var(--display);font-size:12px;font-weight:700;
  padding:2px 8px;border-radius:999px;white-space:nowrap}
.pill.ok{background:var(--ok-soft);color:var(--ok)}
.pill.warn{background:var(--warn-soft);color:var(--warn)}
.pill.bad{background:var(--bad-soft);color:var(--bad)}
.pill.sea{background:var(--sea-soft);color:var(--sea)}
.rule{font-family:var(--display);font-weight:700;padding:12px 16px;background:var(--sand);
  color:var(--sand-ink);margin:16px 0}
footer{margin-top:64px;padding-top:16px;border-top:1px solid var(--line);
  font-size:13px;color:var(--ink-3);font-family:var(--mono)}
[hidden]{display:none!important}
```

Fonts load from Google Fonts only (same allowance `diagram-design` itself uses) — no
other CDN, everything else inline.

### Dark/Light toggle — required, separate from VI/EN

A second, independent toggle for theme (not language). `prefers-color-scheme` sets the
default from the OS, but the report also needs a manual override — the two
`:root[data-theme="..."]` blocks above exist exactly for this, and they must actually
carry the dark/light values (a comment saying "same as above" is not a valid value —
write the real hex codes in both blocks, every time):

```html
<div class="theme-toggle">
  <button type="button" data-set-theme="light">☼</button>
  <button type="button" data-set-theme="dark">☾</button>
</div>
<script>
document.querySelectorAll('[data-set-theme]').forEach(function(btn){
  btn.addEventListener('click', function(){
    document.documentElement.setAttribute('data-theme', btn.getAttribute('data-set-theme'));
  });
});
</script>
```

Place `.theme-toggle` fixed top-right, next to `.lang-toggle` (e.g. `right:16px` for
language, `right:96px` for theme) — same visual treatment (mono, bordered, uppercase),
two separate controls, never merged into one button. Don't set a `data-theme` attribute
by default — no attribute means "follow the OS", which is the correct starting state;
only clicking a button pins it one way.

### VI/EN toggle — required, exact pattern

Every piece of user-visible text (headers, table cells, tldr, footer) is written
**twice**, once per language, as sibling spans — never left untranslated in one
language:

```html
<span class="t-vi">Tên dự án</span><span class="t-en">Project name</span>
```

```css
body[data-lang="en"] .t-vi{display:none}
body[data-lang="vi"] .t-en{display:none}
```

```html
<div class="lang-toggle">
  <button type="button" data-set-lang="vi" class="active">VI</button>
  <button type="button" data-set-lang="en">EN</button>
</div>
<script>
document.querySelectorAll('[data-set-lang]').forEach(function(btn){
  btn.addEventListener('click', function(){
    document.body.setAttribute('data-lang', btn.getAttribute('data-set-lang'));
    document.querySelectorAll('[data-set-lang]').forEach(function(b){
      b.classList.toggle('active', b === btn);
    });
  });
});
</script>
```

Place the `.lang-toggle` fixed top-right (`position:fixed;top:16px;right:16px`),
styled with the same tokens as `header .tag` (mono, uppercase, bordered) so it reads
as part of this system, not a bolted-on widget. Default `<body data-lang="vi">`.
**Table 2 especially** — every Epic/Feature/Story heading, every Task/Subtask cell,
and every acceptance criterion needs both spans, not just the column headers.

### Structure, in order

1. `<header>`: `.lang-toggle` (above), `.tag` pill naming the project ("BA ·
   <tên dự án>"), `<h1>` = project name, `.lede` = 1-sentence scope (both languages),
   `.meta` = date + "ba-skill" in mono.
2. `.tldr` box: 2-3 sentences — the single most important AS-IS→TO-BE change, not a
   recap of every row (both languages).
3. `.rule` divider + `<h2><span class="t-vi">Bảng 1A — AS-IS vs TO-BE</span><span
   class="t-en">Table 1A — AS-IS vs TO-BE</span></h2>`, then Table 1A as a real
   `<table>` — one row per comparable step, `.pill` in the "Thay đổi/Change" column
   (`.pill.ok` MỚI/NEW, `.pill.warn` THAY ĐỔI/CHANGED, `.pill.bad` LOẠI BỎ/REMOVED).
   Then `<h2>Bảng 1B — Actor & Hành động / Actors &amp; Actions</h2>`, Table 1B as its
   own `<table>` (one row per actor). Then `<h2>Bảng 1C — Yêu cầu & Use case / Requirements
   &amp; Use Cases</h2>`, Table 1C as its own `<table>` (2-column field/content — only
   4 rows now that AS-IS/TO-BE and Actors moved out, so this stays short). Three
   separate `<table>` elements, three separate `<h2>`s — not one table with three
   sub-sections.
4. `.rule` divider + `<h2>...Diagram<small>BPMN-style, drawn by
   diagram-design</small></h2>`, then the diagram's SVG **pasted directly inline** —
   not an `<iframe>`, not a linked file:
   ```html
   <figure style="margin:16px 0;border:1px solid var(--line);padding:16px;background:var(--paper)">
     <svg viewBox="..." role="img" aria-labelledby="dg-title dg-desc">
       <title id="dg-title" class="t-vi">...</title><title class="t-en">...</title>
       <desc id="dg-desc" class="t-vi">...</desc><desc class="t-en">...</desc>
       <!-- every node/lane label as a PAIR at the same position, not one gloss -->
       <text x="120" y="60" class="t-vi">Chọn chuyên khoa &amp; bác sĩ</text>
       <text x="120" y="60" class="t-en">Choose specialty &amp; doctor</text>
       <!-- diagram-design's own connectors/geometry/legend from Phase 3, unchanged -->
     </svg>
   </figure>
   ```
   **The diagram must obey the same toggle as everything else.** The `body[data-lang]`
   CSS rule from the VI/EN section above already hides/shows any `.t-vi`/`.t-en`
   element regardless of whether it's HTML or SVG — `<text>`, `<title>`, `<desc>` all
   take the class the same way a `<span>` does. So: every label pair sits at
   **identical coordinates** (same `x`/`y`, or the same `<tspan>` position), and only
   one member of each pair is visible at a time, driven by the one toggle button — do
   not build a second, separate diagram image to swap between; that doubles the file
   for no reason when the existing show/hide mechanism already does it per-element.

   This is the entire point of Phase 5: the diagram must never live in a second
   file — if `diagram-design` gave you a full `.html` document, extract just its
   `<svg>...</svg>` (and any `<style>` rules it depends on, merged into this report's
   own `<style>` block, renamed to avoid clashing with the tokens above), re-tag its
   text elements into `t-vi`/`t-en` pairs per the above, and drop the external file.
5. `.rule` divider + `<h2>...Table 2<small>Epic → Feature → User Story → Task →
   Subtask</small></h2>`, then the nested `.epic-block`/`.feature-block`/`.story-card`
   structure from Phase 4 — **not a flat table**. Each Epic's `<h3>` carries a
   `.pill.sea` badge, so grouping is visible without repeating the Epic name on every
   row the way a flat table would have needed to.
6. `<footer>`: source scenario one-liner + "Generated by ba-skill" in mono (both
   languages).

No dashboard chrome (no cards, no shadows, no gradients) — the register is a written
document that happens to be HTML, not an app screen.

### Pre-delivery checklist — mandatory, do not skip

Three earlier runs of this skill all shipped a report where the diagram's text was
one language only (or both languages hardcoded side by side, never toggling). That is
a failed run, not a passable one with a caveat. Before calling the report done,
literally check the file for these, one by one:

1. **Exactly one `.html` file exists** — no second diagram file next to it.
2. **Every `<text>`/`<title>`/`<desc>` inside the `<svg>` has a `class="t-vi"` or
   `class="t-en"`** — search the file yourself; if any diagram text lacks one of
   these two classes, the diagram is not done, go back to Step 3b/Phase 5-item-4 and
   fix it before delivering.
3. **Both a `.lang-toggle` and a `.theme-toggle` exist**, each with two buttons and a
   working click handler.
4. **No FR/NFR cell contains an unexplained abbreviation** — read each one back as if
   you'd never seen this project before.
5. **Embed the actual Step 3a ASCII sketch inside the delivered HTML file itself**,
   as an HTML comment right before the `<figure>` that holds the diagram:
   ```html
   <!-- STEP-3A-ASCII-SKETCH
   [paste the literal ASCII art here, exactly as drawn]
   -->
   ```
   This is deliberately mechanical, not an honor system. A benchmark of this skill
   found that "paste the sketch in your reply" was satisfied in only 2 of 3 fresh
   runs — the third run skipped Step 3a, said nothing about it, and only produced a
   sketch when directly challenged afterward. Asking nicely was not enough; a
   grep-able artifact in the file itself is. If you reach this checklist item with no
   real sketch to embed, that means Step 3a did not happen: go back, draw it now, and
   check it against the SVG you already made before delivering — don't reconstruct a
   sketch from the finished SVG and embed that, that is fabricating evidence in the
   deliverable, not fixing the gap.
6. **Every branch point in the diagram is a diamond (gateway), not a rectangle with
   more than one arrow leaving it** — scan the SVG's shapes yourself; a rectangle
   with two or more outgoing connectors means a gateway is missing. The legend must
   also name every shape actually used (start/end event, activity, exclusive
   gateway, parallel gateway) — not just the highlight color, the way earlier runs
   only explained "bước lõi/nhánh tuỳ chọn" and left the shapes themselves
   unexplained.

If any of these fail, fix them before replying — don't deliver a report with a known
gap and a caveat explaining why; the caveat is not a substitute for the fix.

## Judgment calls

- **Scenario too thin to fill Table 1** — ask the 2-3 blocking questions (actors,
  trigger, pain point), don't invent an AS-IS. A short honest table beats a
  plausible-sounding invented one.
- **`diagram-design` not installed / not available** — say so plainly and describe
  the process in the TO-BE row of Table 1 instead of hand-drawing an SVG; don't
  silently skip the diagram deliverable without saying why it's missing.
- **ASCII sketch doesn't match what `diagram-design` actually rendered** (it merged
  nodes to fit the density budget, rerouted a connector) — re-check the rendered SVG
  against Table 1's TO-BE list before pasting it into the report; note any merge in
  the diagram's caption rather than silently presenting a diagram that quietly drops
  a step the sketch had.
- **A Feature that turns out not to be "Valuable" under the INVEST check** — don't
  force a split. Fold it into whichever Feature it actually serves and note why in
  Table 2.
- **User pastes an already-existing Epic/Story list instead of a scenario** — skip
  straight to applying the split patterns (Phase 4) rather than re-deriving Table 1
  from nothing.

## Credits — what came from where

- **Table 1's method (AS-IS/TO-BE, actor identification, traceable
  requirements)** — adapted from VoltAgent's `business-analyst` subagent profile
  (`awesome-claude-code-subagents`, `categories/08-business-product/business-analyst.md`):
  its discovery checklist, process-mapping priorities, and "100% traceability"
  principle.
- **The BPMN-style diagram step** — delegated entirely to Cathryn Lavery's
  `diagram-design` skill (`cathrynlavery/diagram-design`), using its own swimlane/
  process type distinction, density budget, and self-contained HTML+SVG output
  contract verbatim rather than reimplementing them.
- **The User Story split method** — adapted from Dean Peters' `Product-Manager-Skills`
  (`epic-breakdown-advisor` and `user-story-splitting`), both built on Richard
  Lawrence's Humanizing Work patterns: the INVEST pre-check, the ordered pattern list,
  and the horizontal-slicing anti-pattern warning.
- **Task and Subtask levels are NOT from any of the three sources** — none of them
  decomposes past the User Story. Built here as a plain engineering breakdown so
  Table 2 reaches Subtask as the user asked.
