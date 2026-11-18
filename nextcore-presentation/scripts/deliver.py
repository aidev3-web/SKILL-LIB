# -*- coding: utf-8 -*-
"""File a checked NextCore presentation into the client's Drive folder, md5-verified. Nothing is sent to the client.

    python -I -X utf8 deliver.py <client dir> [--root DIR] [--dry-run]
    python -I -X utf8 deliver.py <client dir> --to "<any folder>" [--name nextcore]   # a flat copy (the builder's own test folder)

Client folder target (same layout as the SLA and Sales Proposal builders):
  01. Client Folder\\NN. <Client>\\04. Presentation\\
      <Client> - TechNext Presentation Rev X.Y (Draft).html
      preview\\0N-technext-<client>-deck-<slide>.png            (the six slides + the phone view)
  01. Client Folder\\NN. <Client>\\_build\\presentation\\       client-profile.json, deck.json, the logo
A different revision already in 04. Presentation is moved, whole, to
  NN. <Client>\\00. old\\Presentation Rev <old> (superseded YYYY-MM-DD)\\
The client folder is found by the short name (or created as the next NN). Every copy is md5-checked and retried once.
Refuses to deliver when check_deck fails, shots are missing, or deck.json / the profile is newer than the HTML.
"""
import argparse, datetime as dt, hashlib, json, os, pathlib, re, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent
CLIENT_ROOT = r'G:\Shared drives\Marketing\01. Client Folder'
SUB = '04. Presentation'
SLIDES = ['who-technext-is', 'what-we-heard', 'odoo-apps', 'nextsprint', 'phases-timeline', 'next-step', 'phone']


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def safe(s):
    return re.sub(r'[<>:"/\\|?*]', '', s).strip().rstrip('.')


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def copy_checked(src, dst, dry):
    print(('WOULD COPY ' if dry else 'COPY ') + str(dst))
    if dry:
        return True
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for _ in (1, 2):   # Drive sync can corrupt a large copy: check and retry once
        shutil.copyfile(src, dst)
        if md5(src) == md5(dst):
            return True
    print('  MD5 MISMATCH', dst)
    return False


def find_client_folder(root, name, short):
    nums, hits = [], []
    for n in os.listdir(root) if os.path.isdir(root) else []:
        m = re.match(r'^(\d+)\.\s+(.*)$', n)
        if not m:
            continue
        nums.append(int(m.group(1)))
        if short.lower() in m.group(2).lower():
            hits.append(n)
    if len(hits) > 1:
        raise SystemExit(f'more than one client folder matches {short!r}: {hits}; pass --folder')
    if hits:
        return os.path.join(root, hits[0]), False
    return os.path.join(root, f'{max(nums, default=0) + 1:02d}. {safe(name)}'), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('client_dir')
    ap.add_argument('--root', default=CLIENT_ROOT)
    ap.add_argument('--folder', help='exact client folder name under --root')
    ap.add_argument('--to', help='flat copy into this folder instead (HTML + NN-technext-<name>-deck-<slide>.png)')
    ap.add_argument('--name', help='preview name part (default: the client short name; the builder test uses nextcore)')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    cdir = pathlib.Path(a.client_dir).resolve()
    D = json.loads((cdir / 'deck.json').read_text(encoding='utf-8-sig'))
    prof = cdir / 'client-profile.json'
    html = cdir / 'out' / 'presentation.html'
    shots = cdir / 'out' / 'shots'
    if not html.exists():
        raise SystemExit('no out/presentation.html: run build_deck.py first')
    newest_src = max(os.path.getmtime(cdir / 'deck.json'), os.path.getmtime(prof))
    if newest_src > os.path.getmtime(html):
        raise SystemExit('deck.json or the profile is newer than the HTML: run build_deck.py and shots.py again')
    sys.path.insert(0, str(HERE))
    import check_deck
    if not check_deck.check(html, D):
        raise SystemExit('check_deck failed: fix and rebuild before delivery')
    C = D['client']
    name_part = a.name or slug(C['short'])
    pre = {}
    for i, sl in enumerate(SLIDES, 1):
        src = next(iter(shots.glob(f'{i:02d}-technext-*-deck-{sl}.png')), None)
        if not src or os.path.getmtime(src) < os.path.getmtime(html):
            raise SystemExit(f'missing or stale shot {i:02d} {sl}: run shots.py after the last build')
        pre[f'{i:02d}-technext-{name_part}-deck-{sl}.png'] = src
    status = {'draft': ' (Draft)', 'sample': ' (Sample)'}.get(str(D.get('status', 'Draft')).lower(), '')
    base = f"{safe(C['name'])} - TechNext Presentation Rev {D['rev']}{status}.html"

    bad = 0
    if a.to:   # flat copy (the builder's own folder on Drive)
        to = pathlib.Path(a.to)
        bad += not copy_checked(html, to / base, a.dry_run)
        for n, src in pre.items():
            bad += not copy_checked(src, to / n, a.dry_run)
        print('files', 1 + len(pre), '| md5 mismatches:', bad, '| dry run' if a.dry_run else '')
        sys.exit(1 if bad else 0)

    client_dir, new = (os.path.join(a.root, a.folder), not os.path.isdir(os.path.join(a.root, a.folder))) if a.folder \
        else find_client_folder(a.root, C['name'], C['short'])
    print('client folder:', client_dir, '(new)' if new else '')
    target = os.path.join(client_dir, SUB)
    rev = str(D['rev'])
    moves = []
    if os.path.isdir(target):   # supersede an older revision: move the whole folder content to 00. old
        olds = set()
        for _, _, fs in os.walk(target):
            for f in fs:
                m = re.search(r'Rev ([\d.]+)', f)
                if m and m.group(1).rstrip('.') != rev:
                    olds.add(m.group(1).rstrip('.'))
        if olds:
            old = sorted(olds, key=lambda v: [int(x) for x in v.split('.') if x.isdigit()])[-1]
            dest = os.path.join(client_dir, '00. old', f'Presentation Rev {old} (superseded {dt.date.today().isoformat()})')
            for r_, _, fs in os.walk(target):
                for f in fs:
                    s = os.path.join(r_, f)
                    moves.append((s, os.path.join(dest, os.path.relpath(s, target))))
    for s, t in moves:
        print(('WOULD MOVE ' if a.dry_run else 'MOVE ') + os.path.relpath(s, client_dir), '->', os.path.relpath(t, client_dir))
        if not a.dry_run:
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.move(s, t)
    bad += not copy_checked(html, os.path.join(target, base), a.dry_run)
    for n, src in pre.items():
        bad += not copy_checked(src, os.path.join(target, 'preview', n), a.dry_run)
    bdir = os.path.join(client_dir, '_build', 'presentation')
    srcs = [prof, cdir / 'deck.json']
    logo = (json.loads(prof.read_text(encoding='utf-8-sig')).get('brand') or {}).get('logo')
    if logo and (cdir / logo).exists():
        srcs.append(cdir / logo)
    for s in srcs:
        bad += not copy_checked(s, os.path.join(bdir, s.name), a.dry_run)
    print('files', 1 + len(pre) + len(srcs), '| moved', len(moves), '| md5 mismatches:', bad, '| dry run' if a.dry_run else '')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
