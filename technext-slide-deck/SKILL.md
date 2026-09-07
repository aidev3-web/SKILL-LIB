---
name: technext-slide-deck
description: Create a bilingual (Vietnamese/English, toggle button) branded HTML slide-deck presentation for TechNext Asia — full-viewport scroll-snap slides with a cover, dot navigation, and a reusable component system (cards, grids, tables, callouts, step-flows) matching the exact visual system used in Trung's decks (e.g. Trung_skill-library-project.html, Trung_mcp-skill-bridge-tools.html). Use this whenever asked to make a presentation, "bảng thuyết trình", "slide báo cáo", "làm slide", "trình bày", "deck", or to turn research/findings/a Q&A thread into presentable slides for TechNext Asia. Also use it to add new slides to an existing deck already built with this same template.
---

# TechNext slide deck (bilingual, scroll-snap)

## What this is for

Turning research, a decision, or technical findings into a presentable slide deck for TechNext Asia — one slide per idea, full-viewport scroll-snap sections, a working VI/EN toggle, and a consistent branded visual language across every deck so a viewer can jump between different decks and immediately recognize the same design system. This skill only **writes the deck file**. It does not publish/share it anywhere — ask before turning it into a shareable link.

## Reference template

`assets/slide-deck-template.html` is the exact, validated visual system — read it before writing anything. Copy its `<style>` block, the `<body>` shell (language-toggle buttons + dots nav + script), and the cover slide structure verbatim. Do not modify the CSS or the script — they're already tested (scroll-snap, IntersectionObserver dot-sync, VI/EN toggle, print styles, mobile responsive breakpoints, the `zoom:.70` compact-slide trick) across multiple real decks.

Key structural facts:

- **Bilingual pattern**: every user-visible string appears twice, once in `<span class="vi">` and once in `<span class="en">`, immediately adjacent. CSS shows/hides based on `body[data-lang]`. Never write text that isn't wrapped in both spans — the toggle has nothing to show in the other language otherwise.
- **One slide = one `<section class="slide" id="...">`.** Content goes inside `<div class="inner">`, except the cover slide (`id="s1"`), which uses `.cover` directly, not `.inner`.
- **Cover slide** (`id="s1"`): TechNext logo (inline base64 SVG — do not swap for an external `<img src="...">` file; it keeps the whole deck a single self-contained, portable HTML file), an `.eyebrow` pill, `<h1>` title, one lead paragraph, `.meta` chips (org name, date, 1-2 short fact chips), and a decorative `.orb` icon on the right (swap only the inner `<svg>` shape per deck topic — 2-4 simple shapes, keep the orb wrapper and its gradient).
- **Every content slide** follows the same `.head` pattern: `.kicker` (small label), `.title` (`<h2>`), `.lead` (one-sentence summary), and optionally `.num` (large faded number). Only use `.num` or `.toolnum` numbered badges when the slides genuinely form a numbered sequence (e.g. "Tool 1", "Tool 2" enumerating a fixed list) — don't add numbering as decoration on slides that aren't actually a sequence.
- **Component vocabulary** — reuse these exact classes, don't invent new ones per deck:
  - `.grid.g2` / `.grid.g3` — 2 or 3-column card grid.
  - `.card` plus exactly one accent class `.blue` / `.violet` / `.green` — colors the top border; rotate the three across a row, don't repeat the same accent on every card in one grid.
  - `.badge` — small uppercase pill label inside a card.
  - `code` (inline) / `.code` (block, dark background, monospace) — for literal commands, JSON, file paths, config snippets.
  - `table` / `th` / `td` — for comparisons or structured reference data; add `.yes`/`.no` classes to a `<td>` for a green/orange emphasized word inside it.
  - `.callout` — left-border highlight box for the single most important caveat or rule on that slide, not a dumping ground for extra content that didn't fit elsewhere.
  - `.flow` + `.step` — left-to-right (stacks vertically on mobile automatically) numbered pipeline; only for content that is a true ordered sequence.
  - `.pipe` — small inline chip sequence (e.g. `search → pull → deploy`) for a short pipeline reference inside a slide that isn't primarily about the pipeline itself.
- **Dots nav must stay in sync with the sections.** `<nav class="dots">` needs exactly one `<button class="dot" data-target="...">` per section `id`, in the same top-to-bottom order as the `<section>` elements. The script wires up click-to-scroll and scroll-to-active-dot automatically — you only maintain the list of buttons and section ids, never touch the script.
- **`<title>` stays stable for the life of a deck** — set it once when first creating the file; don't change it on a later revision of the same deck (matches the general rule that a name is how people recognize their tab/link).

## Writing the content

1. **Confirm scope before building**: the real topic, the intended audience, and roughly how many slides — ask if any of these is unclear rather than guessing a slide count or inventing content to fill slides.
2. **Copy `assets/slide-deck-template.html`** to the destination filename (see Naming below), then replace the placeholder cover and the three example slides (`overview`, `detail`, `flow` — demonstrating the card-grid, table, and pipeline patterns respectively) with real slides for the real topic. Delete whichever example slides don't apply; add more sections in the same shape for additional real content.
3. **Pick the simplest component that fits** each slide's actual content shape — a slide that's just one idea needs nothing more than `.head` + `.lead`; reach for `.grid`/`table`/`.flow` only when the content genuinely has that structure. Structural devices like numbering or a pipeline diagram should encode something true about the content, not decorate it.
4. **Keep every `vi`/`en` pair equally concise** — don't let one language run long and the other short; translate faithfully, not word-for-word.
5. **Update `<nav class="dots">` and the section `id`s together**, in lockstep — every `data-target` must match a real section `id` 1:1, or clicking that dot silently does nothing.
6. **Keep the cover's `.orb` SVG simple** (2-4 shapes, `stroke="white"`/an accent color) — it's a small decorative icon, not a diagram; save real diagrams for a content slide's `.card` or its own section.

## Naming and saving

Name the file `Trung_<kebab-case-topic>.html`, saved at the repo root — matching the existing decks `Trung_skill-library-project.html` and `Trung_mcp-skill-bridge-tools.html`. Don't invent a different naming scheme or move decks into a subfolder.

Deliver the finished file in the conversation so it can be opened directly. Ask before publishing it as a shareable Artifact link — these decks can contain draft or internal findings not yet meant for wider distribution, so treat "make it shareable" as a separate, deliberate step the user asks for explicitly, not something this skill does on its own.

## Judgment calls

If asked to "make a deck" with only a vague topic, ask for the real content/findings first — a polished-looking shell with invented slide content is worse than one clarifying question. If revising an existing deck built from this template, only touch the slides that actually changed; don't silently rewrite the shared CSS/script even if you think you can improve it — the visual system stays fixed across every deck in the series so they read as one consistent whole. If a genuine, deck-wide improvement to the template itself is needed (not just one slide's content), say so explicitly and ask before changing `assets/slide-deck-template.html`, since that changes every future deck, not just the one at hand.
