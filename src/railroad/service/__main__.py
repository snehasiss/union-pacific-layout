"""Run the railroad Flask development server."""

from __future__ import annotations

import argparse

from railroad.service import create_app


def main() -> None:
    parser = argparse.ArgumentParser(prog="railroad.service")
    parser.add_argument("--config", default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    create_app(args.config).run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
