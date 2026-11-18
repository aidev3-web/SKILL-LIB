# -*- coding: utf-8 -*-
"""Run the builder on every edge-case profile in tests/cases.json and report the lapses.

    python -I -X utf8 test_suite.py [--shots] [--only name,name] [--work DIR]

Each case is built from scratch (deck.json regenerated) into <work>/<case>/. The suite checks: the build and
check_deck pass, the "must" strings are in the visible text and the "must_not" strings are not; with --shots it also
runs shots.py (frame, clipped text, glyph clips, arrow walk, print, phone). Run it after ANY template or builder change.
"""
import argparse, json, pathlib, re, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
import check_deck  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shots', action='store_true')
    ap.add_argument('--only')
    ap.add_argument('--work', default=str(pathlib.Path.home() / 'ClaudeWork/nextcore-presentation/tests'))
    a = ap.parse_args()
    cases = json.loads((SKILL / 'tests/cases.json').read_text(encoding='utf-8'))['cases']
    only = set(a.only.split(',')) if a.only else None
    fails = 0
    for name, cs in cases.items():
        if only and name not in only:
            continue
        d = pathlib.Path(a.work) / name
        shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
        (d / 'client-profile.json').write_text(json.dumps(cs['profile'], ensure_ascii=False, indent=2), encoding='utf-8')
        if cs.get('logo_from'):
            shutil.copy(SKILL / cs['logo_from'], d / cs['profile']['brand']['logo'])
        r = subprocess.run([sys.executable, '-I', '-X', 'utf8', str(HERE / 'build_deck.py'), str(d), '--regen', '--status', 'Sample'],
                           capture_output=True, text=True, encoding='utf-8')
        out = (r.stdout + r.stderr).strip()
        problems = [] if r.returncode == 0 else ['build/check failed: ' + ' | '.join(l.strip() for l in out.splitlines()[-6:])]
        html = d / 'out/presentation.html'
        if html.exists():
            txt = re.sub(r'\s+', ' ', check_deck.visible_text(html.read_text(encoding='utf-8')))
            problems += [f'missing {m!r}' for m in cs.get('must', []) if m not in txt]
            problems += [f'contains {m!r}' for m in cs.get('must_not', []) if re.search(re.escape(m), txt)]
            if a.shots:
                s = subprocess.run([sys.executable, '-I', '-X', 'utf8', str(HERE / 'shots.py'), str(html), '--name', name],
                                   capture_output=True, text=True, encoding='utf-8')
                problems += [l.strip() for l in s.stdout.splitlines() if 'ERROR' in l]
        print(f'{name:10s}', 'PASS' if not problems else 'FAIL')
        for p in problems:
            print('    -', p)
        fails += bool(problems)
    print(f'{fails} case(s) failed')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
