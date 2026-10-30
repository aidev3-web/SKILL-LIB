#!/usr/bin/env python3
"""Put a finished proposal's card into the TechNext Proposal Library.

Two ways, the first one that is set up is used, and neither ever sends the proposal HTML anywhere (only the card text and the section
list, worked out here from the file):
  1. The library's HTTPS endpoint (nothing to install, no git, no GitHub account, no key). Needs only the address, from the
     environment (PROPOSAL_LIBRARY_URL), from ~/.claude/proposal-library.json ("endpoint") or from library-endpoint.json next to this
     script (the library owner ships it with the skill). Without a key the card goes into the suggestion box: in the owner's "live"
     setting it appears in the library at once with an Auto-added badge, in the "queue" setting it waits for the owner; sending the same
     proposal again refreshes it. With a team key
     (PROPOSAL_LIBRARY_KEY, "key" in the settings or in library-endpoint.json) the card is written straight into the library, marked
     "Needs review" until approved, and an update keeps the card's review state.
  2. A git clone of the library (private GitHub repo aidev3-web/proposal-library, which Vercel deploys from `main`), used only when a
     clone is named (--repo, PROPOSAL_LIBRARY_REPO or "repo" in the settings file). It edits registry.json, rebuilds site/, runs the
     library's Python tests, commits and pushes with the git login the person already has. No token of its own.

  python library_publish.py <proposal folder> --artifact-url https://claude.ai/artifact/<id> --summary "<one honest sentence>" \
         [--meeting-file <proposal>/captures/library-meeting.json] [--status ready] [--by "<name>"] [--title "<title>"] [--repo <clone>] [--dry-run] [--yes] [--no-push] [--trailer "<line>"]

Meeting data (optional): the card can also carry the meeting `minutes` and the four `followups` drafts (the library shows them to all staff
signed in to it). Build the JSON from the finished proposal, then pass it:
  python library_publish.py extract-meeting <proposal folder> [--minutes <minutes.json> | --minutes-record <file>] [--confirmed]   -> <folder>/captures/library-meeting.json
  python library_publish.py check-meeting <file>                                                         (validate only)
  python library_publish.py <proposal folder> --artifact-url ... --meeting-file <folder>/captures/library-meeting.json [--dry-run]

Meeting links that staff added in the library (Google Docs meeting notes, quotation docs, other docs). Needs the address and the team key:
  python library_publish.py links <slug> [--all]       prints {"slug", "count", "links": [...]} as JSON; only links not yet used unless --all
  python library_publish.py mark-link-used <slug> <id> [--used-at <ISO time>] [--dry-run]   marks a link as folded into the proposal
Date, input table (channel, signer, language, source) and draft texts come from the proposal HTML (follow-ups and meeting-minutes sections,
English text, placeholders skipped); summary, decisions and next steps come from captures/meeting-<date>/minutes.json because the minutes
prose in the HTML is free-form. Invalid data exits 2 and nothing is sent.

Settings file ~/.claude/proposal-library.json (all optional):
  {"endpoint": "<https address>", "key": "<team key>", "repo": "<path of a clone>", "mode": "auto" | "ask" | "off", "name": "<who is updating>"}

mode: "auto" (the default) publishes as soon as the checks pass; "ask" stops with exit code 3 until --yes is given, so the caller
can show the record and get a yes; "off" does nothing.

Exit codes: 0 done (or nothing to do), 2 refused or failed (nothing was pushed), 3 needs a yes (mode ask).
It never forces a push and never touches any other repo.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser

REPO_URL = "https://github.com/aidev3-web/proposal-library.git"
REMOTE_RE = re.compile(r"[:/]aidev3-web/proposal-library(\.git)?/?$")
CONFIG = pathlib.Path.home() / ".claude" / "proposal-library.json"
DEFAULT_CLONE = pathlib.Path.home() / ".claude" / "proposal-library-repo"
GENERATED = ("registry.json", "site", "build-manifest.json")


class Refused(Exception):
    pass


def say(msg):
    print(msg, file=sys.stderr)


def git(repo, *args, check=True):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if check and r.returncode != 0:
        raise Refused(f"git {' '.join(args)} failed: {(r.stderr or r.stdout).strip()[:400]}")
    return r


def load_config():
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def ensure_repo(path, may_clone):
    path = pathlib.Path(path).expanduser()
    if not path.exists():
        if not may_clone:
            raise Refused(f"{path} does not exist")
        say(f"cloning the library to {path} (uses your own GitHub login)")
        path.parent.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        r = subprocess.run(["git", "clone", REPO_URL, str(path)], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        if r.returncode != 0:
            raise Refused("could not clone the library. Sign in to GitHub on this machine with an account that can read "
                          f"aidev3-web/proposal-library, then run again. ({r.stderr.strip()[:200]})")
    url = git(path, "remote", "get-url", "origin").stdout.strip()
    if not REMOTE_RE.search(url):
        raise Refused(f"{path} is not a clone of aidev3-web/proposal-library (origin is {url})")
    if git(path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() != "main":
        raise Refused(f"{path} is not on the main branch")
    if git(path, "status", "--porcelain", "--untracked-files=no").stdout.strip():
        raise Refused(f"{path} has uncommitted changes; commit or stash them first")
    git(path, "fetch", "origin", "main")
    if int(git(path, "rev-list", "--count", "origin/main..HEAD").stdout.strip() or 0) > 0:
        raise Refused(f"{path} has commits that are not pushed; push or reset them first")
    git(path, "merge", "--ff-only", "origin/main")
    return path


def load_library(repo):
    spec = importlib.util.spec_from_file_location("build_library", repo / "tools" / "build_library.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["build_library"] = mod
    spec.loader.exec_module(mod)
    return mod


def find_proposal(folder):
    files = sorted(f for f in folder.glob("*-proposal.html") if "artifact" not in f.name and "before" not in f.name and not f.name.startswith("."))
    if not files:
        raise Refused(f"no *-proposal.html in {folder}")
    return files[0]


def iso_date(value):
    """argparse type: a real calendar date written YYYY-MM-DD, returned unchanged."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or ""):
        raise argparse.ArgumentTypeError(f"{value!r} is not a date written YYYY-MM-DD")
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not a real calendar date")
    return value


def add_meeting_fields(rec, a):
    """Optional follow-up fields; only set when given, so older cards keep what they have."""
    if getattr(a, "meeting_date", None):
        rec["meeting_date"] = a.meeting_date
    if getattr(a, "next_followup", None):
        rec["next_followup"] = a.next_followup


