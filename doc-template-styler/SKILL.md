---
name: doc-template-styler
description: Reformat a raw or unstructured document into a finished, self-contained HTML file by filling the skill's fixed TechNext HTML template — the layout never changes, only the colour palette does (25 named palettes, or the user's own colours), unless the user explicitly names a different bundled template in that request. Use when asked to lay out or pretty-print a document, "áp template", "format lại tài liệu", "đóng gói thành báo cáo", turn notes/a draft/an exported doc into a polished HTML deliverable, or choose a colour for a document. Also covers the bundled editor (assets/editor/doc-styler-editor.html) for hand-editing structure and previewing templates. This re-presents content that already exists; it does not research, expand or rewrite it.
---

# Doc Template Styler

Turn a document the user already has into a self-contained HTML file, using the
HTML template assets in this skill and a colour palette.

The template is an asset on disk, not something you design on the fly — and not
something you go shopping for either. This skill substitutes the content into the
fixed TechNext template and appends one palette override. It never edits a
template file and never invents content: only what is in the source document is
re-presented.

## Setup - unpack the assets first

This skill ships its templates, palettes, editor and scripts **packed** into
`assets.bundle.json`, because the shared library caps a skill at three
supporting files. Unpack them once, in place:

```bash
python scripts/render_doc.py --unpack
```

That writes `assets/` and the other files next to this `SKILL.md`, after which
every path below (`assets/templates/technext-shell/template.html`) is real. The
scripts also unpack by themselves the first time they run, so this is only
needed when you want to look at the files by hand.

## The template is fixed (hard rule)

`assets/templates/technext-shell/template.html` is **the** template. Every
document this skill produces is laid out in it, unmodified. The layout does not
vary; the **palette** does. That is the only free variable.

- Never substitute a different layout because it seems to fit better. There is
  nothing to choose and nothing to search for.
- Never ask the user to pick a template. Ask about **colour**; the layout is
  already settled.
- The other twenty-two folders are **inventory, not options**. Use one only when
  the user names it in that request — and then only for that one document.
- Never edit `technext-shell/template.html`, or any template file. Fill its
  placeholders, append the palette override, stop.
- A request for a colour is a request for a colour, not for a layout. Wanting a
  different look is a change to confirm, never one to assume.

**The document bends to the template, never the template to the document.**
Anything that would deviate — a different layout, a different skin, an extra
element, a restructured block — happens only when the user asks for that change
in so many words. Absent that request, deliver it in `technext-shell`.

## Assets in this skill

| Path | What it is |
| --- | --- |
| `assets/templates/<id>/template.html` | a template: placeholders `{{title}}`, `{{body}}`, `{{toc}}`, ... |
| `assets/templates/<id>/manifest.json` | `label`, `use_when`, `doc_types`, `default_palette` |
| `assets/palettes.json` | 25 named palettes, each with a `dark` and a `light` variant |
| `references/template-contract.md` | the full placeholder, class and colour-variable contract |
| `references/content-model.md` | the model JSON shape written in step 3 |
| `scripts/scan_templates.py` | list every template with its use_when, placeholders and vars |
| `scripts/preview_sheet.py` | render one model through every template into a comparison page (on request, step 5) |
| `scripts/render_doc.py` | fill a template: `--palette <name>` or `--palette-file <json>` |
| `scripts/custom_palette.py` | build a palette file from colours the user names |
| `scripts/validate_output.py` | check a rendered file before handing it over |
| `scripts/build_template_variants.py` | regenerate the colour skins from a base template |
| `assets/templates/<base>/variants.json` | which palettes a base template is skinned into |
| `assets/editor/doc-styler-editor.html` | optional: the user edits structure by hand in a browser |

Twenty-three templates ship here, so a request for a different look can be
answered without inventing one. This is inventory: `technext-shell` is what gets
used unless someone names another (see the hard rule above). Twelve are layouts:

