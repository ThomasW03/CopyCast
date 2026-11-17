"""Helpers shared by the tests: a local web server and ready-made manifest entries."""

import threading
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from demo_library.manifest import MediaEntry


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._respond(send_body=True)

    def do_HEAD(self):
        self._respond(send_body=False)

    def _respond(self, send_body: bool) -> None:
        body = self.server.routes.get(self.path)
        if body is None:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def log_message(self, *args):
        """Keeps the test output quiet."""


class LocalServer:
    """Serves fixed bytes on 127.0.0.1. Use it as a context manager."""

    def __init__(self, routes: dict):
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self._server.routes = routes
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self._server.server_port}{path}"

    def __enter__(self) -> "LocalServer":
        self._thread.start()
        return self

    def __exit__(self, *exc_info) -> None:
        self._server.shutdown()
        self._server.server_close()


def make_entry(**overrides) -> MediaEntry:
    """A valid manifest entry. Pass keyword arguments to change fields."""
    fields = dict(
        id="sample",
        kind="movie",
        title="Sample",
        year=2020,
        filename="sample.2020.mkv",
        difficulty="none",
        url="https://example.org/sample.mkv",
        size=10,
        license="CC BY 3.0",
        license_url="https://creativecommons.org/licenses/by/3.0/",
        attribution="Someone",
        source_page="https://example.org/sample",
    )
    fields.update(overrides)
    return MediaEntry(**fields)


def make_zip(path: Path, members: dict) -> bytes:
    """Writes a zip file holding `members` (name to bytes) and returns its content."""
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in members.items():
            archive.writestr(name, content)
    return path.read_bytes()