# ---------------------------------------------------------------- meeting minutes and follow-up drafts (optional card fields)
# The library card can carry `minutes` and `followups`. They come from a JSON file ({"minutes": ..., "followups": [...]}) that
# `extract-meeting` builds from the finished proposal (+ the Minutes Studio minutes.json) and `--meeting-file` loads. The same limits
# the library enforces are checked here first, so invalid data is never sent. The library shows these to all signed-in staff.
MINUTES_KEYS = {"date", "channel", "signer", "language", "source", "confirmed", "summary", "decisions", "next_steps"}
MINUTES_LIMITS = {"channel": 40, "signer": 80, "language": 40, "source": 120, "summary": 2000}
STEP_KEYS = {"what", "who", "due"}
FOLLOWUP_KEYS = {"key", "date", "drafts"}
FOLLOWUP_ORDER = ["d0", "d1", "d3", "d7"]
FOLLOWUP_OFFSETS = {"d0": 0, "d1": 1, "d3": 3, "d7": 7}
DRAFT_KEYS = {"whatsapp", "viber", "email"}
BAD_CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")  # everything but \n (0a) and \t (09)


def _date_ok(v):
    if not isinstance(v, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return False
    try:
        datetime.date.fromisoformat(v)
    except ValueError:
        return False
    return True


def _text_errors(path, v, limit, errs):
    if not isinstance(v, str):
        errs.append(f"{path}: must be text")
        return
    if not v.strip():
        errs.append(f"{path}: must not be empty")
    if len(v) > limit:
        errs.append(f"{path}: {len(v)} characters, the limit is {limit}")
    if BAD_CONTROL.search(v):
        errs.append(f"{path}: contains control characters (only new line and tab are allowed)")


def validate_meeting(data):
    """List of plain-language problems with a {minutes, followups} object; an empty list means valid. Same limits as the library."""
    errs = []
    if not isinstance(data, dict):
        return ["the meeting file must be a JSON object with 'minutes' and/or 'followups'"]
    for k in data:
        if k not in ("minutes", "followups"):
            errs.append(f"unknown key '{k}' (only 'minutes' and 'followups' are allowed)")
    if "minutes" not in data and "followups" not in data:
        errs.append("the meeting file has neither 'minutes' nor 'followups'")
    m = data.get("minutes")
    if "minutes" in data:
        if not isinstance(m, dict):
            errs.append("minutes: must be an object")
        else:
            for k in m:
                if k not in MINUTES_KEYS:
                    errs.append(f"minutes.{k}: unknown key")
            if "date" not in m:
                errs.append("minutes.date: required (YYYY-MM-DD)")
            elif not _date_ok(m["date"]):
                errs.append(f"minutes.date: {m['date']!r} is not a real date written YYYY-MM-DD")
            for k, lim in MINUTES_LIMITS.items():
                if k in m:
                    _text_errors(f"minutes.{k}", m[k], lim, errs)
            if "confirmed" in m and not isinstance(m["confirmed"], bool):
                errs.append("minutes.confirmed: must be true or false")
            dec = m.get("decisions", [])
            if not isinstance(dec, list):
                errs.append("minutes.decisions: must be a list")
            else:
                if len(dec) > 20:
                    errs.append(f"minutes.decisions: {len(dec)} items, the limit is 20")
                for i, d in enumerate(dec, 1):
                    _text_errors(f"minutes.decisions[{i}]", d, 300, errs)
            steps = m.get("next_steps", [])
            if not isinstance(steps, list):
                errs.append("minutes.next_steps: must be a list")
            else:
                if len(steps) > 20:
                    errs.append(f"minutes.next_steps: {len(steps)} items, the limit is 20")
                for i, s in enumerate(steps, 1):
                    p = f"minutes.next_steps[{i}]"
                    if not isinstance(s, dict):
                        errs.append(f"{p}: must be an object")
                        continue
                    for k in s:
                        if k not in STEP_KEYS:
                            errs.append(f"{p}.{k}: unknown key")
                    if "what" not in s:
                        errs.append(f"{p}.what: required")
                    else:
                        _text_errors(f"{p}.what", s["what"], 300, errs)
                    if "who" in s:
                        _text_errors(f"{p}.who", s["who"], 80, errs)
                    if "due" in s and s["due"] is not None and not _date_ok(s["due"]):
                        errs.append(f"{p}.due: {s['due']!r} is not a real date written YYYY-MM-DD (or null)")
    fu = data.get("followups")
    if "followups" in data:
        if not isinstance(fu, list):
            errs.append("followups: must be a list")
        else:
            if len(fu) > 4:
                errs.append(f"followups: {len(fu)} entries, the limit is 4")
            seen = []
            for i, f in enumerate(fu, 1):
                p = f"followups[{i}]"
                if not isinstance(f, dict):
                    errs.append(f"{p}: must be an object")
                    continue
                for k in f:
                    if k not in FOLLOWUP_KEYS:
                        errs.append(f"{p}.{k}: unknown key")
                key = f.get("key")
                if key not in FOLLOWUP_ORDER:
                    errs.append(f"{p}.key: {key!r} must be one of d0, d1, d3, d7")
                elif key in seen:
                    errs.append(f"{p}.key: '{key}' is used twice")
                else:
                    if seen and FOLLOWUP_ORDER.index(key) < FOLLOWUP_ORDER.index(seen[-1]):
                        errs.append(f"{p}.key: '{key}' is out of order (must be d0, d1, d3, d7)")
                    seen.append(key)
                if "date" in f and f["date"] is not None and not _date_ok(f["date"]):
                    errs.append(f"{p}.date: {f['date']!r} is not a real date written YYYY-MM-DD (or null)")
                drafts = f.get("drafts")
                if not isinstance(drafts, dict):
                    errs.append(f"{p}.drafts: must be an object")
                    continue
                for k, v in drafts.items():
                    q = f"{p}.drafts.{k}"
                    if k not in DRAFT_KEYS:
                        errs.append(f"{q}: unknown channel (only whatsapp, viber, email)")
                    elif k == "email":
                        if not isinstance(v, dict):
                            errs.append(f"{q}: must be an object with subject and body")
                            continue
                        for kk in v:
                            if kk not in ("subject", "body"):
                                errs.append(f"{q}.{kk}: unknown key")
                        _text_errors(f"{q}.subject", v.get("subject"), 200, errs)
                        _text_errors(f"{q}.body", v.get("body"), 4000, errs)
                    else:
                        _text_errors(q, v, 2000, errs)
    return errs


def load_meeting_file(path):
    """Read and validate a meeting JSON file; raises Refused with every problem listed when it is not valid."""
    p = pathlib.Path(path).expanduser()
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except OSError as e:
        raise Refused(f"cannot read the meeting file {p}: {e}")
    except ValueError as e:
        raise Refused(f"the meeting file {p} is not valid JSON: {e}")
    errs = validate_meeting(data)
    if errs:
        raise Refused(f"the meeting file {p} is not valid, nothing was sent:\n  - " + "\n  - ".join(errs[:30]))
    return data


def planned_date(meeting_date, offset):
    """Meeting date + offset days; Saturday and Sunday move to Monday (same rule as the follow-ups section's script)."""
    d = datetime.date.fromisoformat(meeting_date) + datetime.timedelta(days=offset)
    if d.weekday() == 5:
        d += datetime.timedelta(days=2)
    elif d.weekday() == 6:
        d += datetime.timedelta(days=1)
    return d.isoformat()


def add_meeting_data(rec, a):
    """--meeting-file: put `minutes` and `followups` into the record (both transports). A part the file lacks leaves the card's own."""
    path = getattr(a, "meeting_file", None)
    if not path:
        return
    data = load_meeting_file(path)
    for k in ("minutes", "followups"):
        if k in data:
            rec[k] = data[k]
    if "minutes" in data and not getattr(a, "meeting_date", None):
        rec["meeting_date"] = data["minutes"]["date"]


class _MeetingScan(HTMLParser):
    """Reads the `meeting-minutes` input table and the `follow-ups` drafts out of a finished proposal (stdlib html.parser only)."""
    VOID = {"input", "br", "hr", "img", "meta", "link"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.sec, self.mdate = [], None, ""
        self.row = None        # {"cells": [{"en": str, "vi": str, "any": str}]}
        self.rows = []         # table rows of the meeting-minutes section
        self.draft = None      # (tab, channel) of the open .fu-draft
        self.drafts = {}       # (tab, channel) -> {"text": str, "subject": str or None}
        self.in_ta = False
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag not in self.VOID:
            self.stack.append((tag, cls))
        if tag == "section":
            self.sec = a.get("id")
            if self.sec == "follow-ups":
                self.mdate = (a.get("data-meeting-date") or "").strip()
        if tag == "div" and "fu-draft" in cls and self.sec == "follow-ups":
            self.draft = (a.get("data-tab"), a.get("data-ch"))
            self.drafts.setdefault(self.draft, {"text": "", "subject": None})
        if tag == "input" and "fu-subject" in cls and self.draft:
            self.drafts[self.draft]["subject"] = a.get("value") or ""
        if tag == "textarea" and "fu-text" in cls and self.draft:
            self.in_ta = True
            self.drafts[self.draft]["text"] = ""
        if self.sec == "meeting-minutes":
            if tag == "tr":
                self.row = {"cells": []}
            elif tag == "td" and self.row is not None:
                self.row["cells"].append({"en": "", "vi": "", "any": ""})
            elif tag == "span" and "t-en" in cls:
                self.lang = "en"
            elif tag == "span" and "t-vi" in cls:
                self.lang = "vi"

    def handle_endtag(self, tag):
        cls = []
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                cls = self.stack[i][1]
                del self.stack[i:]
                break
        if tag == "textarea":
            self.in_ta = False
        if tag == "section":
            self.sec, self.draft = None, None
        if tag == "span" and self.lang and ("t-en" in cls or "t-vi" in cls):
            self.lang = None
        if tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.in_ta and self.draft:
            self.drafts[self.draft]["text"] += data
        elif self.sec == "meeting-minutes" and self.row is not None and self.row["cells"]:
            c = self.row["cells"][-1]
            c["any"] += data
            if self.lang:
                c[self.lang] += data


INPUT_ROWS = {"recording transcript": "source", "meeting date": "date", "channel": "channel", "signer": "signer", "language": "language"}


def _clean(s):
    return re.sub(r"[ \t]+\n", "\n", s.replace("\r\n", "\n").replace("\r", "\n")).strip()


def extract_html_meeting(html_path):
    """(meeting date, input fields, drafts) read from a proposal HTML. Placeholders are skipped. Nothing is invented."""
    scan = _MeetingScan()
    scan.feed(pathlib.Path(html_path).read_text(encoding="utf-8", errors="replace"))
    fields = {}
    for row in scan.rows:
        if len(row["cells"]) < 2:
            continue
        label = _clean(row["cells"][0]["en"] or row["cells"][0]["any"]).lower()
        key = INPUT_ROWS.get(label)
        value = _clean(row["cells"][1]["en"] or row["cells"][1]["any"])
        if key and value and "PLACEHOLDER" not in value.upper():
            fields[key] = re.sub(r"\s+", " ", value)
    return scan.mdate, fields, scan.drafts


def build_followups(meeting_date, drafts, warn):
    out = []
    for tab in FOLLOWUP_ORDER:
        d = {}
        for ch, name in (("wa", "whatsapp"), ("viber", "viber")):
            t = _clean((drafts.get((tab, ch)) or {}).get("text", ""))
            if t and "PLACEHOLDER" not in t.upper():
                d[name] = t
            elif t:
                warn(f"{tab} {name}: still a placeholder, skipped")
        em = drafts.get((tab, "email")) or {}
        subj, body = _clean(em.get("subject") or ""), _clean(em.get("text", ""))
        if subj and body and "PLACEHOLDER" not in (subj + body).upper():
            d["email"] = {"subject": subj, "body": body}
        elif subj or body:
            warn(f"{tab} email: subject or body is still a placeholder or empty, skipped")
        if d:
            out.append({"key": tab, "date": planned_date(meeting_date, FOLLOWUP_OFFSETS[tab]) if meeting_date else None, "drafts": d})
    return out


MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
                                      "november", "december"], 1)}


