#!/usr/bin/env python3
"""
Citation bind-check - the free replacement for a paid claim-verification API.

For every inline citation in a proposal (or a Phase-1 group preview), fetch the
cited page and confirm the quote sitting in `.cite-tip-excerpt` is really taken
from that source. This is the check a paid `verify_claim` API sells, done with
free tooling instead:

    Jina Reader (free, no key)      -> fetch the source page as clean text
    trafilatura (optional)          -> pull the article body out of the HTML
    normalized substring + token coverage -> verdict: bound / partial / unbound

Why this check belongs in this pipeline: `assets/research-rules.md` already
requires every `.cite-tip-excerpt` to be "a real short quote or close paraphrase
actually taken from that source page". If that excerpt cannot be found in the
source text, then either the excerpt was invented or the source does not support
the claim - and both are exactly what the `source-auditor` gate exists to stop.

Usage:
    python bind_check.py <file.html> [<file2.html> ...]
                         [-o bind-check-report.json]
                         [--direct] [--limit N] [--sleep SECONDS]
                         [--threshold 0.85] [--quiet]

Exit codes:
    0 = every citation bound (or skipped/no citations)
    1 = at least one UNBOUND citation, OR at least one citation's source page was
        unreachable (a real fix: unreachable used to be excluded from "failures" and
        the script would print "no unbound citation" as if that were a clean pass —
        an unreachable source is unverified, not confirmed, and blocks the gate too)
    2 = usage error

Dependencies: none required (stdlib only). Optional but recommended:
    pip install beautifulsoup4 trafilatura
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import trafilatura
except ImportError:
    trafilatura = None

JINA_PREFIX = "https://r.jina.ai/"
USER_AGENT = (
    "Mozilla/5.0 (compatible; technext-proposal-bind-check/1.0; "
    "+github.com/aidev3-web/technext-sales-proposal)"
)
WORD_RE = re.compile(r"[a-z0-9]+")


def normalize_url(url):
    """Canonical form for matching a citation's URL against a manifest key —
    strips scheme, a leading www., and one trailing slash, lowercases the host.
    Without this, https://www.client-delta.example/about/ silently misses a manifest key
    of https://client-delta.example/about (a real case: 60 of 112 citations pointed at the
    same domain, differing only in www./trailing slash — that's most of the cache's
    value lost to a one-character mismatch, with no warning)."""
    parsed = urllib.parse.urlsplit(url.strip())
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = parsed.path.rstrip("/")
    return f"{host}{path}{('?' + parsed.query) if parsed.query else ''}"


def normalize(text):
    """Lowercase, collapse every non-alphanumeric run to a single space."""
    return " ".join(WORD_RE.findall((text or "").lower()))


def tokens(text):
    return WORD_RE.findall((text or "").lower())


def strip_html(raw_html):
    """Fallback main-text extraction when trafilatura is unavailable."""
    text = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw_html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    for entity, char in (("&nbsp;", " "), ("&amp;", "&"), ("&#39;", "'"),
                         ("&quot;", '"'), ("&lt;", "<"), ("&gt;", ">")):
        text = text.replace(entity, char)
    return text


def extract_claims_from_json(data, source_name):
    """Return [{file, url, excerpt}] by walking any JSON structure (dict/list at any
    depth) and collecting every dict that has both a `source_url` and an `excerpt`
    key — this is how `competitor-research-worker` (and any future facts-only
    output) structures a checkable claim, so this works generically without
    hardcoding field names like `strengths`/`weaknesses`."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            if "source_url" in node and "excerpt" in node:
                found.append({
                    "file": source_name,
                    "url": node.get("source_url"),
                    "excerpt": node.get("excerpt") or "",
                })
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return found