| id | for |
| --- | --- |
| `technext-shell` | on-screen documents with a sidebar, cover page and searchable contents |
| `plain-report` | the neutral single column that prints cleanly; the safest fallback |
| `classic-report` | formal, serif, sheet-like; annual and quarterly reports, board papers |
| `magazine` | two-column editorial with drop caps and pull quotes |
| `card-grid` | short independent sections shown as cards; dashboards and round-ups |
| `dashboard` | KPI tiles and numeric tables; anything metric-heavy |
| `timeline` | a rail with one marker per section; plans, procedures, logs |
| `report-longform` | a sticky left rail over one measured column; long analysis |
| `meeting-minutes` | dense and ruled, with a contents box and decision/action tags |
| `proposal-pitch` | a gradient cover band and a highlighted commercial table |
| `letter-memo` | letterhead, memo header block and a signature line; no chrome |
| `checklist` | list items become tick boxes, plus a scroll-progress bar |

The other eleven are **colour skins of `technext-shell`** — `technext-shell-ocean`,
`-midnight`, `-aubergine`, `-carbon`, `-crimson`, `-amber`, `-forest`, `-rose`,
`-mint`, `-steel`, `-graphite`. A skin is the base template's markup, byte for
byte, with only `default_palette` changed: same layout, one colour, chosen from
the template list instead of the palette question. They exist so "show me the
shell in red / green / purple" is a template answer, not a separate round of
questions. Do not hand-edit a skin — the base file is the source, and

```bash
python scripts/build_template_variants.py        # regenerate every skin
python scripts/build_template_variants.py --list # check they are all present
```

Every one of the 23 defines the five colour variables, so any palette still
applies to any of them. Read a manifest's `use_when` only to judge whether a
template the user *named* can carry this document — never to go shopping for one.
When the user asks for a colour by name, the palette is the answer: change the
colour, not the layout.

## Workflow

### 1. Open the template

The template is `assets/templates/technext-shell/`. Open it and move on. There is
nothing to search for and nothing to choose.

Only when the user names a template in this same request, resolve it in order:

1. The template path or folder they named.
2. A `templates/` folder next to the source document.
3. `assets/templates/<id>/` in this skill.

Never improvise a new design, and never edit one you were given. If the user
wants a design that does not exist, offer to build it against
`references/template-contract.md` — as its own explicitly requested step.

### 2. Read the registry — only if a template was named

Skip this for the default `technext-shell`: its contract and colour variables are
already known.

```bash
python scripts/scan_templates.py <templates-dir>
```

Each entry carries `use_when`, the placeholders it offers and the colour
variables it defines. Match `use_when` against the *document*, not against the
design you like: is it long and section-heavy, or short and printable? Does it
have metrics, tables, action items, a timeline? Anything in a template's `issues`
list matters only if it affects this document — say so if you use such a template.

### 3. Read the document and write the model

Read the source in full first. Then write the model JSON from
`references/content-model.md` to a working folder — `.doc-styler/` next to the
output, never over a file the user owns.

Decide `doc_type`: `report`, `memo`, `meeting-minutes`, `proposal`, `how-to`,
`newsletter`, `spec` or `notes`. Sections keep the source order; choose a block
type by what the content *is* (`- ` lines are a `list`, `Key: Value` lines are
`kv`, a pipe table is a `table`), not by how it looked in the original.

If the source is already bilingual, or the user wants both languages, put a
`{"vi": "...", "en": "..."}` object in every text field. Fill both languages
everywhere or neither: a half-translated document looks broken the moment the
reader toggles.

### 4. Show the structure and let the user reshape it

Before rendering anything, print the outline you derived and ask whether it is
right. This is the step where the user reorganises their document, so make it
cheap to answer:

