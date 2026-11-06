"""Ghép template + playbook + lead. Dùng: python <skill>/tools/build.py <slug> [--url URL | --check]"""
import argparse, html, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(os.environ.get("JOURNEY_ROOT") or Path(__file__).resolve().parents[1])
# Repo có leads/ trong journey/; bản đóng gói thì không, dữ liệu lead nằm ở ~/sales-journey.
LEADS = Path(os.environ.get("JOURNEY_LEADS") or (ROOT / "leads" if (ROOT / "leads").is_dir() else Path.home() / "sales-journey"))
# Bản đóng gói mang theo luật kiểm của portal ở tools/portal.
# shortcut: fallback về bản clone portal trên máy Anthony (test của repo dựa vào nó), bỏ khi repo cũng dùng tools/portal.
PORTAL_DIR = os.environ.get("PORTAL_DIR") or str(ROOT / "tools" / "portal" if (ROOT / "tools" / "portal").is_dir() else r"C:\Anthony\proposal-portal")
TEMPLATE = (ROOT / "template" / "journey.html").read_text(encoding="utf-8")


def _script(id_, data):
    # Đổi "<" thành \u003c để chuỗi trong JSON không đóng được thẻ <script>.
    return f'<script type="application/json" id="{id_}">' + json.dumps(data, ensure_ascii=False).replace("<", "\\u003c") + "</script>"


def portal_cli():
    """journey-check.mjs của portal. Thiếu file của portal thì thoát mã 2: lỗi cài đặt, không phải lỗi của lead."""
    p = Path(PORTAL_DIR)
    if not all((p / f).is_file() for f in ("lib/lead.mjs", "tools/journey-check.mjs")):
        print(f"Không thấy lib/lead.mjs và tools/journey-check.mjs trong PORTAL_DIR={PORTAL_DIR}. Clone proposal-portal vào đó "
              "(hoặc đặt PORTAL_DIR) và checkout nhánh feat/lead-contracts (sau khi merge: preview). Lỗi cài đặt, không phải lỗi lead.",
              file=sys.stderr)
        raise SystemExit(2)
    return p / "tools" / "journey-check.mjs"


def check(lead_path, slug, playbook_path=None, record_path=None):
    """Kiểm lead, playbook và record.json (mặc định nằm cạnh lead.json, lead.profile phải khớp facts) bằng luật JS
    của portal. Trả về danh sách lỗi; thiếu record.json là một lỗi. Thiếu node, thiếu portal hay CLI lỗi dùng thì dừng."""
    cli = portal_cli()
    pb = playbook_path or ROOT / "playbook" / "playbook.json"
    rec = Path(record_path or Path(lead_path).parent / "record.json")
    missing = [] if rec.is_file() else [f"thiếu record.json ({rec}): lead nào cũng cần hồ sơ, lead mới thì dựng khung record.json trước"]
    cmd = ["node", str(cli), "--playbook", str(pb), "--lead", str(lead_path), "--slug", slug,
           "--template", str(ROOT / "template" / "journey.html"), "--json"] + ([] if missing else ["--record", str(rec)])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", shell=False)
    except FileNotFoundError:
        raise SystemExit("Không tìm thấy node. Cài Node.js rồi chạy lại.")
    if r.returncode == 2:
        raise SystemExit(f"journey-check.mjs báo lỗi cách dùng (kiểm PORTAL_DIR={PORTAL_DIR}): {r.stderr.strip()}")
    try:
        return json.loads(r.stdout)["errors"] + missing
    except (ValueError, KeyError):
        raise SystemExit(f"journey-check.mjs trả kết quả không đọc được (mã {r.returncode}): {r.stdout}{r.stderr}")


def render(pb, ld):
    """Ghép template với playbook và lead thành trang HTML. Không validate, không đọc hay ghi file."""
    for marker in ("<!--@PB@-->", "<!--@LD@-->", "@@TITLE@@"):
        if TEMPLATE.count(marker) != 1:
            raise SystemExit(f"template phải có đúng một {marker}")
    return (TEMPLATE.replace("@@TITLE@@", html.escape(ld["lead"]["company"]) + " · Sales Journey")
                    .replace("<!--@PB@-->", _script("pb", pb))
                    .replace("<!--@LD@-->", _script("ld", ld)))


def build(slug, url=None):
    pb = json.loads((ROOT / "playbook" / "playbook.json").read_text(encoding="utf-8"))
    ld = json.loads((LEADS / slug / "lead.json").read_text(encoding="utf-8"))
    errs = check(LEADS / slug / "lead.json", slug)
    if errs:
        raise SystemExit("Không build được:\n" + "\n".join(errs))
    out = LEADS / slug / "journey.html"
    out.write_text(render(pb, ld), encoding="utf-8")
    idx_path = LEADS / "index.json"
    idx = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else {}
    row = idx.get(slug, {})
    row.update(company=ld["lead"]["company"], owner=ld["lead"]["owner"],
               version=ld["version"], playbook_version=ld["playbook_version"])
    if url:
        row["url"] = url
    idx[slug] = row
    idx_path.write_text(json.dumps(idx, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--url")
    ap.add_argument("--check", action="store_true", help="chỉ kiểm, không ghi file; mã 1 nếu có lỗi")
    a = ap.parse_args()
    if a.check:
        errs = check(LEADS / a.slug / "lead.json", a.slug)
        print("\n".join(errs) or "OK")
        sys.exit(1 if errs else 0)
    print(build(a.slug, a.url))
