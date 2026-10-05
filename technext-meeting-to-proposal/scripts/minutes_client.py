#!/usr/bin/env python3
"""Command-line client for the Minutes Studio API (standard library only, so it runs on any machine with Python 3.8+).

    minutes_client.py send  FILE   --owner EMAIL [--client X] [--meeting-type Y] [--subject Z] [--date YYYY-MM-DD] [--terms a,b]
    minutes_client.py wait  RUN_ID --owner EMAIL [--timeout 5400] [--every 10]
    minutes_client.py fetch RUN_ID --owner EMAIL --out DIR [--pdf]

The server address comes from, in this order: the environment variable MINUTES_API_URL, a .minutes-api file in the project folder (or above),
then DEFAULT_API_URL at the top of this file, for example http://192.168.10.157:8502.
Progress goes to stderr; the result is one JSON object on stdout. Exit codes:
    0 done   1 call failed   2 a person must open the link (unknown voice)   3 the run failed   4 timed out
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

EXIT_OK, EXIT_FAILED, EXIT_NEEDS_PERSON, EXIT_RUN_ERROR, EXIT_TIMEOUT = 0, 1, 2, 3, 4

# ---- Default settings. Edit them here to change the defaults for everyone who uses this copy of the script. ----
# The server address used when neither MINUTES_API_URL nor a .minutes-api file gives one. For a team, put the LAN address of the
# machine that runs the Minutes Studio, for example "http://192.168.10.157:8502". "" means: no default, ask for one.
DEFAULT_API_URL = "http://localhost:8502"
DEFAULT_WAIT_TIMEOUT = 5400      # seconds `wait` keeps checking before it gives up (90 minutes)
DEFAULT_WAIT_EVERY = 10.0        # seconds between two checks


def _address_from_project_file():
    """The first non-comment line of a file named .minutes-api in the current folder or any folder above it."""
    for folder in [Path.cwd()] + list(Path.cwd().parents):
        candidate = folder / ".minutes-api"
        if candidate.is_file():
            for line in candidate.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
    return ""


def base_url():
    """The server address: MINUTES_API_URL, else a .minutes-api file in the project (any agent), else DEFAULT_API_URL at the top of this file."""
    url = (os.environ.get("MINUTES_API_URL") or _address_from_project_file() or DEFAULT_API_URL).strip().rstrip("/")
    if not url:
        raise SystemExit("The server address is not set. Set MINUTES_API_URL, put it in a .minutes-api file in the project, or set "
                         "DEFAULT_API_URL at the top of minutes_client.py, for example http://192.168.10.157:8502 (ask the administrator).")
    return url


def call(method, path, owner, params=None, body=None, length=None, timeout=60):
    query = urllib.parse.urlencode(dict({"owner": owner}, **(params or {})))
    headers = {}
    if body is not None:
        headers["Content-Length"] = str(length)
        headers["Content-Type"] = "application/octet-stream"
    request = urllib.request.Request("%s%s?%s" % (base_url(), path, query), data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            kind = response.headers.get("Content-Type", "")
            return response.status, (json.loads(raw.decode("utf-8")) if kind.startswith("application/json") else raw)
    except urllib.error.HTTPError as err:
        try:
            detail = json.loads(err.read().decode("utf-8")).get("error", "")
        except ValueError:
            detail = ""
        raise ApiProblem(err.code, detail or err.reason)
    except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
        raise ApiProblem(0, "The server closed the connection during the upload. Check that the email address is valid for this server "
                            "and that the file is not too large, then try again.")
    except urllib.error.URLError as err:
        if isinstance(err.reason, (ConnectionAbortedError, ConnectionResetError, BrokenPipeError)):
            raise ApiProblem(0, "The server closed the connection during the upload. Check that the email address is valid for this server "
                                "and that the file is not too large, then try again.")
        raise ApiProblem(0, "Cannot reach the Minutes Studio at %s (%s). Is the server running and the port open?" % (base_url(), err.reason))


class ApiProblem(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status, self.message = status, message


def cmd_send(args):
    path = Path(args.file)
    if not path.is_file():
        raise ApiProblem(0, "File not found: %s" % path)
    params = {"name": path.name, "client": args.client, "meeting_type": args.meeting_type, "subject": args.subject,
              "date": args.date, "terms": args.terms}
    params = {k: v for k, v in params.items() if v}
    size = path.stat().st_size
    print("Uploading %s (%.1f MB) ..." % (path.name, size / 1e6), file=sys.stderr)
    with path.open("rb") as handle:
        _, result = call("PUT", "/api/runs", args.owner, params, body=handle, length=size, timeout=3600)
    print(json.dumps(result, ensure_ascii=False))
    return EXIT_OK


def cmd_wait(args):
    deadline = time.time() + args.timeout
    last = None
    while True:
        _, status = call("GET", "/api/runs/" + args.run_id, args.owner)
        line = "%5.1f%%  %s" % (status["percent"], status.get("message") or status.get("state"))
        if line != last:
            print(line, file=sys.stderr)
            last = line
        if status["state"] == "done":
            print(json.dumps(status, ensure_ascii=False))
            return EXIT_OK
        if status["state"] == "error":
            print(json.dumps(status, ensure_ascii=False))
            return EXIT_RUN_ERROR
        if status.get("needs_person"):
            print(json.dumps(status, ensure_ascii=False))
            return EXIT_NEEDS_PERSON
        if not status.get("working") and status["state"] not in ("created", "prepared", "confirmed", "ready"):
            print("The run stopped without finishing; open %s and press Resume." % status["web_url"], file=sys.stderr)
            print(json.dumps(status, ensure_ascii=False))
            return EXIT_RUN_ERROR
        if time.time() > deadline:
            print(json.dumps(status, ensure_ascii=False))
            return EXIT_TIMEOUT
        time.sleep(args.every)


def cmd_fetch(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    written = {}
    _, status = call("GET", "/api/runs/" + args.run_id, args.owner)
    _, minutes = call("GET", "/api/runs/%s/minutes" % args.run_id, args.owner)
    _, transcript = call("GET", "/api/runs/%s/transcript" % args.run_id, args.owner)
    for name, data in (("minutes.json", minutes), ("transcript.json", transcript), ("status.json", status)):
        (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        written[name] = str(out / name)
    if args.pdf:
        for filename in status.get("outputs", {}).values():
            _, pdf = call("GET", "/api/runs/%s/files/%s" % (args.run_id, urllib.parse.quote(filename)), args.owner, timeout=300)
            (out / filename).write_bytes(pdf)
            written[filename] = str(out / filename)
    print(json.dumps({"run_id": args.run_id, "web_url": status["web_url"], "files": written}, ensure_ascii=False))
    return EXIT_OK


def main(argv=None):
    parser = argparse.ArgumentParser(prog="minutes_client")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("send", help="upload a recording and start a run")
    p.add_argument("file")
    p.add_argument("--owner", required=True, help="your Claude account email")
    p.add_argument("--client", default="")
    p.add_argument("--meeting-type", default="")
    p.add_argument("--subject", default="")
    p.add_argument("--date", default="")
    p.add_argument("--terms", default="", help="comma-separated names and terms to watch for")
    p.set_defaults(func=cmd_send)
    p = sub.add_parser("wait", help="wait until the run is done, needs a person, or fails")
    p.add_argument("run_id")
    p.add_argument("--owner", required=True)
    p.add_argument("--timeout", type=int, default=DEFAULT_WAIT_TIMEOUT, help="seconds before giving up (default set at the top of this file)")
    p.add_argument("--every", type=float, default=DEFAULT_WAIT_EVERY, help="seconds between checks")
    p.set_defaults(func=cmd_wait)
    p = sub.add_parser("fetch", help="download the minutes, the transcript and optionally the PDFs")
    p.add_argument("run_id")
    p.add_argument("--owner", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--pdf", action="store_true")
    p.set_defaults(func=cmd_fetch)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ApiProblem as err:
        print("ERROR: %s" % err.message, file=sys.stderr)
        return EXIT_FAILED


if __name__ == "__main__":
    sys.exit(main())
