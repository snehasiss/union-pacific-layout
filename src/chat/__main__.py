"""Run chat_service as a separate Flask development service."""

from __future__ import annotations

import argparse
import os

from chat import create_app


def main() -> None:
    parser = argparse.ArgumentParser(prog="chat")
    parser.add_argument("--config", default=None)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5203)
    parser.add_argument("--slm-url", default=os.getenv("CHAT_SLM_URL"))
    parser.add_argument("--slm-model", default=os.getenv("CHAT_SLM_MODEL", "local-model"))
    parser.add_argument(
        "--slm-debug",
        action="store_true",
        default=os.getenv("CHAT_SLM_DEBUG", "").casefold() in {"1", "true", "yes", "on"},
    )
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    app = create_app(args.config)
    app.config["CHAT_SLM_URL"] = args.slm_url
    app.config["CHAT_SLM_MODEL"] = args.slm_model
    app.config["CHAT_SLM_DEBUG"] = args.slm_debug
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