def _due(text):
    """A date only when the text states one in full ('2026-11-06' or '6 November 2026'); 'TBC' and the like give None."""
    t = str(text or "")
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", t)
    if m and _date_ok(m.group(1)):
        return m.group(1)
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})\b", t)
    if m and m.group(2).lower() in MONTHS:
        try:
            return datetime.date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1))).isoformat()
        except ValueError:
            return None
    return None


def extract_minutes_json(path, warn):
    """summary, decisions and next steps from Minutes Studio's minutes.json (a document spec: description[], meeting_details[], blocks[])."""
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"))
    if isinstance(data, dict) and "blocks" not in data and isinstance(data.get("minutes"), dict):
        data = data["minutes"]
    if not isinstance(data, dict):
        raise Refused(f"{path} is not a minutes.json object")
    blocks = [b for b in data.get("blocks", []) if isinstance(b, dict)]
    summary, in_status = "", False
    for b in blocks:
        if b.get("type") in ("h1", "h2"):
            in_status = bool(re.search(r"status at a glance|summary|overview", str(b.get("text", "")), re.I))
        elif in_status and b.get("type") == "p" and b.get("text"):
            summary += (" " if summary else "") + str(b["text"]).strip()
        elif in_status and b.get("type") == "bullets":
            summary += (" " if summary else "") + " ".join(str(x).strip() for x in b.get("items", []))
    if not summary:
        desc = data.get("description") or (data.get("cover") or {}).get("description") or []
        summary = " ".join(str(x).strip() for x in desc if str(x).strip())
    if len(summary) > 2000:
        warn("summary is longer than 2000 characters and was cut at a word boundary")
        summary = summary[:1999].rsplit(" ", 1)[0] + "…"
    decisions, steps = [], []
    for b in blocks:
        if b.get("type") == "decisions":
            decisions += [str(i.get("text", "")).strip() for i in b.get("items", []) if isinstance(i, dict) and str(i.get("text", "")).strip()]
        elif b.get("type") == "actions":
            for i in b.get("items", []):
                if not isinstance(i, dict) or not str(i.get("action", "")).strip():
                    continue
                s = {"what": str(i["action"]).strip()}
                who = str(i.get("owner") or "").strip()
                if who and who.upper() not in ("TBC", "UNKNOWN", "N/A"):
                    s["who"] = who
                s["due"] = _due(i.get("target"))
                steps.append(s)
    details = {str(r[0]).strip().lower(): str(r[1]).strip() for r in data.get("meeting_details", []) if isinstance(r, list) and len(r) >= 2}
    return {"summary": summary, "decisions": decisions, "next_steps": steps, "date_hint": _due(details.get("date"))}


