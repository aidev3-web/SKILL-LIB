#!/usr/bin/env python3
"""Render a document model into a user-supplied HTML template.

The model is the canonical intermediate format (see references/content-model.md).
Block markup is generated here so the same template always yields the same
classes. Two things are injected rather than written into the template:

  * the palette, as one :root / [data-theme] override, so the template's theme
    toggle keeps working across every palette;
  * bilingual text, as <span class="t-vi">/<span class="t-en"> pairs, so the
    template's language switch has something to switch between.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}")
PREFERRED_ENTRIES = ("template.html", "index.html", "template.htm", "index.htm")
LANG_KEYS = ("vi", "en")

# The layout is fixed: every document uses the skill's TechNext template unless
# the user names another one in the request. See "The template is fixed" in
# SKILL.md - this default is that rule, made mechanical.
SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = SKILL_ROOT / "assets" / "templates" / "technext-shell"
BUNDLE = SKILL_ROOT / "assets.bundle.json"


def unpack_assets(force=False):
    """Materialise the packed assets beside this script.

    The published copy of this skill ships every asset inside
    assets.bundle.json, because the shared library caps a skill at three
    supporting files. Unpacking in place makes that copy identical to the
    development tree, so the asset paths below stay true.
    """
    if not BUNDLE.exists():
        return 0
    import base64
    data = json.loads(BUNDLE.read_text(encoding="utf-8"))
    count = 0
    for rel, rec in data.get("files", {}).items():
        target = SKILL_ROOT / rel
        if target.exists() and not force:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if rec.get("encoding") == "base64":
            target.write_bytes(base64.b64decode(rec["text"]))
        else:
            target.write_text(rec["text"], encoding="utf-8", newline="")
        count += 1
    return count


if not (SKILL_ROOT / "assets").exists():
    try:
        unpack_assets()
    except Exception:
        pass


def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def is_dual(value):
    return isinstance(value, dict) and any(key in value for key in LANG_KEYS)


def rt(value):
    """Rich text: escaped plain string, or a bilingual span pair."""
    if is_dual(value):
        return "".join(
            '<span class="t-%s">%s</span>' % (code, esc(value.get(code)))
            for code in LANG_KEYS
            if value.get(code) is not None
        )
    return esc(value)


def plain(value, lang="vi"):
    """One language only — for <title> and attributes, which cannot hold spans."""
    if is_dual(value):
        if value.get(lang) is not None:
            return str(value[lang])
        for code in LANG_KEYS:
            if value.get(code) is not None:
                return str(value[code])
        return ""
    return "" if value is None else str(value)


def has_dual(value):
    if is_dual(value):
        return True
    if isinstance(value, dict):
        return any(has_dual(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(has_dual(v) for v in value)
    return False


def find_entry(template_dir):
    for name in PREFERRED_ENTRIES:
        candidate = template_dir / name
        if candidate.is_file():
            return candidate
    html_files = sorted(p for p in template_dir.rglob("*.htm*") if p.is_file())
    if not html_files:
        raise FileNotFoundError("no .html file found in %s" % template_dir)
    return html_files[0]


def render_blocks(blocks):
    parts = []
    for block in blocks or []:
        kind = (block.get("type") or "paragraph").lower()
        if kind == "paragraph":
            parts.append("<p>%s</p>" % rt(block.get("text")))
        elif kind == "heading":
            level = min(max(int(block.get("level", 3)), 1), 6)
            parts.append("<h%d>%s</h%d>" % (level, rt(block.get("text")), level))
        elif kind == "list":
            tag = "ol" if block.get("ordered") else "ul"
            items = "".join("<li>%s</li>" % rt(i) for i in block.get("items") or [])
            parts.append("<%s>%s</%s>" % (tag, items, tag))
        elif kind == "table":
            headers = block.get("headers") or []
            head = ""
            if headers:
                head = "<thead><tr>%s</tr></thead>" % "".join("<th>%s</th>" % rt(h) for h in headers)
            rows = "".join(
                "<tr>%s</tr>" % "".join("<td>%s</td>" % rt(c) for c in row)
                for row in block.get("rows") or []
            )
            parts.append('<table class="doc-table">%s<tbody>%s</tbody></table>' % (head, rows))
        elif kind == "quote":
            parts.append("<blockquote>%s</blockquote>" % rt(block.get("text")))
        elif kind == "callout":
            tone = esc(block.get("tone", "info"))
            title = block.get("title")
            heading = ""
            if title is not None:
                heading = '<p class="callout__title">%s</p>' % rt(title)
            parts.append(
                '<div class="callout callout--%s">%s<p>%s</p></div>'
                % (tone, heading, rt(block.get("text")))
            )
        elif kind == "kv":
            pairs = "".join(
                "<dt>%s</dt><dd>%s</dd>" % (rt(pair[0]), rt(pair[1]))
                for pair in block.get("pairs") or []
                if len(pair) >= 2
            )
            parts.append('<dl class="kv">%s</dl>' % pairs)
        elif kind == "hr":
            parts.append("<hr>")
        else:
            parts.append("<p>%s</p>" % rt(block.get("text")))
    return "\n".join(parts)


def section_id(section):
    heading = section.get("heading")
    if is_dual(heading):
        heading = plain(heading)
    return section.get("id") or _slug(heading or "section")


def render_toc(sections):
    links = []
    for section in sections or []:
        heading = section.get("heading")
        if heading is None or heading == "":
            continue
        links.append('<a href="#%s">%s</a>' % (esc(section_id(section)), rt(heading)))
    return "\n".join(links)


def render_sections(sections):
    parts = []
    for section in sections or []:
        heading = section.get("heading")
        level = min(max(int(section.get("level", 2)), 1), 6)
        head = ""
        if heading is not None and heading != "":
            head = "<h%d>%s</h%d>" % (level, rt(heading), level)
        parts.append(
            '<section class="doc-section" id="%s">\n%s\n%s\n</section>'
            % (esc(section_id(section)), head, render_blocks(section.get("blocks")))
        )
    return "\n".join(parts)


def _slug(text):
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text)).strip("-").lower()
    return slug or "section"


def palette_style(palette, theme):
    """Both modes are emitted as attribute rules.

    A template that ships its own light fallback puts it on html[data-theme=...],
    which outranks a bare :root — so writing the palette's chosen mode to :root
    would silently lose to the template. Attribute rules plus a :root fallback
    (for templates with no theme attribute at all) covers both cases.
    """
    if not palette:
        return ""
    modes = palette.get("modes") or {}
    if not modes:
        return '<style id="palette-override">:root{%s}</style>' % _decls(palette.get("vars"))
    initial = theme or palette.get("default_mode") or "dark"
    blocks = [":root{%s}" % _decls(modes.get(initial))]
    for mode in ("dark", "light"):
        if mode in modes:
            blocks.append('html[data-theme="%s"]{%s}' % (mode, _decls(modes[mode])))
    return '<style id="palette-override">%s</style>' % "".join(blocks)


def _decls(variables):
    return "".join("%s:%s;" % (k, v) for k, v in (variables or {}).items())


def inject_palette(document, style):
    if not style:
        return document
    if "</head>" in document:
        return document.replace("</head>", style + "\n</head>", 1)
    return style + "\n" + document


def load_palette(name, path):
    palettes = json.loads(Path(path).read_text(encoding="utf-8-sig")).get("palettes") or {}
    if name not in palettes:
        raise KeyError(
            "unknown palette %r; available: %s" % (name, ", ".join(sorted(palettes)))
        )
    return palettes[name]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--unpack" in argv:
        print("unpacked %d file(s) into %s" % (unpack_assets(force=True), SKILL_ROOT))
        return 0
    parser = argparse.ArgumentParser(description="Render a document model into an HTML template.")
    parser.add_argument("--model", required=True, help="document model JSON")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE),
                        help="template folder; defaults to the skill's fixed "
                             "template (technext-shell). Pass another only when "
                             "the user named one.")
    parser.add_argument("--out", required=True, help="output HTML path")
    parser.add_argument("--palette", default="", help="palette name from palettes.json")
    parser.add_argument("--palettes", default="", help="palettes.json path")
    parser.add_argument("--palette-file", default="",
                        help="a palette JSON file (from custom_palette.py) instead of a named palette")
    parser.add_argument("--theme", default="", help="initial mode: dark or light")
    parser.add_argument("--bilingual", choices=("auto", "true", "false"), default="auto",
                        help="show the language switch; auto detects it from the model")
    args = parser.parse_args(argv)

    model = json.loads(Path(args.model).read_text(encoding="utf-8-sig"))
    template_dir = Path(args.template).expanduser()
    is_default_template = template_dir.resolve() == DEFAULT_TEMPLATE.resolve()
    entry = find_entry(template_dir)
    document = entry.read_text(encoding="utf-8")

    palette = None
    if args.palette and args.palette_file:
        print("error: pass either --palette or --palette-file, not both", file=sys.stderr)
        return 2
    if args.palette_file:
        palette_path = Path(args.palette_file).expanduser()
        if not palette_path.is_file():
            print("error: no palette file at %s" % palette_path, file=sys.stderr)
            return 2
        try:
            palette = json.loads(palette_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            print("error: %s is not valid JSON (%s)" % (palette_path, exc), file=sys.stderr)
            return 2
        if not palette.get("modes"):
            print("error: %s has no \"modes\" object" % palette_path, file=sys.stderr)
            return 2
    elif args.palette:
        palettes_path = Path(args.palettes).expanduser() if args.palettes else \
            Path(__file__).resolve().parent.parent / "assets" / "palettes.json"
        try:
            palette = load_palette(args.palette, palettes_path)
        except KeyError as exc:
            print("error: %s" % exc, file=sys.stderr)
            return 2
    else:
        # No palette asked for: fall back to the one the template is designed
        # around, so a bare --template still produces the intended look.
        manifest = template_dir / "manifest.json"
        default_name = ""
        if manifest.is_file():
            try:
                default_name = (json.loads(manifest.read_text(encoding="utf-8-sig")) or {}).get("default_palette") or ""
            except json.JSONDecodeError:
                default_name = ""
        if default_name:
            palettes_path = Path(args.palettes).expanduser() if args.palettes else \
                Path(__file__).resolve().parent.parent / "assets" / "palettes.json"
            try:
                palette = load_palette(default_name, palettes_path)
                args.palette = default_name
            except KeyError:
                print("warning: template default_palette %r is not in %s" % (default_name, palettes_path),
                      file=sys.stderr)

    lang = plain(model.get("lang")) or "vi"
    theme = args.theme or (palette or {}).get("default_mode") or "dark"
    bilingual = has_dual(model) if args.bilingual == "auto" else (args.bilingual == "true")
    sections = model.get("sections")

    values = {
        "title": esc(plain(model.get("title"), lang)),
        "title_html": rt(model.get("title")),
        "subtitle": rt(model.get("subtitle")),
        "date": esc(plain(model.get("date"), lang)),
        "doc_type": esc(plain(model.get("doc_type"), lang)),
        # optional: the organisation this document belongs to. Absent means
        # the bar label disappears rather than showing a made-up name.
        "brand": rt(model.get("brand")),
        "lang": esc(lang),
        "theme": esc(theme),
        "bilingual": "true" if bilingual else "false",
        "body": render_sections(sections),
        "toc": render_toc(sections),
    }

    document = PLACEHOLDER_RE.sub(
        lambda m: values[m.group(1)] if m.group(1) in values else m.group(0), document
    )
    document = inject_palette(document, palette_style(palette, theme))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(document, encoding="utf-8")

    leftover = sorted(set(PLACEHOLDER_RE.findall(document)))
    print("rendered %s" % out)
    print("template: %s (%s)%s" % (template_dir.name, entry.name,
                                   "" if is_default_template
                                   else "  [NOT the default template - "
                                        "only correct if the user named it]"))
    print("palette: %s" % (args.palette or (Path(args.palette_file).name if args.palette_file else "template default")))
    print("theme: %s | language: %s | bilingual: %s" % (theme, lang, "yes" if bilingual else "no"))
    print("sections: %d" % len(sections or []))
    if leftover:
        print("unfilled placeholders: %s" % ", ".join("{{%s}}" % p for p in leftover))
    if bilingual and not has_dual(model):
        print("note: the switch is forced on, but no field has an en/vi pair yet")
    elif bilingual:
        print("note: language switch will show; fill both vi and en everywhere for a clean toggle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())