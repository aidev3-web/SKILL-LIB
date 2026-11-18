# -*- coding: utf-8 -*-
"""Checks on a built NextCore presentation (the words a client sees, the alt/aria text and the page source).

    python -I -X utf8 check_deck.py <presentation.html> [--deck deck.json]

1. House claims (content-rules of technext-presentations + owner rules in memory):
   Odoo never "free"; no BIR guarantees and no BIR-ready/compliant/accredited/certified; "Odoo Ready Partner",
   never certified/Gold/Silver, and in Singapore only; British "adviser"; no WhatsApp or number; sales@ never a link;
   none of the banned brand words (world-class, one-stop shop, trusted advisor, vendor, reseller).
2. No other client's name (from the folder names in 01. Client Folder) and no sample company of another deck.
3. One file only: no external URL loaded (fonts, images, scripts), no leftover {{ }} token.
4. Only the UI asked for: no presenter view, TV mode, settings, share/print/download buttons, service worker or storage.
Returns True when every check passes.
"""
import argparse, html as H, json, os, pathlib, re, sys

CLIENT_ROOT = r'G:\Shared drives\Marketing\01. Client Folder'
SKIP = {'bin', 'old', 'new folder'}
DROP = r"\b(Website|Websites|Presentations?|Product Catalogue|Videos?|PH|Event Marketing|flipbook)\b"
OTHER_SAMPLES = ['Kestrel & Pine', 'Sunbird Clinics', 'Lumen Trading', 'Hitachi', 'GERP', 'Makati', 'South Star', "Liah"]

RULES = [
    (r'\bfree\b', 'Odoo is never "free"'),
    (r'BIR[\s-]*(ready|compliant|accredited|certified|approved)', 'no BIR-ready/compliant/accredited claims'),
    (r'\b(guarantee[ds]?|we confirm (?:you|your|whether))', 'no guarantees'),
    (r'\baccredit', 'no accreditation claims'),
    (r'certified|gold partner|silver partner', 'say "Odoo Ready Partner", never certified/Gold/Silver'),
    (r'partner[^.]{0,40}philippines|philippines?[^.]{0,20}partner', 'Odoo Partner in Singapore only'),
    (r'\badvisor', 'British "adviser"'),
    (r'wa\.me|\+65\s?8839|whats\s?app (?:us|me|our)|message us on whats\s?app', 'no WhatsApp links or number'),
    (r'mailto:', 'sales@ is plain text, never a link'),
    (r'world-class|one-stop|trusted advisor|\b(?:we are|we\'re|as) an? (?:vendor|reseller|agency)\b|\breseller\b|\bleading (?:provider|partner|company|expert)', 'banned brand words'),
    (r'\bISO\s?27001', 'not ISO 27001 certified'),
]
UI_BANS = [
    (r'presenter|BroadcastChannel', 'presenter view'), (r'is-tv|kiosk', 'TV / kiosk mode'),
    (r'serviceWorker|localStorage|sessionStorage', 'storage / offline worker'),
    (r'<button[^>]*>(?:[^<]|<(?!/button))*\b(share|print|download|settings|full ?screen|menu)\b', 'extra buttons'),
    (r'data-home|data-shared|launcher', 'launcher / share-link machinery'),
]


def client_marks(own):
    marks, own = set(), [o.lower() for o in own if o]
    if not os.path.isdir(CLIENT_ROOT):
        return marks
    for n in os.listdir(CLIENT_ROOT):
        m = re.match(r'^\d+\.\s+(.*)$', n)
        if not m:
            continue
        nm = re.sub(r'\(.*?\)', '', m.group(1))
        nm = re.sub(DROP, '', nm, flags=re.I)
        nm = re.sub(r'\s+', ' ', nm).strip(' &-')
        if not nm or nm.lower() in SKIP or any(o in nm.lower() or nm.lower().split()[0] in o for o in own):
            continue
        words = nm.split()
        w0 = re.sub(r"['\u2019]s$", '', words[0])
        marks.add(' '.join(words[:2]) if len(words) > 1 else w0)
        if (w0.isupper() and len(w0) >= 3) or len(w0) >= 7:
            marks.add(w0)
    return marks


