from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
import tempfile
import webbrowser
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class QuietRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


def _extract_export(zip_path: Path) -> tempfile.TemporaryDirectory:
    temp = tempfile.TemporaryDirectory()
    try:
        with zipfile.ZipFile(zip_path) as archive:
            for name in archive.namelist():
                path = PurePosixPath(name)
                if path.is_absolute() or PureWindowsPath(name).drive or ".." in path.parts or "\\" in name:
                    raise SystemExit(f"unsafe archive path: {name}")
            for entry in archive.infolist():
                destination = Path(temp.name).joinpath(*PurePosixPath(entry.filename).parts)
                if entry.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(archive.read(entry))
        if not (Path(temp.name) / "index.html").exists():
            raise SystemExit("decision export is missing index.html")
    except BaseException:
        temp.cleanup()
        raise
    return temp


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve an exported decision package locally.")
    parser.add_argument("zip_path", type=Path, help="Path to a generated export ZIP")
    parser.add_argument("--port", type=int, default=8767, help="Local port to serve on")
    parser.add_argument("--open", action="store_true", help="Open the local browser automatically")
    args = parser.parse_args()

    temp = _extract_export(args.zip_path)
    handler = functools.partial(QuietRequestHandler, directory=temp.name)
    with temp, ReusableTCPServer(("127.0.0.1", args.port), handler) as server:
        url = f"http://127.0.0.1:{args.port}/index.html"
        print(url, flush=True)
        if args.open:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            return 0
        finally:
            temp.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