def extract_citations(html, source_name):
    """Return [{file, url, excerpt}] for every .cite-wrap in the document."""
    found = []
    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "html.parser")
        for wrap in soup.select("span.cite-wrap"):
            link = wrap.select_one("a.cite")
            excerpt_el = wrap.select_one(".cite-tip-excerpt")
            found.append({
                "file": source_name,
                "url": link.get("href") if link else None,
                "excerpt": excerpt_el.get_text(" ", strip=True) if excerpt_el else "",
            })
        return found

    # Regex fallback: pair each <a class="cite" href="..."> with the first
    # .cite-tip-excerpt that follows within a generous window.
    for match in re.finditer(r'<a class="cite"[^>]*href="([^"]+)"', html):
        window = html[match.end():match.end() + 2000]
        excerpt_match = re.search(
            r'class="cite-tip-excerpt"[^>]*>(.*?)</span>', window, re.S)
        excerpt = excerpt_match.group(1) if excerpt_match else ""
        found.append({
            "file": source_name,
            "url": match.group(1),
            "excerpt": re.sub(r"(?s)<[^>]+>", " ", excerpt).strip(),
        })
    return found


def fetch(url, use_jina, timeout):
    """Fetch a URL as text. Returns (text, error_string)."""
    target = url if not use_jina else JINA_PREFIX + url
    request = urllib.request.Request(target, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace"), None
    except urllib.error.HTTPError as exc:
        return None, "http_%s" % exc.code
    except urllib.error.URLError as exc:
        return None, "url_error_%s" % exc.reason
    except Exception as exc:  # timeout, decode, anything else
        return None, "error_%s" % type(exc).__name__


def main_text(raw, fetched_via_jina):
    """Best-effort main text from whatever the fetcher returned."""
    if fetched_via_jina:
        # Jina Reader already returns markdown, not HTML.
        return raw
    if trafilatura is not None:
        extracted = trafilatura.extract(raw)
        if extracted:
            return extracted
    return strip_html(raw)


MIN_EXCERPT_CHARS = 10


def verdict_for(excerpt, source_text, threshold):
    """bound / partial / unbound, plus the token-coverage score."""
    normalized_excerpt = normalize(excerpt)
    normalized_source = normalize(source_text)
    if not normalized_excerpt:
        return "skipped", 1.0
    if len(normalized_excerpt) < MIN_EXCERPT_CHARS:
        # same floor as validate-proposal.py check 10: "22 videos" is not evidence
        return "unbound", 0.0
    if normalized_excerpt in normalized_source:
        return "bound", 1.0
    excerpt_tokens = set(tokens(excerpt))
    if not excerpt_tokens:
        return "skipped", 1.0
    source_tokens = set(tokens(source_text))
    coverage = len(excerpt_tokens & source_tokens) / float(len(excerpt_tokens))
    if coverage >= threshold:
        return "partial", round(coverage, 3)
    return "unbound", round(coverage, 3)


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Check that every citation excerpt is really on its source page.")
    parser.add_argument("files", nargs="+",
                        help="proposal/group-preview HTML file(s), or (with --facts) "
                             "facts-only JSON file(s) such as competitor-research/*.json")
    parser.add_argument("--facts", action="store_true",
                        help="input files are JSON (e.g. competitor-research/*.json), "
                             "not HTML — verify every {source_url, excerpt} object "
                             "found anywhere in the JSON, before this data is ever "
                             "read by Phase 1. This is the 'verify before you write, "
                             "not after' gate: bind-checking p1-group*.html happens "
                             "after the content is already written; --facts catches a "
                             "bad excerpt in the research input before that.")
    parser.add_argument("-o", "--out", default="bind-check-report.json",
                        help="report path (default: bind-check-report.json)")
    parser.add_argument("--direct", action="store_true",
                        help="fetch the source URL directly instead of through Jina Reader")
    parser.add_argument("--from-cache", metavar="MANIFEST_JSON", default=None,
                        help="read from web-osint-scanner's captures/manifest.json + "
                             "captures/*.md instead of fetching over the network — "
                             "turns a ~15-20 min network-bound bind-check into a few "
                             "seconds when the cited URLs were already pre-fetched in "
                             "Phase 0.8. Falls back to a live fetch (Jina/direct per "
                             "--direct) for any cited URL not found in the manifest.")
    parser.add_argument("--limit", type=int, default=0,
                        help="check at most N distinct URLs (useful for a cheap sample run)")
    parser.add_argument("--sleep", type=float, default=1.5,
                        help="seconds to wait between distinct-URL fetches (default: 1.5)")
    parser.add_argument("--threshold", type=float, default=0.85,
                        help="token-coverage ratio at or above which an excerpt counts "
                             "as partial rather than unbound (default: 0.85)")
    parser.add_argument("--quiet", action="store_true", help="only print the summary")
    return parser.parse_args(argv)


def load_capture_manifest(manifest_path):
    """Load web-osint-scanner's captures/manifest.json — {url: {file, fetched_at}} —
    and return {normalize_url(url): absolute_file_path}. Returns {} if the file
    doesn't exist/isn't valid JSON, so --from-cache degrades to a normal live fetch
    for every URL rather than crashing.

    Two real bugs fixed here: (1) `file` paths in the manifest are relative to the
    manifest's OWN directory, not whatever directory this script happens to be run
    from — resolved against manifest_path's parent, not left as a bare relative path
    that silently misses when run from elsewhere. (2) keys are matched via
    normalize_url() so a scheme/www./trailing-slash difference between a citation's
    href and the manifest's key doesn't silently miss."""
    try:
        with open(manifest_path, encoding="utf-8-sig") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    base_dir = os.path.dirname(os.path.abspath(manifest_path))
    resolved = {}
    for url, entry in raw.items():
        file_path = entry.get("file") if isinstance(entry, dict) else None
        if not file_path:
            continue
        if not os.path.isabs(file_path):
            # web-osint-scanner / social-browser-scan write paths relative to the RUN
            # dir ("captures/x.md"), older manifests relative to the manifest's own dir
            # ("x.md") — try both, then the current dir, and keep the first that exists.
            candidates = [os.path.join(base_dir, file_path),
                          os.path.join(os.path.dirname(base_dir), file_path),
                          os.path.abspath(file_path)]
            file_path = next((c for c in candidates if os.path.isfile(c)), candidates[0])
        resolved[normalize_url(url)] = file_path
    return resolved


def main(argv):
    args = parse_args(argv)
    use_jina = not args.direct
    manifest = load_capture_manifest(args.from_cache) if args.from_cache else {}

    citations = []
    for path in args.files:
        try:
            if args.facts:
                with open(path, encoding="utf-8-sig") as handle:
                    data = json.load(handle)
                citations.extend(extract_claims_from_json(data, path))
            else:
                with open(path, encoding="utf-8") as handle:
                    html = handle.read()
                citations.extend(extract_citations(html, path))
        except OSError as exc:
            print("cannot read %s: %s" % (path, exc), file=sys.stderr)
            return 2
        except json.JSONDecodeError as exc:
            print("cannot parse %s as JSON: %s" % (path, exc), file=sys.stderr)
            return 2

    if not citations:
        what = "{source_url, excerpt} claim(s)" if args.facts else ".cite-wrap citations"
        print("No %s found in %s" % (what, ", ".join(args.files)))
        return 0

    # Fetch each distinct URL once, keep an insertion-ordered cache.
    unique_urls = []
    for citation in citations:
        url = citation["url"]
        if not url or url.startswith("#"):
            continue
        if url not in unique_urls:
            unique_urls.append(url)
    if args.limit:
        unique_urls = unique_urls[:args.limit]

    cache = {}
    live_fetch_count = 0
    cache_misses = []  # URLs --from-cache was given for, but weren't found in the manifest
    for url in unique_urls:
        file_path = manifest.get(normalize_url(url)) if manifest else None
        if file_path:
            try:
                with open(file_path, encoding="utf-8") as f:
                    cache[url] = {"ok": True, "text": f.read()}
                if not args.quiet:
                    print("  cached  %-70s %d chars" % (url[:70], len(cache[url]["text"])))
                continue
            except OSError:
                pass  # manifest points at a missing file — fall through to live fetch
        if manifest:
            cache_misses.append(url)
        if live_fetch_count:
            time.sleep(args.sleep)
        live_fetch_count += 1
        raw, error = fetch(url, use_jina, timeout=45)
        if error:
            cache[url] = {"ok": False, "error": error}
        else:
            cache[url] = {"ok": True, "text": main_text(raw, use_jina)}
        if not args.quiet:
            status = "unreachable (%s)" % cache[url]["error"] if not cache[url]["ok"] \
                else "%d chars" % len(cache[url]["text"])
            print("  fetched %-70s %s" % (url[:70], status))
    if manifest:
        print("  %d/%d URL(s) served from cache, %d fetched live" %
              (len(unique_urls) - live_fetch_count, len(unique_urls), live_fetch_count))
        if cache_misses:
            print("  ⚠ %d URL(s) were NOT in the cache manifest and had to be fetched "
                  "live (--from-cache is losing most of its benefit if this list is "
                  "long — check for a URL-normalization or relative-path mismatch "
                  "between the manifest and these citations): %s" %
                  (len(cache_misses), cache_misses[:10]), file=sys.stderr)

    results = []
    counts = {"bound": 0, "partial": 0, "unbound": 0, "unreachable": 0, "skipped": 0}
    for citation in citations:
        url = citation["url"] or ""
        excerpt = citation["excerpt"] or ""
        if not url or url.startswith("#"):
            state, score = "skipped", None
        elif not excerpt.strip():
            state, score = "skipped", None
        elif url not in cache:
            state, score = "skipped", None  # trimmed by --limit
        elif not cache[url]["ok"]:
            state, score = "unreachable", None
        else:
            state, score = verdict_for(excerpt, cache[url]["text"], args.threshold)
        counts[state] = counts.get(state, 0) + 1
        results.append({
            "file": citation["file"],
            "url": url,
            "excerpt": excerpt[:280],
            "verdict": state,
            "coverage": score,
        })

    report = {
        "files": args.files,
        "fetcher": "direct" if args.direct else "jina-reader",
        "threshold": args.threshold,
        "counts": counts,
        "results": results,
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("\n=== citation bind-check ===")
    print("  bound       %d" % counts.get("bound", 0))
    print("  partial     %d" % counts.get("partial", 0))
    print("  UNBOUND     %d" % counts.get("unbound", 0))
    print("  unreachable %d" % counts.get("unreachable", 0))
    print("  skipped     %d" % counts.get("skipped", 0))

    failures = [r for r in results if r["verdict"] == "unbound"]
    unreachable = [r for r in results if r["verdict"] == "unreachable"]
    if failures:
        print("\nBlocking: %d citation(s) whose excerpt is NOT in the source page."
              % len(failures))
        for failure in failures[:20]:
            print("  - %s" % failure["url"])
            print("    excerpt: %s" % failure["excerpt"][:120])
            print("    coverage: %s" % failure["coverage"])
        print("\nRoute each back to the owning subagent: either fix the quote, or "
              "re-tag the claim .assess if no source actually supports it.")
    elif unreachable:
        # Fixed a real false-PASS bug: this used to print "no unbound citation" here
        # even when several citations were never actually checked because their
        # source page couldn't be fetched — that's not a pass, it's an unverified
        # claim, and reporting it as clean was actively misleading.
        print("\nNo UNBOUND citation, but %d citation(s) could not be checked at all "
              "(source page unreachable) — these are unverified, not confirmed. "
              "Do not report this as a clean pass." % len(unreachable))
        for r in unreachable[:20]:
            print("  - %s" % r["url"])
    else:
        print("\nNo unbound citation. Every excerpt evaluated was found in its source.")

    print("Report written to %s" % args.out)
    return 1 if (failures or unreachable) else 0  # unverified citations block the gate too


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))