def newest_minutes_json(folder, meeting_date):
    found = sorted(folder.glob("captures/meeting-*/minutes.json"))
    if meeting_date:
        for f in found:
            if f.parent.name == f"meeting-{meeting_date}":
                return f
    return found[-1] if found else None


def extract_meeting(folder_or_html, minutes_path=None, confirmed=False, warn=say, minutes_record=None):
    """The {minutes, followups} object for a finished proposal. Drafts, meeting date and the input table come from the proposal HTML;
    summary, decisions and next steps come from the captures minutes.json (the proposal's meeting-minutes prose is free-form, so it is not parsed)."""
    p = pathlib.Path(folder_or_html).resolve()
    html = p if p.is_file() else find_proposal(p)
    folder = html.parent
    mdate, fields, drafts = extract_html_meeting(html)
    if minutes_record:  # a hand-written record in the library's `minutes` shape (for example from Google Docs notes): used as is, validated
        try:
            rec = json.loads(pathlib.Path(minutes_record).read_text(encoding="utf-8-sig"))
        except OSError as e:
            raise Refused(f"cannot read the minutes record {minutes_record}: {e}")
        except ValueError as e:
            raise Refused(f"the minutes record {minutes_record} is not valid JSON: {e}")
        if not isinstance(rec, dict):
            raise Refused("the minutes record must be a JSON object in the library minutes shape")
        if confirmed:
            rec["confirmed"] = True
        rec.setdefault("confirmed", False)
        out = {"minutes": rec, "followups": build_followups(rec["date"] if _date_ok(rec.get("date")) else (mdate if _date_ok(mdate) else None), drafts, warn)}
        errs = validate_meeting(out)
        if errs:
            raise Refused("the minutes record is not valid, nothing was written:\n  - " + "\n  - ".join(errs[:30]))
        return out
    mj = pathlib.Path(minutes_path) if minutes_path else newest_minutes_json(folder, mdate or fields.get("date"))
    mdata = None
    if mj and mj.exists():
        try:
            mdata = extract_minutes_json(mj, warn)
        except ValueError as e:
            raise Refused(f"{mj} is not valid JSON: {e}")
    elif minutes_path:
        raise Refused(f"{minutes_path} does not exist")
    else:
        warn("no captures/meeting-*/minutes.json found: the minutes part has only the date and the input table, no summary, decisions or next steps")
    date = mdate if _date_ok(mdate) else (fields.get("date") if _date_ok(fields.get("date", "")) else None)
    if not date and mj:
        m = re.fullmatch(r"meeting-(\d{4}-\d{2}-\d{2})", mj.parent.name)
        date = (m.group(1) if m and _date_ok(m.group(1)) else None) or (mdata or {}).get("date_hint")
    if not date:
        raise Refused("no meeting date: set data-meeting-date on the follow-ups section (YYYY-MM-DD) first")
    minutes = {"date": date}
    for k in ("channel", "signer", "language", "source"):
        if fields.get(k):
            minutes[k] = fields[k]
    minutes["confirmed"] = bool(confirmed)
    if mdata:
        if mdata["summary"]:
            minutes["summary"] = mdata["summary"]
        minutes["decisions"] = mdata["decisions"]
        minutes["next_steps"] = mdata["next_steps"]
    out = {"minutes": minutes, "followups": build_followups(date, drafts, warn)}
    errs = validate_meeting(out)
    if errs:
        raise Refused("the extracted meeting data is not valid, nothing was written:\n  - " + "\n  - ".join(errs[:30]))
    return out


def meeting_cli(argv):
    ap = argparse.ArgumentParser(prog="library_publish.py extract-meeting|check-meeting",
                                 description="extract-meeting <proposal folder or .html> [--minutes minutes.json] [--out file] [--confirmed]: build the "
                                             "meeting JSON (default <folder>/captures/library-meeting.json). check-meeting <file>: validate only.")
    ap.add_argument("cmd", choices=["extract-meeting", "check-meeting"])
    ap.add_argument("target")
    ap.add_argument("--minutes", help="minutes.json from Minutes Studio (default: the captures/meeting-<date>/minutes.json of the folder)")
    ap.add_argument("--minutes-record", help="JSON object in the library minutes shape (date, channel, signer, language, source, confirmed, summary, "
                                             "decisions, next_steps), used instead of parsing minutes.json; validated; follow-ups still come from the HTML")
    ap.add_argument("--out")
    ap.add_argument("--confirmed", action="store_true", help="the person has read the minutes and confirms them (sets minutes.confirmed)")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "check-meeting":
            load_meeting_file(a.target)
            say("meeting file is valid")
            return 0
        data = extract_meeting(a.target, a.minutes, a.confirmed, minutes_record=a.minutes_record)
        p = pathlib.Path(a.target).resolve()
        out = pathlib.Path(a.out) if a.out else (p if p.is_dir() else p.parent) / "captures" / "library-meeting.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        say(f"wrote {out}: minutes (decisions {len(data['minutes'].get('decisions', []))}, next steps {len(data['minutes'].get('next_steps', []))}), "
            f"{len(data['followups'])} follow-up(s) with drafts")
        print(str(out))
        return 0
    except Refused as e:
        say(f"meeting data not built: {e}")
        return 2


