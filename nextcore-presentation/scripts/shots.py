# -*- coding: utf-8 -*-
"""Screenshot a built NextCore presentation in headless Chrome and run the layout checks.

    python -I -X utf8 shots.py <presentation.html> [--out DIR] [--name nextcore] [--wait 2.8]

Writes, in <out> (default: <html dir>/shots):
  01-technext-<name>-deck-who-technext-is.png ... 06-technext-<name>-deck-next-step.png   1600x900, every slide finished
  07-technext-<name>-deck-phone.png        a phone held upright (390x844, touch): the deck turns sideways
  qa/NN-first-build.png                    slides with builds, at their first build (what the room sees on arrival)
  qa/sheet.jpg                             contact sheet of the six finished slides
Checks: script errors, text outside the 1600x900 stage or in the footer band, clipped one-line text, every slide
finished at its last build. Exit 1 on an ERROR.
"""
import argparse, pathlib, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _cdp import Chrome  # noqa: E402
from PIL import Image  # noqa: E402

SLIDES = ['who-technext-is', 'what-we-heard', 'odoo-apps', 'nextsprint', 'phases-timeline', 'next-step']

MEASURE = r"""
(() => {
  const out = [], st = document.querySelector('.stage'), sr = st.getBoundingClientRect(), k = sr.width / 1600;
  const sl = Deck.slides[Deck.index];
  sl.querySelectorAll('*').forEach(el => {
    if (el.closest('.s-chrome,.s-foot,.sr-only,svg,.mx-w')) return;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return;
    if (!el.childNodes.length || ![...el.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim())) return;
    const r = el.getBoundingClientRect();
    const x0 = (r.left - sr.left) / k, y0 = (r.top - sr.top) / k, x1 = (r.right - sr.left) / k, y1 = (r.bottom - sr.top) / k;
    const name = el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : '');
    const txt = el.textContent.trim().slice(0, 40);
    if (x0 < 110 || x1 > 1490 || y0 < 96 || y1 > 842) out.push(['ERROR', 'outside the content frame', name, txt, [x0, y0, x1, y1].map(Math.round)]);
    if (el.scrollWidth > el.clientWidth + 1 && cs.overflow !== 'visible' && cs.whiteSpace === 'nowrap') out.push(['ERROR', 'clipped text', name, txt]);
  });
  const leaves = [...sl.querySelectorAll('h1,h2,h3,p,li > b,dt,dd,.st-n,.st-d,.st-r,.who,em,.lg-h,.fig-n,.fig-l,.ms-l,.tag,.illus,.legend > span,.g-key,.users,.meta > span')]
    .filter(e => { const cs = getComputedStyle(e); return cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > 0 && e.textContent.trim() && !e.closest('.s-chrome,.s-foot,.sr-only,.rec'); })
    .map(e => [e, e.getBoundingClientRect()]);
  for (let a = 0; a < leaves.length; a++) for (let b = a + 1; b < leaves.length; b++) {
    const [ea, ra] = leaves[a], [eb, rb] = leaves[b];
    if (ea.contains(eb) || eb.contains(ea)) continue;
    const w = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), h = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
    if (w > 3 && h > 3) out.push(['ERROR', 'text on text', ea.textContent.trim().slice(0, 30), eb.textContent.trim().slice(0, 30), [Math.round(w), Math.round(h)]]);
  }
  const hidden = [...sl.querySelectorAll('[data-step]')].filter(e => e.dataset.until == null && !e.classList.contains('is-shown')).length;
  if (hidden) out.push(['ERROR', hidden + ' build(s) not shown at the last step']);
  return out;
})()
"""


GLYPH_BOXES = r"""
(() => [...Deck.slides[Deck.index].querySelectorAll('.mx-words, .lg-q, .st-n, .sp h3, .g-l b, .nx-steps h3, .fig-n, .rec-id, .bar')]
  .map(e => { const r = e.getBoundingClientRect(); return [e.className || e.tagName, Math.max(0, r.left - 24), Math.max(0, r.top - 24), r.width + 48, r.height + 48]; }))()
"""
UNCLIP = ("(() => { const s = document.createElement('style'); s.id = 'unclip'; s.textContent = "
          "'.mx-w{clip-path:none!important} *{overflow:visible!important}'; document.head.appendChild(s); })()")


