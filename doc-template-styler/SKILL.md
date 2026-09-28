---
name: doc-template-styler
description: Turn raw data or an existing document (notes, Markdown, Word .docx, a chat paste, exported text) into a finished, self-contained HTML document with a clickable table of contents — every section is listed and one click jumps to it. Asks the user which layout they want (12 bundled templates plus 11 colour skins, or their OWN sample — an HTML file, a screenshot, a website to match) and which colour (26 palettes or their own hex), then renders, validates and delivers. Use when asked to lay out or pretty-print a document, "áp template", "format lại tài liệu", "đóng gói thành báo cáo", "làm docs có mục lục", "tạo tài liệu từ data", turn notes/a draft/an exported doc into a polished HTML deliverable, or choose a template/colour for a document. Also covers the bundled editor (`docstyler.py editor`) for hand-editing structure and previewing templates. This re-presents content that already exists; it does not research, expand or rewrite it.
---

# Doc Template Styler

Turn data or a document the user already has into one self-contained HTML file
with a **clickable table of contents**: every section is listed, and a click
jumps straight to it. The layout and the colour are **the user's choice** —
from the templates and palettes in this skill, or from a sample they bring.

The skill never invents content: only what is in the source is re-presented.

## The three things that matter

1. **Every document has a working contents.** Each headed section gets a unique
   anchor ("Kết quả" -> `#ket-qua`) and a link in the contents. Templates with a
   sidebar/contents slot (`{{toc}}`) put it there; for any template without one
   — including a user's own — `docstyler.py render` adds a contents box at the top of
   the body. `docstyler.py validate` fails a document where a headed section is
   missing from the contents or a link lands nowhere.
2. **Ask, don't assume.** Before rendering, ask the user which template and which
   colour (step 3). Offer a sensible default so the question is one click, but
   the choice is theirs — never pick a layout silently.
3. **The user may bring their own look.** An HTML/template file, a screenshot, a
   website, a brand colour — any of these is a valid answer to "which
   template?" (step 4).

## Files in this skill