def make_record(bl, folder, existing, a):
    src = find_proposal(folder)
    meta = bl.inspect_proposal(src)
    today = datetime.date.today().isoformat()
    if existing:
        rec = dict(existing)
        action = "updated"
    else:
        rec = bl.draft_entry(folder)
        rec["slug"] = a.slug or rec["slug"]
        action = "added"
    rec.pop("source", None)  # the card must build on any machine: the facts travel inside the record
    rec["artifact_url"] = a.artifact_url or rec.get("artifact_url")
    if not rec["artifact_url"]:
        raise Refused("no artifact address: publish the proposal as an artifact first, then pass --artifact-url")
    rec["updated"] = today
    if rec.get("created") and rec["created"] > today:
        rec["created"] = today
    if not rec.get("created"):
        rec["created"] = today
    add_meeting_fields(rec, a)
    add_meeting_data(rec, a)
    if a.status:
        rec["status"] = a.status
    if a.summary:
        rec["summary"] = a.summary
    if a.title:
        rec["title"] = a.title
    for field, value in (("industry", a.industry), ("country", a.country), ("company_url", a.company_url)):
        if value:
            rec[field] = value
    if not existing and not a.industry and ";" in str(rec.get("industry", "")):
        say("note: the industry taken from the intake looks cut off; pass --industry with a short phrase")
    name = a.by or load_config().get("name")
    if name:
        rec["last_update_by"] = name
    for k in ("sections", "palette", "c1", "c2", "sha256"):
        rec[k] = meta[k]
    rec["nav"] = meta["nav"]
    if rec.get("country") == "TO CONFIRM" or rec.get("industry") == "TO CONFIRM":
        say("note: country or industry is still 'TO CONFIRM' in the card; edit registry.json later or pass them in the intake file")
    return rec, action


NAV_ITEM = re.compile(r'\{\n\s+("id": [^\n]*),\n\s+("en": [^\n]*),\n\s+("vi": [^\n]*),\n\s+("ge": [^\n]*),\n\s+("gv": [^\n]*),\n\s+("star": (?:true|false))\n\s+\}')


def dump_registry(reg):
    """Tab-indented like the hand-edited file, with each section of a proposal's list on one line so diffs stay readable."""
    text = json.dumps(reg, indent="\t", ensure_ascii=False)
    return NAV_ITEM.sub(lambda m: "{" + ", ".join(m.groups()) + "}", text) + "\n"


def upsert(repo, bl, record):
    path = repo / "registry.json"
    original = path.read_text(encoding="utf-8")
    reg = json.loads(original)
    items = reg["proposals"]
    for i, p in enumerate(items):
        if p["slug"] == record["slug"]:
            items[i] = record
            break
    else:
        items.append(record)
    path.write_text(dump_registry(reg), encoding="utf-8")
    try:
        bl.load_registry(path)  # the library's own validation
    except bl.RegistryError as e:
        path.write_text(original, encoding="utf-8")
        raise Refused(f"the library rejected the record: {e}")


def restore(repo):
    git(repo, "checkout", "--", *GENERATED, check=False)
    git(repo, "clean", "-fdq", "--", "site", check=False)  # site/ is generated; drop files a failed build left behind


def checks(repo, bl):
    bl.build(repo / "registry.json", repo / "site", root=repo)
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=repo, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise Refused("the library's tests failed, nothing was pushed:\n" + (r.stderr or r.stdout)[-1200:])


def message(action, record, trailer):
    verb = "Add" if action == "added" else "Update"
    subject = f"{'feat' if action == 'added' else 'chore'}(library): {verb} the {record['client']} proposal"
    body = (f"Card status: {record['status']}. It opens the claude.ai artifact; no proposal HTML is published. "
            f"Updated by {record.get('last_update_by') or 'unknown'}.")
    return [subject, body] + ([trailer] if trailer else [])


# ---------------------------------------------------------------- transport 1: the library's HTTPS endpoint (no git, no GitHub account)
# The library owner makes a team key (`node tools/make_key.mjs team` in the library repo), sets its hash in Vercel and ships the key in
# library-endpoint.json next to this script: {"endpoint": "https://proposal-library-blue.vercel.app", "key": "pl_team_..."}.
# Anyone who has the skill can then add or update cards. A card made this way is marked "Needs review" until the owner approves it.
# With no key at all (library-endpoint.json holds only the address) the card goes to the library's suggestion box. The owner decides
# what that does with LIBRARY_OPEN_SUBMISSIONS in Vercel: "live" puts the card straight into the library with an Auto-added badge,
# "1" holds it in a review queue nobody sees until the owner accepts it, anything else (or unset) closes the box.
SHIPPED = pathlib.Path(__file__).resolve().parent / "library-endpoint.json"
COUNTRY_FIX = {"ph": "Philippines", "sg": "Singapore", "vn": "Vietnam", "my": "Malaysia", "id": "Indonesia", "th": "Thailand"}
NAV_ID_RE = re.compile(r"[A-Za-z0-9-]{1,60}")
NAV_RESERVED = {"settings", "sidebar", "customize", "upgrade", "downloads"}
ENDPOINT_RE = re.compile(r"^https://[A-Za-z0-9.-]+(:\d+)?$|^http://(127\.0\.0\.1|localhost)(:\d+)?$")


def usable_nav(items):
    """Keep the sections whose id can be a '#name' link into an artifact (same rule as the library's build_library.usable_nav)."""
    out, seen = [], set()
    for it in items:
        i = it["id"]
        if not NAV_ID_RE.fullmatch(i) or i.lower() in NAV_RESERVED or i.lower().startswith("comment-") or i in seen:
            continue
        seen.add(i)
        out.append(it)
    return out[:80]


