"""Command-line entry point for the local workbench."""

from __future__ import annotations

import argparse

from .server import create_server


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the private AskJamie Found-Ry workbench.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--data-dir", default=".foundry-data")
    args = parser.parse_args()
    server = create_server(args.port, args.data_dir)
    print(f"AskJamie Found-Ry listening on http://127.0.0.1:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