def glyph_clip(c, i, qa):
    """Display type cut by a mask or an overflow clip (owner rule, 7 Nov 2026): shoot each title with and without
    the word masks and overflow clips; any pixel that changes is ink that was cut."""
    from PIL import ImageChops
    boxes = c.ev(GLYPH_BOXES) or []
    before = [c.shot(qa / f'_g{i}_{k}a.png', clip=b[1:]) for k, b in enumerate(boxes)]
    c.ev(UNCLIP); c.sleep(.2)
    bad = 0
    for k, b in enumerate(boxes):
        after = c.shot(qa / f'_g{i}_{k}b.png', clip=b[1:])
        d = ImageChops.difference(Image.open(before[k]).convert('L'), Image.open(after).convert('L')).point(lambda v: 255 if v > 40 else 0)
        n = d.histogram()[255]
        if n > 12:
            print(f'  slide {i + 1:02d} ERROR glyphs clipped in {b[0][:40]!r}: {n} px change when masks are removed')
            bad += 1
    c.ev("document.getElementById('unclip').remove()")
    for p in qa.glob(f'_g{i}_*.png'):
        p.unlink()
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    ap.add_argument('--out')
    ap.add_argument('--name', default='nextcore')
    ap.add_argument('--wait', type=float, default=2.8)
    a = ap.parse_args()
    src = pathlib.Path(a.html).resolve()
    out = pathlib.Path(a.out) if a.out else src.parent / 'shots'
    (out / 'qa').mkdir(parents=True, exist_ok=True)
    url = src.as_uri()
    errors, files = 0, []
    with Chrome(1600, 900) as c:
        c.open(url + '#1', settle=1.0)
        steps = c.ev('Deck.slides.map((s,i)=>{Deck.go(i,0);return +s.dataset.steps||Math.max(0,...[...s.querySelectorAll("[data-step]")].map(e=>+e.dataset.step))})')
        for i, sl in enumerate(SLIDES):
            if steps[i]:
                c.ev(f'Deck.go({(i + 1) % 6},0)'); c.sleep(.4)
                c.ev(f'Deck.go({i},0)'); c.sleep(a.wait)
                c.shot(out / 'qa' / f'{i + 1:02d}-first-build.png')
            c.ev(f'Deck.go({(i + 1) % 6},0)'); c.sleep(.4)
            c.ev(f'Deck.go({i},-1)'); c.sleep(a.wait)
            p = out / f'{i + 1:02d}-technext-{a.name}-deck-{sl}.png'
            c.shot(p); files.append(p)
            for row in c.ev(MEASURE) or []:
                print(f'  slide {i + 1:02d}', *row)
                errors += row[0] == 'ERROR'
            errors += glyph_clip(c, i, out / 'qa')
        # walk the whole deck with the arrow key, as a clicker would, and come back
        c.ev('Deck.go(0,0)'); c.sleep(.5)
        for _ in range(sum(steps) + 6):
            c.call('Input.dispatchKeyEvent', type='keyDown', key='ArrowRight', code='ArrowRight', windowsVirtualKeyCode=39)
            c.call('Input.dispatchKeyEvent', type='keyUp', key='ArrowRight', code='ArrowRight', windowsVirtualKeyCode=39)
            c.sleep(.25)
        end = c.ev('[Deck.index, Deck.step]')
        if end != [5, 0]:
            print('  ERROR arrow walk ended at', end, 'expected the last slide'); errors += 1
        # print (PDF only when the user asks, but it must work): six pages, every one finished, none blank
        c.ev("window.dispatchEvent(new Event('beforeprint'))"); c.sleep(.5)
        pdf = c.pdf(out / 'qa' / 'print-check.pdf')
        try:
            import pymupdf
            d = pymupdf.open(pdf)
            blank = [i + 1 for i, pg in enumerate(d) if not pg.get_text().strip()]
            print(f'  print: {d.page_count} pages' + (f', blank: {blank}' if blank else ''))
            if d.page_count != 6 or blank:
                print('  ERROR print should give 6 finished pages'); errors += 1
            d.close()
        except ImportError:
            print('  print: pymupdf missing, page count not checked')
        if c.errors:
            print('  ERROR script errors:', *sorted(set(c.errors)), sep='\n    '); errors += 1
    with Chrome(390, 844, mobile=True, touch=True) as c:
        c.open(url + '#3', settle=1.0)
        c.ev('Deck.go(2,-1)'); c.sleep(a.wait)
        rot = c.ev("document.querySelector('.deck').classList.contains('is-rotated')")
        p = out / f'07-technext-{a.name}-deck-phone.png'
        c.shot(p); files.append(p)
        print('  phone upright: deck turned' if rot else '  ERROR phone upright: the deck did not turn')
        errors += not rot
        if c.errors:
            print('  ERROR phone script errors:', *sorted(set(c.errors)), sep='\n    '); errors += 1
    sheet = Image.new('RGB', (1600 + 30, 3 * 450 + 40), '#E9E7EE')
    for i, p in enumerate(files[:6]):
        im = Image.open(p).convert('RGB').resize((800, 450), Image.LANCZOS)
        sheet.paste(im, (10 + (i % 2) * 810, 10 + (i // 2) * 460))
    sheet.save(out / 'qa' / 'sheet.jpg', quality=88)
    for p in files:
        print(' ', p.name, Image.open(p).size)
    print('shots:', out, '|', 'PASS' if not errors else f'{errors} ERROR(s)')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