def visible_text(src):
    body = re.sub(r'<script\b.*?</script>|<style\b.*?</style>', ' ', src, flags=re.S | re.I)
    attrs = ' '.join(re.findall(r'(?:alt|aria-label|title|content)="([^"]*)"', src))
    data = ' '.join(re.findall(r'<script type="application/json"[^>]*>(.*?)</script>', src, flags=re.S))
    return H.unescape(re.sub(r'<[^>]+>', ' ', body) + ' ' + attrs + ' ' + data)


def check(path, deck=None, quiet=False):
    src = pathlib.Path(path).read_text(encoding='utf-8')
    txt = re.sub(r'\s+', ' ', visible_text(src))
    fails, rows = [], []
    claims = re.sub(r'We are not affiliated with[^.]*\.', ' ', txt)   # the required disclaimer is not a claim
    for rx, why in RULES:
        hits = sorted({m.group(0) for m in re.finditer(rx, claims, re.I)})
        if hits:
            fails.append(f'{why}: {hits}')
    own = []
    if deck:
        c = deck.get('client', {})
        own = [c.get('name'), c.get('short'), c.get('city')]
    for mark in sorted(client_marks(own)) + OTHER_SAMPLES:
        if re.search(r'\b' + re.escape(mark) + r'\b', txt, re.I) and not any(mark.lower() in (o or '').lower() for o in own):
            fails.append(f'another client or sample name in the deck: {mark!r}')
    ext = sorted(set(re.findall(r'(?:src|href)=["\'](https?:[^"\']+)', src)) | set(re.findall(r'url\((https?:[^)]+)\)', src)))
    if ext:
        fails.append(f'loads from outside the file: {ext}')
    if re.search(r'\{\{\s*[\w.]|[\w.]\s*\}\}|\[\[|\]\]', txt):
        fails.append('a leftover {{ }} or [[ ]] marker in the text')
    leaks = sorted({m.group(0) for m in re.finditer(r'\bTODO\b|\bTBD\b|lorem ipsum|deck\.json|client-profile|[A-Z]:\\\\|ClaudeWork|_note|\bundefined\b|\bNaN\b|\bNone\b|\bnull\b', txt, re.I)})
    if leaks:
        fails.append(f'internal text leaked onto the slides: {leaks}')
    for rx, why in UI_BANS:
        if re.search(rx, src, re.I):
            fails.append(f'UI not asked for ({why}): /{rx}/')
    country = (deck or {}).get('country', 'PH')
    if country != 'PH' and re.search(r'BIR', txt):
        fails.append(f'BIR wording in a {country} deck: BIR is the Philippine tax authority')
    if re.search(r'BIR', txt) and 'not affiliated' not in txt:
        fails.append('BIR is mentioned but the not-affiliated disclaimer is missing')
    if re.search(r'1 users', txt):
        fails.append('"1 users": use the singular')
    n_slides = len(re.findall(r'<section class="slide', src))
    if n_slides != 6:
        fails.append(f'{n_slides} slides, expected 6')
    hl = re.findall(r'<h[12][^>]*>(.*?)</h[12]>', src, flags=re.S)
    for h in hl:
        k = h.count('class="hl"')
        if k != 1:
            fails.append(f'headline needs exactly one marker phrase, has {k}: {re.sub("<[^>]+>", "", h)[:60]}')
    if not quiet:
        print(f'check {pathlib.Path(path).name}: {len(src) // 1024} KB, {n_slides} slides, {len(hl)} headlines')
        for f in fails:
            print('  FAIL', f)
        print('  checks:', 'PASS' if not fails else f'{len(fails)} failed')
    return not fails


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    ap.add_argument('--deck')
    a = ap.parse_args()
    d = json.loads(pathlib.Path(a.deck).read_text(encoding='utf-8')) if a.deck else None
    sys.exit(0 if check(a.html, d) else 1)
