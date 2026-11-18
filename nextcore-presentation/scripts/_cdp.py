# -*- coding: utf-8 -*-
"""Shared helpers for the technext-presentations scripts: a local static server for the repo and a real-time
headless Chrome driven over the DevTools protocol (frames run in real time, so slide animations finish).

    from _cdp import REPO, serve, Chrome
    with serve() as base, Chrome(1600, 900) as c:
        c.open(base + "company-profile.html")
        c.ev("Deck.go(2, -1)"); c.sleep(3); c.shot("out.png")
"""
import base64, contextlib, functools, http.server, json, os, pathlib, shutil, socket, subprocess, tempfile, threading, time, urllib.request

import websocket  # pip install websocket-client

import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # slide titles carry · and – on a cp1252 console

REPO = pathlib.Path(os.environ.get("TN_DECKS", pathlib.Path.home() / "ClaudeWork/technext-presentations"))
CHROME = os.environ.get("CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


@contextlib.contextmanager
def serve(root=REPO, base=None):
    """Serve the repo on a free port (or use an already running server when base is given). Yields the base URL."""
    if base:
        yield base.rstrip("/") + "/"
        return
    port = free_port()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(_Quiet, directory=str(root)))
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{port}/"
    finally:
        srv.shutdown()


class Chrome:
    """Headless Chrome with one page. Collects console errors and uncaught exceptions in self.errors."""

    def __init__(self, w=1600, h=900, mobile=False, touch=False):
        self.w, self.h, self.mobile, self.touch = w, h, mobile, touch
        self.errors, self._events, self.i = [], [], 0

    def __enter__(self):
        self.port = free_port()
        self.prof = tempfile.mkdtemp(prefix="tn-decks-")
        self.proc = subprocess.Popen([CHROME, "--headless=new", "--no-sandbox", "--hide-scrollbars", "--no-first-run", "--disable-extensions",
                                      "--remote-allow-origins=*", f"--remote-debugging-port={self.port}", f"--user-data-dir={self.prof}",
                                      f"--window-size={self.w},{self.h}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        url = None
        for _ in range(120):
            try:
                pages = [t for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json")) if t.get("type") == "page"]
                if pages:
                    url = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            time.sleep(.2)
        if not url:
            raise RuntimeError("headless Chrome did not start")
        self.ws = websocket.create_connection(url, max_size=None, timeout=180, suppress_origin=True)
        for m in ("Page.enable", "Runtime.enable", "Log.enable"):
            self.call(m)
        self.call("Emulation.setDeviceMetricsOverride", width=self.w, height=self.h, deviceScaleFactor=1, mobile=self.mobile)
        if self.touch:
            self.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
            self.call("Emulation.setEmitTouchEventsForMouse", enabled=True)
        return self

    def __exit__(self, *a):
        try:
            self.ws.close()
        except Exception:
            pass
        self.proc.kill()
        shutil.rmtree(self.prof, ignore_errors=True)

    def _event(self, m):
        meth, p = m.get("method"), m.get("params", {})
        if meth == "Runtime.exceptionThrown":
            d = p.get("exceptionDetails", {})
            self.errors.append("exception: " + (d.get("exception", {}).get("description") or d.get("text", "")).split("\n")[0])
        elif meth == "Runtime.consoleAPICalled" and p.get("type") == "error":
            self.errors.append("console.error: " + " ".join(str(a.get("value", a.get("description", ""))) for a in p.get("args", []))[:300])
        elif meth == "Log.entryAdded" and p.get("entry", {}).get("level") == "error":
            e = p["entry"]
            self.errors.append(f"{e.get('source')}: {e.get('text', '')[:200]} {e.get('url', '')}".strip())

    def call(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.i:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})
            self._event(m)

    def ev(self, js):
        r = self.call("Runtime.evaluate", expression=js, returnByValue=True, awaitPromise=True)
        if r.get("exceptionDetails"):
            raise RuntimeError("eval failed: " + r["exceptionDetails"].get("exception", {}).get("description", str(r["exceptionDetails"]))[:400])
        return r.get("result", {}).get("value")

    def sleep(self, s):
        """Wait in real time while still draining events (console errors arrive while slides play)."""
        end = time.time() + s
        while time.time() < end:
            self.ev("0")
            time.sleep(min(.25, max(0, end - time.time())))

    def open(self, url, settle=1.2):
        self.call("Page.navigate", url=url)
        for _ in range(240):
            time.sleep(.25)
            try:
                if self.ev("document.readyState") == "complete":
                    break
            except Exception:
                pass
        self.ev("document.fonts.ready.then(()=>1)")
        self.sleep(settle)

    def images_loaded(self, scope="document"):
        return self.ev("Promise.all([...%s.querySelectorAll('img')].filter(i=>i.getAttribute('src')).map(i=>i.complete?1:new Promise(r=>{i.onload=i.onerror=r;setTimeout(r,8000)}))).then(()=>1)" % scope)

    def shot(self, path, clip=None):
        p = {"format": "png"}
        if clip:
            p["clip"] = dict(x=clip[0], y=clip[1], width=clip[2], height=clip[3], scale=1)
        data = self.call("Page.captureScreenshot", **p)["data"]
        pathlib.Path(path).write_bytes(base64.b64decode(data))
        return path

    def pdf(self, path):
        data = self.call("Page.printToPDF", printBackground=True, preferCSSPageSize=True)["data"]
        pathlib.Path(path).write_bytes(base64.b64decode(data))
        return path


def decks():
    """The launcher's deck list from _src/build.py: [(group, dict(slug, title, pdf, ...))]."""
    import sys
    sys.path.insert(0, str(REPO / "_src"))
    import build  # noqa: E402  (module level only reads json and defines functions)
    return [(g, d) for g, ds in build.DECKS for d in ds]
