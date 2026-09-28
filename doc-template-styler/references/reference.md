# Reference

Two parts: **Part 1 — the document model** (what step 1 writes) and **Part 2 — the template contract** (what a template must offer; read it before building a template from a user's sample).

## Part 1 — Document model

The canonical intermediate format. The agent reads the raw document and writes
this JSON; `scripts/render_doc.py` turns it into HTML. Keeping the model between
the two means the same document always renders the same way, and the agent never
writes CSS or HTML by hand.

### Shape

```json
{
  "title": "Báo cáo quý 3",
  "subtitle": "Phòng Kinh doanh",
  "date": "2026-09-25",
  "doc_type": "report",
  "brand": "TechNext",
  "lang": "vi",
  "sections": [
    {
      "heading": "Kết quả kinh doanh",
      "level": 2,
      "blocks": [
        { "type": "paragraph", "text": "Doanh thu đạt 12,4 tỷ đồng." },
        { "type": "list", "ordered": false, "items": ["Miền Bắc", "Miền Nam"] },
        { "type": "table", "headers": ["Chỉ số", "Giá trị"], "rows": [["Doanh thu", "12,4 tỷ"]] },
        { "type": "callout", "tone": "warn", "title": "Rủi ro", "text": "Tồn kho tăng." },
        { "type": "kv", "pairs": [["Người lập", "Nguyễn Văn A"]] }
      ]
    }
  ]
}
```

### Rules for filling it in

- `brand` is optional. It is the organisation the document belongs to and is
  what a template's bar label shows. Leave it out when the source does not name
  one: the label then disappears instead of showing an invented name.
- `doc_type` is the analysed document kind: `report`, `memo`, `meeting-minutes`,
  `proposal`, `how-to`, `newsletter`, `spec`, `notes`.
- Sections keep the source order. Do not merge or reorder content.
- `heading` may be empty for a document with no headings; the section then
  renders as blocks only. Prefer one section with all blocks over inventing titles.
- `level` defaults to 2. Only use deeper levels if the source already nests.
- Choose a block type by what the content *is*, not by how it looked in the
  source. A run of `- ` lines is a `list`; `Key: Value` lines are `kv`; a
  pipe/aligned table is a `table`.
- Callouts are for emphasised asides only (warnings, decisions, action items).
  Most paragraphs are just paragraphs.
- Preserve the source language and wording. Fixing obvious typos and splitting
  run-on text is fine; rewriting or augmenting content is not.
- If the source contains content no block fits, keep it as a `paragraph` rather
  than dropping it.

### Bilingual documents

Any text field may be a plain string or a `{"vi": "...", "en": "..."}` object:

```json
{ "type": "paragraph", "text": { "vi": "Doanh thu tăng 18%.", "en": "Revenue grew 18%." } }
```

This applies to `title`, `subtitle`, `heading`, `text`, `items[]`, `headers[]`,
`rows[][]`, `pairs[][]` and callout titles. The renderer emits a
`<span class="t-vi">`/`<span class="t-en">` pair, and the template's EN/VI switch
appears as soon as any field is bilingual.

Mixing plain strings and pairs in one document reads as broken when the reader
switches language. Fill both languages everywhere or neither. `lang` only sets
which language the file opens in; the sidebar table of contents follows the same
fields as the body.

### Field reference

| Field | Values |
| --- | --- |
| `type` | `paragraph`, `heading`, `list`, `table`, `quote`, `callout`, `kv`, `code`, `image`, `hr` |
| `list.ordered` | `true` for numbered steps, otherwise omit |
| `list.items[]` | a string / `{vi, en}` pair, or `{"text": ..., "items": [...], "ordered": true?}` for an item with a sub-list |
| `callout.tone` | `info`, `warn`, `success` |
| `code.text` / `code.lang` | the code, verbatim (never inline-formatted); optional language label |
| `image.src` | a `data:image/...` URI, or a local path relative to the model file (embedded at render time) |
| `image.alt` / `image.caption` | alt text (plain; one language is used) and an optional caption |
| `heading.level` / `section.level` | 1-6, clamped by the renderer |
| `section.id` | optional anchor; otherwise derived from the heading ("Kết quả" -> `ket-qua`), made unique |

### Inline formatting

Every text field except `code.text` understands a small, safe subset of
Markdown:

| Write | Renders as |
| --- | --- |
| `**bold**` | **bold** |
| `*italic*` or `_italic_` | *italic* |
| `` `code` `` | `code` |
| `[label](https://...)` | a link — `http(s):`, `mailto:`, `tel:`, `#anchor` or a relative path; anything else (e.g. `javascript:`) stays literal text |
| `\*`, `\_`, `\#`, `1\.` ... | the character itself, unformatted |

Everything else is escaped, so raw HTML in the source shows as text. `5 * 3`
and `snake_case_names` are left alone. Keep the source's own emphasis; do not
add emphasis the source did not have.

### Nested lists and new blocks

```json
{ "type": "list", "items": [
  "Miền Bắc",
  { "text": "Miền Nam", "ordered": true, "items": ["TP.HCM", "Cần Thơ"] }
] }
{ "type": "code", "lang": "sql", "text": "select * from orders;" }
{ "type": "image", "src": "img/flow.png", "alt": "Sơ đồ", "caption": { "vi": "Hình 1", "en": "Figure 1" } }
```

An image whose file cannot be found renders as a dashed box with its alt text
and `render_doc.py` warns; remote `http(s)` images are never fetched.

## Part 2 — Template contract

A template is a folder the user drops into the templates directory. The skill
never edits a template; it only substitutes placeholders and appends one
`:root` override.

### Folder layout

```text
templates/<template-id>/
|-- manifest.json      Optional. Without it, metadata is inferred.
|-- template.html      Entry file: template.html, index.html, either .htm variant, or any single .html.
`-- styles.css         Optional. Any .css in the folder is scanned and kept as-is.
```

Everything must work from `file://` with no network: inline the CSS, embed images
as data URIs, load no CDN fonts or scripts.

### manifest.json (optional but recommended)

```json
{
  "id": "quarterly-report",
  "label": "Quarterly Report",
  "description": "Long-form report with a summary block and data tables.",
  "use_when": "documents with metrics, tables or multiple numbered sections",
  "doc_types": ["report", "analysis"],
  "default_palette": "technext-blue",
  "entry": "template.html"
}
```

`use_when` matters most: it is what the skill matches against the analysed
document, so write it as a description of the *document*, not of the design.

### Required placeholders

`{{title}}` and `{{body}}` must appear in the entry file. These are optional:
`{{title_html}}` (same as `{{title}}` but may contain bilingual spans, for
headings), `{{subtitle}}`, `{{date}}`, `{{doc_type}}`, `{{brand}}` (optional;
empty when the document names no organisation), `{{lang}}`, `{{toc}}`,
`{{theme}}` and `{{bilingual}}`.

`{{toc}}` receives one `<a href="#section-id">` per headed section — put it in a
sidebar, rail or box. A template without `{{toc}}` still gets a contents: the
renderer prepends `<nav class="doc-toc">` (a numbered, clickable list, styled
by the renderer's block styles) to `{{body}}`. A template without `{{body}}`
gets the content placed at the end of `<body>`. Neither edits the file.

`{{title}}` is always plain text, because `<title>` cannot hold markup.

`{{body}}` receives already-generated section markup. Any placeholder the
renderer does not know is left untouched on purpose, so validation catches
typos instead of silently dropping content.

### Generated markup and the classes it uses

The renderer emits this fixed shape. A template only needs to style the classes
it actually cares about; unstyled elements still render.

```html
<section class="doc-section" id="slug">
  <h2>Section heading</h2>
  <p>Paragraph text.</p>
  <ul><li>Item</li></ul>
  <ol><li>Item</li></ol>
  <table class="doc-table"><thead>…</thead><tbody>…</tbody></table>
  <blockquote>Quoted text</blockquote>
  <div class="callout callout--info"><p class="callout__title">Title</p><p>Text</p></div>
  <dl class="kv"><dt>Label</dt><dd>Value</dd></dl>
  <ul><li>Item<ol><li>Sub-item</li></ol></li></ul>
  <pre class="doc-code" data-lang="sql"><code>select 1;</code></pre>
  <figure class="doc-figure"><img src="data:image/png;base64,..." alt="..."><figcaption>…</figcaption></figure>
  <figure class="doc-figure doc-figure--missing"><p>alt text</p></figure>
  <hr>
</section>
```

Text inside these elements may carry `<strong>`, `<em>`, `<code>` and `<a>`
from inline formatting. Section ids are unique and never equal an `id` the
template itself uses (`#search`, `#hero` ...): the renderer reads the
template's ids and suffixes a clashing section (`search-2`).

`.doc-code`, `.doc-figure` and nested lists are styled by the renderer, not the
template: it injects `<style id="doc-blocks">` (class selectors only, built on
the five colour variables, plus print rules) just before `</head>`, ahead of
the palette override. A template that styles these classes itself wins.

`callout--info`, `callout--warn` and `callout--success` are the only tone
variants. `callout__title` is omitted when the callout has no title.

### Colour variables

Define these five on `:root` in the template stylesheet so a palette can
override them:

`--brand-primary`, `--brand-accent`, `--brand-ink`, `--doc-bg`, `--doc-surface`

Palettes carry a `dark` and a `light` variant. The renderer appends

```html
<style id="palette-override">
:root{ /* the palette's default mode */ }
html[data-theme="dark"]{ /* dark variables */ }
html[data-theme="light"]{ /* light variables */ }
</style>
```

just before `</head>`, without touching the original file.

Both modes are emitted as attribute rules on purpose. A template that ships its
own light fallback puts it on `html[data-theme="light"]`, which outranks a bare
`:root` — so writing the palette's chosen mode to `:root` alone would silently
lose to the template and every light palette would render identically. The
`:root` block is only there for templates with no theme attribute at all. The attribute on `<html>` needs to be readable, so a template that
offers a toggle should put `data-theme="{{theme}}"` on its `<html>` element and
keep its own light fallback under `html[data-theme="light"]`. Any other variable a
palette sets is ignored by templates that do not use it.

A palette does not have to come from `assets/palettes.json`. `render_doc.py`
accepts `--palette-file <json>` for a one-off palette shaped like one entry of
that file (`{"default_mode": ..., "modes": {"dark": {...}, "light": {...}}}`),
which is what `scripts/custom_palette.py` writes when the user supplies colours
of their own. The five variable names are the only contract either way.

A template may instead hard-code its own colours and simply not offer palettes;
then the skill says the colour cannot be changed and keeps the template's own.

### Theme and language contract

`<html>` carries the reader-switchable state:

```html
<html lang="{{lang}}" data-theme="{{theme}}" data-lang="{{lang}}" data-bilingual="{{bilingual}}">
```

- `data-theme` is `dark` or `light`; `{{theme}}` is the palette's default mode
  unless `--theme` overrode it.
- `data-lang` is the current language. Bilingual text arrives from the renderer as
  sibling `<span class="t-vi">` / `<span class="t-en">` elements, so the switch is
  pure CSS:

```css
html[data-lang="en"] .t-vi{display:none}
html[data-lang="vi"] .t-en{display:none}
```

- `data-bilingual` is `true` only when the document actually contains both
  languages; hide the switch otherwise, or the reader gets a control that does
  nothing (`html[data-bilingual="false"] .lang-switch{display:none}`).

A template that skips this section still renders, it just has no toggles: the
extra placeholders resolve to plain values and the spans both display.

### Print

Give the template an `@media print` block that hides its chrome (navigation,
toggles, progress bars) and prints on white. A template with a dark default
should also switch to light mode for the print — `technext-shell` sets
`data-theme="light"` on `beforeprint` and restores the reader's mode on
`afterprint` — or pale text lands on white paper.

### What the template must not do

- Reference external http(s) assets, or rely on a build step.
- Pre-fill example content that looks real: the skill substitutes `{{body}}`,
  so demo text in a live region becomes fake content in the deliverable.