```text
1. Tổng quan ..................... paragraph, kv
2. Kết quả kinh doanh ........... paragraph, heading(h3), table(4 rows), callout(success)
3. Cơ cấu doanh thu ............. list(4), table(4 rows)
4. Vận hành và chuỗi cung ứng ... paragraph, table(4 rows), callout(warn)
5. Rủi ro và tồn đọng ........... list(3), quote
6. Kế hoạch Quý 4/2026 .......... list(ordered, 4), hr, paragraph
```

Say what did not map cleanly. Then apply what they ask — split a section, rename
a heading, move a block, drop one, promote a table to bullets — by editing the
model JSON and printing the revised outline. Loop until they are happy; adding
sections of your own is not part of this, only reshaping what is there.

If the user would rather drag things around themselves, point them at
`assets/editor/doc-styler-editor.html` — it reads the same model and exports the
same HTML — and continue from the JSON it gives back.

### 5. Render a preview sheet — only when the user asks to compare

**Skip this by default.** The template is fixed, so a preview sheet has nothing to
decide, and running it anyway is the deviation the hard rule forbids. Use it when
the user asks to see the alternatives — "cho tôi xem các mẫu khác", "có kiểu nào
khác không", "compare the layouts" — then show it and let them name one. A
template they name applies to that document; the default stays `technext-shell`.

```bash
python scripts/preview_sheet.py --model .doc-styler/model.json \
  --templates assets/templates --out .doc-styler/preview --palette technext
```

This renders the *same* document through every template and writes
`preview/index.html`: one thumbnail per template, each a real render, with the
template's `use_when` and badges for anything wrong (`no {{body}}`, fixed
colours). Tell the user to open it and name one; naming one never changes the
default. Add `--mode dark|light` to preview
the other mode, or `--palette-file` when the colours are already decided.

When the user wants to compare colours as well as layouts — "show me a lot of
options", "many colours" — pass `--palette-matrix` instead of `--palette`. Every
thumbnail then gets a row of palette buttons, and each button carries that
palette's own light/dark default, so one page covers layout and colour at once:

```bash
python scripts/preview_sheet.py --model .doc-styler/model.json \
  --templates assets/templates --out .doc-styler/preview \
  --palette-matrix "technext-blue,ocean,forest,warm-earth,crimson,plum,steel,mint"
python scripts/preview_sheet.py --model .doc-styler/model.json \
  --templates assets/templates --out .doc-styler/preview --palette-matrix all
```

Each template's own `default_palette` is shown first and marked `*`.

Do not skip this step by picking a template yourself and rendering blind. Reading
a manifest tells you what a template is for; only the render tells the user what
their actual document looks like in it. Do skip it if the user has already named
a template — then just use it.

### 6. Choose colours — or take the user's own

This is the one question worth asking about how a document looks. Colour varies
per document; the layout does not.

Named palettes live in `assets/palettes.json` — 25 of them, each carrying a dark
and a light variant, so the palette decides the brand hues and the reader's theme
toggle decides the mode; `--theme` only picks which mode the file opens in:

- neutral: `mono`, `slate`, `steel`, `graphite`, `carbon`, `ink`
- blue/teal: `technext-blue`, `ocean`, `lagoon`, `midnight`
- green: `forest`, `moss`, `mint`
- warm: `warm-earth`, `amber`, `sand`, `citrus`, `terracotta`
- red/pink: `crimson`, `rose`
- purple: `plum`, `aubergine`, `violet`, `indigo`
- brand: `technext`

Ask about colour at most once, and accept a plain
answer like "màu forest", "technext-blue" or "#1E6F5C".

**When no template suits the document**, the fallback is the user's own colours
on a built-in template. Take the colour(s) they name — one is enough — turn a
name into a hex, say which hex you used, and derive the rest:

```bash
python scripts/custom_palette.py --primary "#8C4A2F" --mode light \
  --out .doc-styler/my-palette.json
```

Then render with that file instead of a named palette:

```bash
python scripts/render_doc.py --model .doc-styler/model.json \
  --template assets/templates/plain-report \
  --palette-file .doc-styler/my-palette.json --out <output>.html
```

`custom_palette.py` fills in every value the user did not give and derives the
opposite mode, so the theme toggle still works. It uses the same derivation as
the editor, so the two never disagree. If the user only says "something dark and
professional", pick a named palette instead and say which — inventing a hex from
a mood is not a colour decision the user made.

### 7. Render, validate, deliver

```bash
python scripts/render_doc.py --model .doc-styler/model.json \
  --template assets/templates/technext-shell --palette <name> --out <output>.html
python scripts/validate_output.py <output>.html --require-palette
```

Pass a different `--template` only when the user named one. The command above is
the rule, not an example.

Fix anything validation reports, then check the render yourself before handing it
over — open it, or screenshot it and look. Report the output path, the template,
the palette (or the custom colours), the section count, and anything from the
source that did not map onto a block type.

## Command reference

```bash
# what templates exist, and what each needs
python scripts/scan_templates.py <templates-dir> [--out registry.json]

# compare templates against one document
python scripts/preview_sheet.py --model m.json --templates dir --out preview \
  [--palette name | --palette-file f.json] [--mode auto|dark|light]
  # or, to compare colours too:
python scripts/preview_sheet.py --model m.json --templates dir --out preview \
  --palette-matrix "ocean,plum,warm-earth,steel"   # or: all

# colours from the user, instead of a named palette
python scripts/custom_palette.py --primary "#8C4A2F" [--accent "#A9691F"] \
  [--ink ...] [--bg ...] [--surface ...] [--mode light] --out palette.json [--name "..."]

# produce the deliverable. --template defaults to the fixed template
# (technext-shell) from the hard rule - pass it only when the user named one.
# with no --palette, the template's own manifest default_palette is applied
python scripts/render_doc.py --model m.json \
  [--template dir] [--palette name | --palette-file f.json] \
  [--theme dark|light] [--bilingual auto|true|false] --out out.html

# check it before delivering
python scripts/validate_output.py out.html --require-palette [--min-sections 0]

# colour skins of a base template (markup copied, only default_palette changed)
python scripts/build_template_variants.py [--list] [--prune] [--base technext-shell]

# after changing a template, the palettes or the editor sources
python scripts/build_editor.py     # rebuilds the editor, regenerates goldens, runs the tests
node scripts/test_editor.mjs       # 58 checks over the shared renderer and parsers
```

## Rules that are not negotiable

- **The template is fixed.** `technext-shell`, unmodified, for every document.
  Only the palette varies. A different layout, a different skin or an edited
  template happens when the user asks for it in that request — never because you
  judged it a better fit.
- **Re-present only.** No summaries, no invented headings, no added sections, no
  research. Splitting run-on text and fixing obvious typos is fine.
- **Never edit a template file.** Substitute its placeholders and append the
  palette override; that is all. A colour skin is generated from its base, never
  hand-tuned.
- **One self-contained file.** Inline CSS, data-URI images, no CDN, no build step;
  it must open correctly from `file://` with no network.
- **Both languages or neither.** A half-translated document reads as broken.
- **Work outside the user's files.** Models and previews go in `.doc-styler/`;
  the only file written beside their document is the deliverable.
- **Show, then ask.** The outline (step 4) lets the user reshape the *structure*
  with their own content in front of them; the preview sheet (step 5) exists for
  when they ask to see other designs. Neither is licence to change the layout on
  your own.

## Handling awkward input

- **Scanned or image-only PDF** — say plainly that there is no text layer rather
  than guessing at the contents.
- **Several documents at once** — one model and one output per document;
  templates and palettes chosen independently.
- **Content that fits no block type** — keep it as a `paragraph` instead of
  dropping it, and tell the user which part that was.
- **A template with no `{{body}}`** — the preview sheet marks it; do not deliver
  with it, since the content has nowhere to go.