| Path | What it is |
| --- | --- |
| `scripts/docstyler.py` | the one entry point: `import`, `render`, `validate`, `palette`, `preview`, `scan`, `editor`, `templates` (`--help` lists them) |
| `assets/bundle.json` | the templates, 26 palettes and the browser editor, unpacked on first run into a cache under the system temp folder |
| `references/reference.md` | Part 1: the model JSON (step 1). Part 2: the template contract (building a template from a user's sample) |

`--template` takes a bundled template **id** (`technext-shell`, `letter-memo` ...)
or a path to a folder of the user's own. Python 3.8+ standard library only.

## Workflow

### 1. Read the source and write the model

Read the source in full first. For Markdown, plain text or Word, let the
importer write the first draft — deterministic, keeps the wording, prints the
outline:

```bash
python scripts/docstyler.py import <source.md|.txt|.docx> --out .doc-styler/model.json
```

It maps headings, lists (nested by indentation or Word numbering), tables,
quotes, `Key: Value` runs, fenced code and images (Word images arrive embedded),
and keeps **bold**, *italic*, `code` and links as inline Markdown. Read the draft
against the source and correct what it guessed wrong.

For **raw data** — a CSV/Excel export, JSON, a list of records, a chat paste —
write the model by hand from `references/reference.md (Part 1)`: one section per
natural group (per table, per entity, per period, per topic the data already
has), a `table` for tabular rows, `kv` for single records, a short `paragraph`
only where the source itself carries the text. Headings come from names already
in the data (sheet names, group keys, column values); do not invent a narrative.
The sections are what the contents will list, so give every section a heading.

The model lives in `.doc-styler/` next to the output, never over a user file.
Decide `doc_type` (`report`, `memo`, `meeting-minutes`, `proposal`, `how-to`,
`newsletter`, `spec`, `notes`). Keep source order; choose block types by what
the content *is*. If the user wants both languages, put `{"vi","en"}` in every
text field — both everywhere or neither.

### 2. Show the outline — this is the contents the reader will click

```bash
python scripts/docstyler.py import --outline .doc-styler/model.json
```

```text
 1. Tổng quan ..................... paragraph, kv
 2. Kết quả kinh doanh ........... paragraph, heading(h3), table(4 rows), callout(success)
 3. Kế hoạch Quý 4/2026 .......... list(ordered, 4), hr, paragraph
```

Say that these headings become the clickable contents, and what did not map
cleanly. Apply what they ask — split, rename, move, drop, merge sections — by
editing the model and printing the outline again. A section with no heading is
not listed in the contents; point that out. The editor
(`python scripts/docstyler.py editor --out .doc-styler/editor.html`, then open it) is the drag-and-drop alternative.

### 3. Ask: which template, which colour

Ask both in **one** question round (use the AskUserQuestion tool when
available; otherwise a short numbered list). Recommend one option for each,
based on the document, and mark it — so a user who does not care answers in
one click.

**Template** — offer 3–4 that fit this document, plus "my own sample":

| id | built for |
| --- | --- |
| `technext-shell` | long on-screen documents: fixed sidebar contents with search, cover page, progress bar (TechNext default) |
| `report-longform` | long analysis: sticky contents rail over one reading column |
| `plain-report` | neutral single column that prints cleanly; memos, short reports |
| `classic-report` | formal, serif; annual/quarterly reports, board papers |
| `meeting-minutes` | dense, ruled, two-column contents box, decision/action tags |
| `proposal-pitch` | gradient cover band, numbered service blocks, commercial table |
| `dashboard` | KPI tiles from `kv` blocks, numeric tables; metric-heavy data |
| `card-grid` | short independent sections as cards; status round-ups |
| `timeline` | one marker per section; plans, procedures, logs |
| `checklist` | list items become tick boxes |
| `magazine` | two-column editorial with drop caps |
| `letter-memo` | letterhead and signature line |

(`technext-shell-<colour>` are the same shell with a preset palette.) Details:
the table above.

**Colour** — offer 3–4 palettes that suit the tone, plus "my own colour".
Palettes (the bundled palettes, each with dark + light, the reader can toggle):

- neutral: `mono`, `slate`, `steel`, `graphite`, `carbon`, `ink`
- blue/teal: `technext-blue`, `ocean`, `lagoon`, `midnight`
- green: `forest`, `moss`, `mint`
- warm: `warm-earth`, `amber`, `sand`, `citrus`, `terracotta`
- red/pink: `crimson`, `burgundy` (đỏ đô + vàng đồng), `rose`
- purple: `plum`, `aubergine`, `violet`, `indigo`
- brand: `technext`

**Let them see before choosing** when they are unsure ("cho xem thử", "không
biết chọn", "show me"): render their *own* document through the templates and
palettes into one page, and ask them to name one:

```bash
python scripts/docstyler.py preview --model .doc-styler/model.json \
  --out .doc-styler/preview \
  --palette-matrix "technext,ocean,forest,warm-earth,crimson,plum,steel,mint"
```

If the user has already said which template and colour, do not ask again — use
them. If they answer only one of the two, use the recommended option for the
other and say so.

### 4. When the user brings their own sample

- **An HTML page or template folder** — use it as the template:
  `docstyler.py render --template <folder-or-file's folder>`. Run
  `docstyler.py scan` on it first and tell the user what it lacks.
  `docstyler.py render` fills gaps without editing their file: no `{{body}}` → content
  goes at the end of `<body>`; no `{{toc}}` → a contents box on top. If it does
  not define the five colour variables (`--brand-primary`, `--brand-accent`,
  `--brand-ink`, `--doc-bg`, `--doc-surface`), palettes will not recolour it —
  say so and keep its own colours unless they ask otherwise.
- **A screenshot, a PDF page or a website to match** — build a new template that
  reproduces that look, against `references/reference.md (Part 2)`: inline CSS,
  `{{title}}`, `{{body}}`, `{{toc}}` (a real contents — sidebar or box), the five
  colour variables, `data-theme`/`data-lang` on `<html>`, an `@media print`
  block. Take its colours from the sample (`docstyler.py palette`). Save it to
  `.doc-styler/templates/<name>/template.html` with a `manifest.json`, show a
  render, and adjust until they approve. Do not fetch fonts or images from the
  network; describe the sample back to the user before building.
- **A colour** ("màu logo #1E6F5C", "xanh như web công ty") — one hex is enough:

```bash
python scripts/docstyler.py palette --primary "#1E6F5C" [--accent ...] --mode light \
  --out .doc-styler/my-palette.json
```

  Turn a colour name into a hex and say which hex you used. A mood ("dark and
  professional") is not a colour: suggest two or three palettes instead.

### 5. Render, validate, deliver

```bash
python scripts/docstyler.py render --model .doc-styler/model.json \
  --template <chosen-id> \
  --palette <chosen> | --palette-file .doc-styler/my-palette.json \
  --out <output>.html
python scripts/docstyler.py validate <output>.html --require-palette \
  --model .doc-styler/model.json
```

The validator fails on: a headed section missing from the contents, a contents
link to nowhere, duplicate ids, unfilled placeholders, network resources, and —
in a bilingual document — a pair with one side empty. Fix everything it reports,
then open or screenshot the result and click through the contents yourself.

Report: the output path, template, palette (or custom colours), number of
sections in the contents, and anything from the source that did not map onto a
block type. Offer to switch template or colour — the model is kept, so it is
one re-render.

## Command reference

```bash
python scripts/docstyler.py import source.md|source.txt|source.docx [--out m.json] [--title ..] [--doc-type ..]
python scripts/docstyler.py import --outline m.json

python scripts/docstyler.py preview --model m.json --out preview \
  [--palette name | --palette-file f.json | --palette-matrix "a,b,c" | --palette-matrix all] [--mode auto|dark|light]

python scripts/docstyler.py scan [<templates-dir>] [--out registry.json]

python scripts/docstyler.py palette --primary "#8C4A2F" [--accent "#A9691F"] \
  [--ink ...] [--bg ...] [--surface ...] [--mode light] --out palette.json [--name "..."]

# --template: a bundled id or a folder; default technext-shell
python scripts/docstyler.py render --model m.json [--template id|dir] \
  [--palette name | --palette-file f.json] [--theme dark|light] [--bilingual auto|true|false] --out out.html

python scripts/docstyler.py validate out.html --require-palette [--model m.json] [--min-sections 0]

python scripts/docstyler.py editor --out .doc-styler/editor.html   # drag-and-drop editor, opens from file://
```

## Rules

- **A clickable contents in every document.** Every headed section is listed and
  reachable; never deliver a file the validator flags for the contents.
- **The user chooses the look.** Ask template and colour once (step 3), with a
  recommendation; accept their own sample. Do not switch layout on your own
  after they chose.
- **Re-present only.** No summaries, invented headings, added sections or
  research. Splitting run-on text and fixing obvious typos is fine.
- **Never edit a bundled template or a file the user gave you.** Fill
  placeholders; `docstyler.py render` adds the palette override, block styles and, if
  needed, the contents box. A new look is a new template in `.doc-styler/`.
  Colour skins are generated from their base, never hand-tuned.
- **One self-contained file.** Inline CSS, data-URI images, no CDN; it must open
  from `file://` with no network.
- **Both languages or neither.**
- **Work outside the user's files.** Models, previews and built templates go in
  `.doc-styler/`; only the deliverable is written beside their document.

## Handling awkward input

- **Scanned or image-only PDF** — say there is no text layer; do not guess.
- **Several documents** — one model and one output each; ask template/colour once
  and offer to reuse the answer for all.
- **Content that fits no block type** — keep it as a `paragraph` and say which.
- **Data with no natural headings** — ask the user how to group it (by column,
  by period, by category) rather than making titles up; the grouping becomes the
  contents.
