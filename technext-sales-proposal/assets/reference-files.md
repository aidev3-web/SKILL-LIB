# Reference files — read before writing anything

**Hard rule, checked mechanically in Phase 4: the delivered file must keep
`assets/proposal-template.html`'s *structure and mechanism* — never a new page
built from scratch.** Every Phase 1 group agent and the final assembly step must work
from the literal contents of `assets/proposal-template.html` — its `#sidenav`/
`buildNav()` mechanism, its single sliding `.tb-btn` VI/EN switch (not two separate
buttons), its `#progress` bar, its component classes (`.card`, `.kpi`, `.tbl`, `.pill`,
etc.), its chart/citation JS. If an agent's returned section HTML uses a different
toggle pattern, or wraps itself in its own `<html>`/`<head>` instead of being a
`<section>` fragment for the existing shell, that agent's output must be rejected and
re-generated with the actual template file attached to its prompt — do not merge it in
and hope it blends.

**The color palette/typography is per-client, not fixed navy/teal — boss feedback
2026-09-23: "I don't like the UI/visuals — AI to find latest UI/color scheme... it
doesn't need to follow exactly the look of the full-chart-manifest-demo."** Before
Phase 1 starts, pick (or ask the user to confirm) a palette + font pairing that fits
*this client's* industry/brand — e.g. a hospitality client can stay warm, a fintech
client can go cool/navy, a wellness client can go soft/pastel — by overriding the
template's `:root{--bg,--panel,--teal,...}` custom-property values and (optionally)
the Google Fonts `<link>`/`font-family` stack. **What must never change per client**
(this is the mechanically-checked part): the CSS variable *names*, the
`#sidenav`/`buildNav()`/`toggleTheme()`/`setLang()` JS, the component class names
(`.card`/`.kpi`/`.tbl`/`.pill`/`.grid`/etc.) and their layout behavior, the chart
helper functions (`regChart`/`mkChart`/`PAL`/`baseOpts`/`gridScale`/`inkColors`), and
the citation hover-card markup. Re-skinning the *values* those variables/classes
resolve to is expected and encouraged; renaming or restructuring them is not — that's
still the "off-template" failure this rule exists to catch.

- `assets/menu-structure.md` — the exact, fixed sidebar structure (group → item →
  slug → VI/EN labels). This is the source of truth for section IDs, order, and
  grouping. Do not drop, rename, or reorder items; you may add an extra item inside an
  existing group if research surfaces something that doesn't fit anywhere ("add more
  relevant categories" is allowed, removing/reordering fixed ones is not).
- `assets/proposal-template.html` — the working shell, styled to match Trung's actual
  reference build ("Client Nova · Strategic Due Diligence & Odoo 19 ERP
  Blueprint · Technext.html", kept alongside `prompt.txt` in the original working
  folder): dark/light `--bg`/`--panel`/`--teal` CSS-variable theme, sticky `#sidenav`,
  scroll progress bar, mobile hamburger nav, hero cover section, and a component
  library (`.card`, `.grid.g2/g3/g4`, `.kpi`, `.pill.p-*`, `.tbl`, `.quad` for any
  2×2 layout, `.tl` timeline, `.acc` accordion, `.tabs`/`.tabpane`, `.callout`). Copy
  this file as your starting point for every run.
  - **The sidebar is not hand-written.** `buildNav()` generates it at load time from
    every `<section data-nav-vi="..." data-nav-en="..." data-grp-vi="..." data-grp-en="...">`
    in `<main>` — tag each section correctly and the nav (grouped, ordered by DOM
    order) appears automatically, exactly the mechanism the real reference file uses
    (there it reads plain `data-nav`/`data-grp`; this template adds the `-vi`/`-en`
    suffix pair so `buildNav()` can also switch label language). Never add `<a>` links
    to `#sidenav` by hand.
  - The nav also has an **⬇ Install** button (PWA `beforeinstallprompt`/`pwaInstall`).
    It stays hidden until the browser's PWA install criteria are actually met, which
    needs **all four** of: served over https (or localhost), the linked
    `manifest.webmanifest` (already in `<head>`), a registered `sw.js`, and at least a
    192×192 + 512×512 icon — `assets/manifest.webmanifest`, `assets/sw.js`,
    `assets/icon-192.png`, `assets/icon-512.png` are provided for exactly this and must
    be deployed **alongside** the final HTML file, at the same relative path (all four
    files sit next to `<client-slug>-proposal.html`, not nested differently). It's a
    no-op, not a bug, when the file is opened locally via `file://` — browsers never
    install from `file://`. Don't try to "fix" it into always showing — that would be a
    fake state, not a working install button.
    - **Deploying through a wrapper/router app** (e.g. a personal "reports viewer" on
      Vercel that serves this file at a hash-routed URL like `#Sales%20Proposal/
      proposal-template.html` instead of as a real static file at its own path) breaks
      the relative `manifest.webmanifest`/`sw.js`/icon links — the browser resolves
      them against whatever the wrapper's actual base path is, which usually isn't
      where these four files were uploaded. If the install button needs to work, the
      proposal + its 4 companion files need to be deployed as their own static site at
      a real path (GitHub Pages, a plain Vercel static deployment, or any static host)
      — not embedded inside another app's hash-routed viewer. Say this explicitly if
      the user reports the button missing after deploying through such a wrapper,
      rather than re-debugging the HTML/JS itself.
  - Fill in each section's body (replace every `placeholder-note` paragraph with real
    bilingual `t-vi`/`t-en` span pairs), replace `<CLIENT NAME>`/`<TÊN KHÁCH HÀNG>` in
    the hero and `<title>`, and delete the template-instructions HTML comment before
    delivering. Do not restructure the shell (CSS tokens, `buildNav`/`toggleTheme`/
    `setLang` scripts) per client — only section bodies, hero text, and title/branding
    change.
- `assets/validate-proposal.py` — the Phase 4 mechanical validator (run via `python`).
  Checks only what's objectively countable: no leftover placeholders, no
  internal-anchor citations, citation/Sources & Citation consistency, required-section
  coverage, `.assess` presence on `recommendations`, `findings.json`
  consistency, that the real template shell was used, that a real spread of
  Chart.js canvases + static diagram blocks is present (not a text/table-only file), that
  citations use the hover-card markup, and that no `<CLIENT NAME>` placeholder or
  stale "Odoo 19" sidebar-brand text is left unfilled anywhere (including inside
  `buildNav()`'s JS string, not just the visible hero/`<title>`). It
  does not check factual accuracy, content depth, or whether a chart's data is any
  good — those stay judgment calls. See `phase4-review.md` for when to run it.