class _Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections, self.title, self._in_title, self.nav = 0, "", False, []

    def handle_starttag(self, tag, attrs):
        if tag == "section":
            self.sections += 1
            a = dict(attrs)
            if a.get("id") and a.get("data-nav-en"):  # the proposal's own sidebar entries
                self.nav.append({"id": a["id"], "en": a["data-nav-en"].strip(), "vi": (a.get("data-nav-vi") or "").strip(),
                                 "ge": (a.get("data-grp-en") or "").strip(), "gv": (a.get("data-grp-vi") or "").strip(),
                                 "star": bool(a.get("data-star"))})
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def inspect_html(path):
    """What the library reads from a proposal file: section count, sidebar list, title, colours, sha256 (never sent: only these facts)."""
    raw = pathlib.Path(path).read_bytes()
    text = raw.decode("utf-8", errors="replace")
    scan = _Scan()
    scan.feed(text)
    m = re.search(r'data-palette-default="(\w+)"', text)
    palette = m.group(1) if m else "blue"
    c1 = c2 = None
    for name, body in re.findall(r'\[data-palette="(\w+)"\]\s*\{([^}]*)\}', text):
        if name == palette:
            a = re.search(r"--teal:\s*(#[0-9a-fA-F]{3,6})", body)
            b = re.search(r"--teal2:\s*(#[0-9a-fA-F]{3,6})", body)
            c1, c2 = (a.group(1) if a else None), (b.group(1) if b else None)
    return {"sections": scan.sections, "nav": usable_nav(scan.nav), "title": scan.title.strip(), "palette": palette,
            "c1": c1 or "#3167CA", "c2": c2 or "#1E4691", "sha256": hashlib.sha256(raw).hexdigest()}


