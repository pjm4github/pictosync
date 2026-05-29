"""
mermaid/browser_renderer.py

Render a Mermaid source file to SVG using the user's regular browser instead
of a headless one (mmdc/Puppeteer).

A tiny ``localhost`` HTTP server serves an HTML page that loads the *bundled*
``mermaid.min.js`` and renders the diagram client-side, then auto-POSTs the
resulting SVG back to the server.  The caller blocks until the SVG arrives
(or a timeout), so the import flow stays the same as the mmdc path — only the
geometry source changes.

This needs no Node, no mmdc, and no network (mermaid.js is bundled).  It does
require a default web browser and momentarily opens a tab.
"""

from __future__ import annotations

import http.server
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

_ASSETS_DIR = Path(__file__).resolve().parent / "assets"
_MERMAID_JS = _ASSETS_DIR / "mermaid.min.js"

_PAGE_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>PictoSync — Mermaid render</title>
<style>
  body { font-family: "Segoe UI", system-ui, sans-serif; margin: 1rem; }
  #status { padding: .6rem .8rem; border-radius: 6px; font-weight: 600;
            background: #eef; color: #224; display: inline-block; }
  #status.ok  { background: #e6f7e6; color: #163; }
  #status.err { background: #fdecec; color: #922; white-space: pre-wrap; }
  #out { margin-top: 1rem; }
</style>
<script src="mermaid.min.js"></script>
</head>
<body>
<div id="status">Rendering diagram…</div>
<div id="out"></div>
<script>
(async () => {
  const status = document.getElementById('status');
  try {
    const src = await (await fetch('source')).text();
    mermaid.initialize({ startOnLoad: false });
    const { svg } = await mermaid.render('pictosyncGraph', src);
    const out = document.getElementById('out');
    out.innerHTML = svg;
    // mermaid serialises foreignObject content as HTML (e.g. <br>), which is
    // not well-formed XML.  Re-serialise the rendered SVG node via
    // XMLSerializer so void elements self-close (<br/>) and entities are
    // escaped — the downstream strict XML parser then accepts it.
    const svgEl = out.querySelector('svg');
    const xml = svgEl ? new XMLSerializer().serializeToString(svgEl) : svg;
    const r = await fetch('result', {
      method: 'POST',
      headers: { 'Content-Type': 'image/svg+xml' },
      body: xml,
    });
    status.className = 'ok';
    status.textContent = r.ok
      ? 'Diagram sent to PictoSync — you can close this tab.'
      : 'Sent, but the server returned status ' + r.status + '.';
  } catch (e) {
    status.className = 'err';
    const msg = (e && e.message) ? e.message : String(e);
    status.textContent = 'Render error:\\n' + msg;
    try {
      await fetch('error', { method: 'POST', body: String((e && e.stack) || e) });
    } catch (_) { /* ignore */ }
  }
})();
</script>
</body>
</html>
"""


class _RenderServer(http.server.ThreadingHTTPServer):
    """Localhost server holding the render job state."""

    daemon_threads = True

    def __init__(self, source: str, mermaid_js: bytes) -> None:
        super().__init__(("127.0.0.1", 0), _RenderHandler)
        self.source_bytes = source.encode("utf-8")
        self.mermaid_js = mermaid_js
        self.done = threading.Event()
        self.svg: Optional[str] = None
        self.error: Optional[str] = None


class _RenderHandler(http.server.BaseHTTPRequestHandler):
    """Serves the render page/assets and receives the rendered SVG."""

    def log_message(self, *args, **kwargs) -> None:  # noqa: D401 - silence access log
        pass

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        srv: _RenderServer = self.server  # type: ignore[assignment]
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self._send(200, _PAGE_HTML.encode("utf-8"), "text/html; charset=utf-8")
        elif path == "/mermaid.min.js":
            self._send(200, srv.mermaid_js, "application/javascript; charset=utf-8")
        elif path == "/source":
            self._send(200, srv.source_bytes, "text/plain; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:
        srv: _RenderServer = self.server  # type: ignore[assignment]
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else b""
        path = self.path.split("?", 1)[0]
        if path == "/result":
            srv.svg = body.decode("utf-8", errors="replace")
        elif path == "/error":
            srv.error = body.decode("utf-8", errors="replace")
        else:
            self._send(404, b"not found", "text/plain")
            return
        self._send(200, b"ok", "text/plain")
        srv.done.set()


def render_mmd_to_svg(
    mmd_path: str,
    output_svg: str | None = None,
    timeout: float = 120.0,
) -> str:
    """Render a ``.mmd``/``.mermaid`` file to SVG via the default browser.

    Args:
        mmd_path: Path to the Mermaid source file.
        output_svg: Optional explicit output path.  Defaults to the source
            path with a ``.svg`` suffix.
        timeout: Seconds to wait for the browser to return the rendered SVG.

    Returns:
        Path to the written SVG file.

    Raises:
        RuntimeError: If mermaid.js is missing, the browser cannot be opened,
            rendering fails, or the result does not arrive before *timeout*.
    """
    if not _MERMAID_JS.is_file():
        raise RuntimeError(
            f"Bundled mermaid.js not found at {_MERMAID_JS}.\n"
            "The browser render backend requires mermaid/assets/mermaid.min.js."
        )

    mmd = Path(mmd_path).resolve()
    if not mmd.is_file():
        raise RuntimeError(f"Mermaid file not found: {mmd}")

    source = mmd.read_text(encoding="utf-8")
    mermaid_js = _MERMAID_JS.read_bytes()

    server = _RenderServer(source, mermaid_js)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}/"

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        if not webbrowser.open(url):
            raise RuntimeError(
                "Could not open a web browser for Mermaid rendering.\n"
                f"Open this URL manually to render: {url}"
            )

        if not server.done.wait(timeout):
            raise RuntimeError(
                f"Timed out after {timeout:.0f}s waiting for the browser to "
                f"render the diagram.\nThe render page was at {url}"
            )

        if server.error is not None:
            raise RuntimeError(f"Mermaid render failed in the browser:\n{server.error}")
        if not server.svg:
            raise RuntimeError("Browser returned an empty SVG.")
        # Guard: the returned SVG must be well-formed XML for the strict
        # downstream parser.  Surface a clean error rather than crashing later.
        import xml.etree.ElementTree as _ET
        try:
            _ET.fromstring(server.svg)
        except _ET.ParseError as pe:
            raise RuntimeError(
                f"Browser returned malformed SVG (not well-formed XML): {pe}"
            )
    finally:
        server.shutdown()
        server.server_close()

    final = Path(output_svg).resolve() if output_svg else mmd.with_suffix(".svg")
    final.write_text(server.svg, encoding="utf-8")
    return str(final)
