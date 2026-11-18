# The single-file engine

`template/deck.html.j2` holds everything: inline CSS, the six slides, and ~250 lines of engine + slide scripts. `build_deck.py` renders it with Jinja2 (autoescape on; comments are `{## ##}`; the script block is `{% raw %}`), inlining fonts (variable woff2, latin; latin-ext only when the text needs it), the TechNext logos, the client logo, the Odoo app icons and the booking QR (segno). Result: one ~450 KB HTML that works offline, from email, a USB stick or Drive.

## Kept from technext-presentations' deck.js
- The 1600 x 900 `.stage` scaled whole with `--s` (`min(vw/1600, vh/900)`), centred, letterboxed on navy.
- **Phone held upright** (coarse pointer, short side ≤ 600): `.deck.is-rotated` turns the deck 90° and sizes it to the screen turned sideways; swipes are mapped through `point()` so they still go the right way. No hint overlay.
- Builds: `[data-step="n"]` (+ `data-until`), `data-steps` on the slide when a script reads the step. **`data-steps` is the LAST build index** (positions minus one).
- `Deck.on(id, {enter, step, leave, settle})` hooks with a per-visit `ctx` (`after`, `on`, `frame`, `tween`); never a bare `setTimeout` on a slide. `settle` paints the finished state (print, `Deck.go(i, -1)`, the shots).
- Keys: → ↓ PageDown Space Enter = next build or slide; ← ↑ PageUp Backspace = back; Home / End. Space/Enter on a focused slide button do the button's job only.
- Click or tap on empty slide space = next; clicks on `a, button, [data-i]` never advance. Swipe left/right (40px, mostly horizontal).
- `#n` in the URL opens slide n; the hash follows the slide.
- Print: `beforeprint` paints every slide finished; `@page 1600px 900px`, one slide per page. (PDF only when the user asks: headless Chrome `Page.printToPDF` with `preferCSSPageSize`.)
- Reduced motion: fades only, `ctx.after` capped at 60 ms, tweens at 120 ms; everything lands finished.
- The motion kit (motion.css/js) folded in: push transitions, the measured eases (`--soft-land`, `--snap-settle`, `--pop-over`...), word-by-word headlines (`.mx-w > .mx-wi`, marker after the last word), `data-fx="land"` for the one spring.

## Removed on purpose (the user: "dont add button or setting that not needed")
Presenter view and BroadcastChannel sync, speaker notes and the N key, overview grid (O), TV/cast display modes and their menu, black/white screen keys, the help overlay, the floating control bar, the progress rule, full-screen key, kiosk loop, offline service worker, wake lock, share copies, the launcher and Home button, the rotate hint. The footer's "02 / 06" is the only counter. Do not bring any of these back without the user asking.

## Slide anatomy
```html
<section class="slide [dark]" id="apps" data-title="..." data-steps="2" aria-roledescription="slide" aria-label="3 of 6: ...">
  {{ chrome(3) }}                                  <!-- logos + client label; footer technext.asia + 03 / 06 -->
  <div class="sec-head">
    <span class="kicker" data-in>the Odoo apps</span>
    <h2 class="h-m" data-in style="--d:80ms">{{ S.apps.title|hl }}</h2>    <!-- [[phrase]] -> one .hl marker -->
    <p class="lead" data-in style="--d:160ms">...</p>
  </div>
  ... the one working object ...
</section>
```
Per-slide styles are scoped by the slide id (`#heard .lg-*`, `#apps .st`, `#method .sp`, `#plan .bar`). Pixel values that depend on the data (rows, columns, weeks) come from `layout()` in build_deck.py, never from deck.json.

## Gotchas met while building it
- Jinja autoescape escaped the inlined `<style>` font CSS and the QR `<svg>` until both were wrapped in `Markup`: an escaped QR renders as invisible text and the card grows 2,000px tall. The shots' frame check caught it.
- `all:unset` on a `<button>` also removes the focus outline: give every reset control its own `:focus-visible` rule.
- A milestone label under a bar collides with it: labels sit to the right of the diamond.
- Short Gantt bars clip their text: `layout()` drops a bar label that would not fit (the row label already says it) and shortens sprint names to S1, S2... when needed.
- A client colour close to the hypercare green made UAT and hypercare look alike: hypercare is a light-blue TechNext bar, independent of the client colour.
- Plus Jakarta Sans at 800 has narrow word spaces and a wide period side bearing: that is the font, not a bug in the word splitter.