def endpoint_settings(cfg):
    """(base url, key) from the environment, the settings file or the file shipped with the skill; None when there is none."""
    shipped = {}
    try:
        shipped = json.loads(SHIPPED.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    url = (os.environ.get("PROPOSAL_LIBRARY_URL") or cfg.get("endpoint") or shipped.get("endpoint") or "").rstrip("/")
    key = os.environ.get("PROPOSAL_LIBRARY_KEY") or cfg.get("key") or shipped.get("key") or ""
    if not url:
        return None
    if not ENDPOINT_RE.match(url):
        raise Refused("the library endpoint must be an https address")
    return url, key


def http(method, url, key, body=None):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json", "User-Agent": "technext-sales-proposal"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except ValueError:
        raise Refused("the library answered with something that is not JSON")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except ValueError:
            return e.code, {"ok": False, "error": "http_error"}
    except (urllib.error.URLError, TimeoutError) as e:
        raise Refused(f"cannot reach the library: {getattr(e, 'reason', e)}")


def draft_record(folder, a, meta):
    """A new card's first draft from the proposal folder: intake and identity files, the checkpoint's start date, the page title."""
    intake = next(iter(sorted(folder.glob("*-intake.json"))), None)
    ident = folder / "company-identity.json"
    data = json.loads(intake.read_text(encoding="utf-8")) if intake else {}
    ident_data = json.loads(ident.read_text(encoding="utf-8")) if ident.exists() else {}
    country = str(a.country or data.get("country") or ident_data.get("country") or "")
    country = COUNTRY_FIX.get(country.strip().lower(), country)
    parts = [x.strip() for x in meta["title"].split("·")]
    tail = " · ".join(parts[1:-1]) if len(parts) > 2 else ""
    created = None
    cp = next(iter(sorted(folder.glob("*-checkpoint.json"))), None)
    if cp:
        started = str(json.loads(cp.read_text(encoding="utf-8")).get("started_at") or "")[:10]
        created = started if re.fullmatch(r"\d{4}-\d{2}-\d{2}", started) else None
    industry = a.industry or str(data.get("industry", "TO CONFIRM")).split(";")[0].strip() or "TO CONFIRM"
    return {"client": data.get("client") or parts[0], "country": country or "TO CONFIRM", "industry": industry[:160],
            "services": ["odoo", "ai", "social"], "status": "ready", "title": a.title or tail or None, "created": created,
            "company_url": a.company_url or data.get("website") or ident_data.get("website") or None,
            "summary": "Strategic due diligence and growth blueprint across Odoo ERP, AI and social media. Bilingual (VI/EN)."}


def endpoint_publish(a, cfg, mode, folder, url, key):
    src = find_proposal(folder)
    meta = inspect_html(src)
    slug = a.slug or re.sub(r"[^a-z0-9]+", "-", folder.name.lower()).strip("-")
    base = f"{url}/api/v1/proposals"
    keyless = not key
    today = datetime.date.today().isoformat()
    last = {}
    if keyless:
        status, out = 404, {}  # a sender with no key cannot read the library, so the card is drafted from the folder
        cp0 = next(iter(sorted(folder.glob("*-checkpoint.json"))), None)
        try:
            last = (json.loads(cp0.read_text(encoding="utf-8")).get("library") or {}) if cp0 else {}
        except (OSError, ValueError):
            last = {}
    else:
        status, out = http("GET", f"{base}/{slug}", key)
    if status == 401:
        raise Refused("the library refused the key (wrong or replaced): ask the library owner for the current skill")
    if status == 200:
        rec, action = dict(out["proposal"]), "updated"
        rec.pop("pending", None)  # the server keeps the review state; a team key may not send it
    elif status == 404:
        rec, action = draft_record(folder, a, meta), "added"
        rec["slug"] = slug
    else:
        raise Refused(f"the library answered {status} ({out.get('error')}); nothing was sent")
    rec["artifact_url"] = a.artifact_url or rec.get("artifact_url")
    if not rec["artifact_url"]:
        raise Refused("no artifact address: publish the proposal as an artifact first, then pass --artifact-url")
    rec["updated"] = today
    if not rec.get("created") or rec["created"] > today:
        rec["created"] = today
    for field, value in (("status", a.status), ("summary", a.summary), ("title", a.title), ("industry", a.industry), ("country", a.country),
                         ("company_url", a.company_url)):
        if value:
            rec[field] = value
    add_meeting_fields(rec, a)
    add_meeting_data(rec, a)
    name = a.by or cfg.get("name")
    if name:
        rec["last_update_by"] = name[:60]
    for k in ("sections", "palette", "c1", "c2", "sha256"):
        rec[k] = meta[k]
    rec["nav"] = meta["nav"]
    rec.pop("source", None)
    if keyless:
        rec.pop("company_url", None)  # the website is set by the owner, never in a submission
        for field, value in (last.get("card") or {}).items():
            if field in ("status", "summary", "title", "industry", "country") and value and not getattr(a, field):
                rec[field] = value  # the same card as the last time, unless this run says otherwise
    shown = {k: v for k, v in rec.items() if k != "nav"}
    shown["nav"] = f"{len(rec['nav'])} sections"
    say(f"{action.upper()} card:\n" + json.dumps(shown, indent=2, ensure_ascii=False))
    if a.dry_run:
        say("dry run: nothing was sent")
        return 0
    if mode == "ask" and not a.yes:
        say("mode is 'ask': show this record to the person, then run again with --yes")
        return 3
    if keyless:
        status, out = http("PUT", f"{url}/api/v1/submissions/{slug}", "", rec)
    else:
        status, out = http("PUT", f"{base}/{slug}", key, rec)
    if status == 401 and keyless:
        raise Refused("the library is not taking cards without a key right now: ask the library owner to open the suggestion box "
                      "(LIBRARY_OPEN_SUBMISSIONS), or for a skill version that includes the team key")
    if status != 200:
        detail = "; ".join(f"{e['field']}: {e['message']}" for e in out.get("errors", [])) or out.get("message") or out.get("error")
        raise Refused(f"the library did not take the card ({status}): {detail}")
    if keyless:
        out["pending"] = True  # flagged: nobody has checked a card that came in with no key
        if out.get("live"):
            say("the card is in the library now, with an Auto-added badge")
        else:
            say("the card was received and waits in the owner's review queue; it is not shown in the library yet")
    cp = next(iter(sorted(folder.glob("*-checkpoint.json"))), None)
    if cp:
        try:
            data = json.loads(cp.read_text(encoding="utf-8"))
            data["library"] = {"artifact_url": rec["artifact_url"], "transport": "endpoint-submission" if keyless else "endpoint", "action": out.get("action"), "pending": out.get("pending"),
                               "version": out.get("version"), "pushed": True, "status": rec["status"], "shown": bool(out.get("live")) if keyless else True,
                               "card": {k: rec.get(k) for k in ("status", "summary", "title", "industry", "country")},
                               "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
            cp.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
        except (OSError, ValueError):
            pass
    print("LIBRARY_RESULT " + json.dumps({"slug": slug, "action": out.get("action"), "pending": out.get("pending"), "pushed": True,
                                          "artifact_url": rec["artifact_url"], "status": rec["status"]}))
    return 0


# ---------------------------------------------------------------- meeting links added in the library (GET / PUT /api/v1/meeting-links/<slug>)
LINK_KINDS = {"minutes", "quotation", "document"}
SLUG_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,79}")
LINK_ID_RE = re.compile(r"[A-Za-z0-9_.:-]{1,100}")
USED_AT_RE = re.compile(r"\d{4}-\d{2}-\d{2}(T[0-9:.]+(Z|[+-]\d{2}:\d{2})?)?")


def validate_links_response(slug, status, out):
    """The links list of a GET meeting-links answer; raises Refused with a plain reason when status or shape is not what the contract says."""
    if status == 401:
        raise Refused("the library refused the key (wrong or replaced): ask the library owner for the current skill")
    if status == 404:
        raise Refused(f"the library has no card for '{slug}' yet: run technext-sales-proposal first (nothing was created)")
    if status != 200:
        err = out.get("error") if isinstance(out, dict) else None
        raise Refused(f"the library answered {status} ({err}); no links read")
    if not isinstance(out, dict) or out.get("ok") is not True:
        raise Refused("the library answer is not in the expected shape (ok is not true)")
    links = out.get("links")
    if not isinstance(links, list):
        raise Refused("the library answer is not in the expected shape (links is not a list)")
    clean = []
    for i, l in enumerate(links, 1):
        if not isinstance(l, dict):
            raise Refused(f"link {i}: not an object")
        for k in ("id", "url", "kind"):
            if not isinstance(l.get(k), str) or not l[k].strip():
                raise Refused(f"link {i}: field '{k}' is missing or not text")
        if l["kind"] not in LINK_KINDS:
            raise Refused(f"link {i}: kind {l['kind']!r} is not one of minutes, quotation, document")
        if not l["url"].startswith("https://"):
            raise Refused(f"link {i}: url is not an https address")
        if "used_at" not in l or not (l["used_at"] is None or isinstance(l["used_at"], str)):
            raise Refused(f"link {i}: field 'used_at' is missing (it must be null or a time)")
        for k in ("label", "added_by", "added_at"):
            if k in l and l[k] is not None and not isinstance(l[k], str):
                raise Refused(f"link {i}: field '{k}' is not text")
        clean.append(l)
    return clean


def _links_setup(slug):
    if not SLUG_RE.fullmatch(slug or ""):
        raise Refused(f"{slug!r} is not a valid slug (lowercase letters, digits and hyphens)")
    settings = endpoint_settings(load_config())
    if not settings:
        raise Refused("the library is not set up on this machine: the skill folder needs library-endpoint.json from the library owner "
                      "(or set PROPOSAL_LIBRARY_URL and PROPOSAL_LIBRARY_KEY)")
    url, key = settings
    if not key:
        raise Refused("meeting links need the team key (PROPOSAL_LIBRARY_KEY, or 'key' in the settings file or library-endpoint.json); none is set")
    return f"{url}/api/v1/meeting-links/{slug}", key


def links_cli(argv):
    ap = argparse.ArgumentParser(prog="library_publish.py links|mark-link-used",
                                 description="links <slug> [--all]: list the meeting links staff added in the library (unused ones unless --all). "
                                             "mark-link-used <slug> <id> [--used-at T] [--dry-run]: mark a link as folded into the proposal.")
    ap.add_argument("cmd", choices=["links", "mark-link-used"])
    ap.add_argument("slug")
    ap.add_argument("id", nargs="?")
    ap.add_argument("--all", action="store_true", help="links: include links already marked as used")
    ap.add_argument("--used-at", help="mark-link-used: ISO time to record (default: the library sets it)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    try:
        endpoint, key = _links_setup(a.slug)
        if a.cmd == "links":
            if a.id:
                raise Refused("links takes only a slug")
            status, out = http("GET", endpoint, key)
            links = validate_links_response(a.slug, status, out)
            if not a.all:
                links = [l for l in links if l["used_at"] is None]
            print(json.dumps({"slug": a.slug, "count": len(links), "links": links}, indent=1, ensure_ascii=False))
            return 0
        if not a.id or not LINK_ID_RE.fullmatch(a.id):
            raise Refused("mark-link-used needs a link id (as printed by `links`)")
        body = {"action": "mark_used", "id": a.id}
        if a.used_at:
            if not USED_AT_RE.fullmatch(a.used_at):
                raise Refused("--used-at must be an ISO date or time, for example 2026-10-30T09:00:00Z")
            body["used_at"] = a.used_at
        if a.dry_run:
            say(f"dry run: would PUT {endpoint} {json.dumps(body)}; nothing was sent")
            return 0
        status, out = http("PUT", endpoint, key, body)
        if status == 401:
            raise Refused("the library refused the key (wrong or replaced): ask the library owner for the current skill")
        if status == 404:
            raise Refused(f"the library has no link {a.id!r} for '{a.slug}' (or no card); nothing was changed")
        if status != 200 or not isinstance(out, dict) or out.get("ok") is not True:
            err = out.get("error") if isinstance(out, dict) else None
            raise Refused(f"the library did not mark the link ({status}, {err})")
        say(f"link {a.id} marked as used")
        print("LINK_RESULT " + json.dumps({"slug": a.slug, "id": a.id, "marked": True}))
        return 0
    except Refused as e:
        say(f"meeting links: {e}")
        return 2


def main(argv=None):
    raw = sys.argv[1:] if argv is None else list(argv)
    if raw and raw[0] in ("links", "mark-link-used"):
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError):
                pass
        return links_cli(raw)
    if raw and raw[0] in ("extract-meeting", "check-meeting"):
        return meeting_cli(raw)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--artifact-url")
    ap.add_argument("--summary")
    ap.add_argument("--status", choices=["ready", "followup", "won", "lost", "archived"])
    ap.add_argument("--title")
    ap.add_argument("--by")
    ap.add_argument("--industry")
    ap.add_argument("--country")
    ap.add_argument("--company-url")
    ap.add_argument("--slug")
    ap.add_argument("--repo")
    ap.add_argument("--trailer")
    ap.add_argument("--meeting-date", type=iso_date, help="YYYY-MM-DD, goes into the card as meeting_date")
    ap.add_argument("--next-followup", type=iso_date, help="YYYY-MM-DD, goes into the card as next_followup")
    ap.add_argument("--meeting-file", help="JSON {minutes, followups} from `extract-meeting`; validated here, then sent as the card's minutes and followups")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--endpoint-only", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.meeting_file:  # an invalid file stops everything before any network or git work
        try:
            load_meeting_file(a.meeting_file)
        except Refused as e:
            say(f"library not updated: {e}")
            return 2
    cfg = load_config()
    mode = cfg.get("mode", "auto")
    if mode not in ("auto", "ask", "off"):
        mode = "auto"
    if mode == "off" and not a.dry_run:
        say("library publishing is switched off on this machine (mode: off in ~/.claude/proposal-library.json)")
        return 0
    folder = pathlib.Path(a.folder).resolve()
    try:
        explicit = a.repo or os.environ.get("PROPOSAL_LIBRARY_REPO") or cfg.get("repo")
        settings = None if (explicit and not a.endpoint_only) else endpoint_settings(cfg)
        if settings:  # no git, no GitHub account: the team key and the address are all it needs
            return endpoint_publish(a, cfg, mode, folder, *settings)
        if not explicit:
            raise Refused("the library is not set up on this machine: the skill folder needs library-endpoint.json from the library owner "
                          "(or set PROPOSAL_LIBRARY_URL and PROPOSAL_LIBRARY_KEY), or give a git clone with --repo / PROPOSAL_LIBRARY_REPO")
        repo = ensure_repo(explicit, may_clone=not pathlib.Path(explicit).expanduser().exists())
        bl = load_library(repo)
        reg0 = json.loads((repo / "registry.json").read_text(encoding="utf-8"))
        slug = a.slug or re.sub(r"[^a-z0-9]+", "-", folder.name.lower()).strip("-")
        existing = next((p for p in reg0["proposals"] if p["slug"] == slug), None)
        record, action = make_record(bl, folder, existing, a)
        shown = {k: v for k, v in record.items() if k != "nav"}
        shown["nav"] = f"{len(record['nav'])} sections"
        say(f"{action.upper()} card:\n" + json.dumps(shown, indent=2, ensure_ascii=False))
        if mode == "ask" and not a.yes and not a.dry_run:
            say("mode is 'ask': show this record to the person, then run again with --yes")
            return 3
        pushed, commit = False, None
        for attempt in (1, 2, 3):
            upsert(repo, bl, record)
            try:
                checks(repo, bl)
            except Refused:
                restore(repo)
                raise
            if a.dry_run:
                say(git(repo, "diff", "--stat").stdout)
                restore(repo)
                say("dry run: nothing committed or pushed")
                return 0
            git(repo, "add", "-A", "--", *GENERATED)
            if git(repo, "diff", "--cached", "--quiet", check=False).returncode == 0:
                say("the library already has exactly this card: nothing to do")
                return 0
            parts = message(action, record, a.trailer)
            cmd = ["commit", "-q"]
            for part in parts:
                cmd += ["-m", part]
            git(repo, *cmd)
            commit = git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
            if a.no_push:
                say(f"committed {commit} locally; not pushed (--no-push)")
                break
            r = git(repo, "push", "origin", "main", check=False)
            if r.returncode == 0:
                pushed = True
                break
            say(f"push was refused ({r.stderr.strip()[:160]}); taking the newest main and applying the card again (attempt {attempt})")
            git(repo, "fetch", "origin", "main")
            git(repo, "reset", "--hard", "origin/main")  # safe: the tree was clean and had no unpushed commits when we started
        else:
            raise Refused("could not push after 3 tries; nothing is lost, run again")
        cp = next(iter(sorted(folder.glob("*-checkpoint.json"))), None)
        if cp:
            try:
                data = json.loads(cp.read_text(encoding="utf-8"))
                data["library"] = {"artifact_url": record["artifact_url"], "commit": commit, "pushed": pushed, "action": action,
                                   "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
                cp.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
            except (OSError, ValueError):
                pass
        print("LIBRARY_RESULT " + json.dumps({"slug": record["slug"], "action": action, "commit": commit, "pushed": pushed,
                                              "artifact_url": record["artifact_url"], "status": record["status"]}))
        return 0
    except Refused as e:
        say(f"library not updated: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
