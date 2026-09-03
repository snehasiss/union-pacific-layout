"""Flask application factory for the asset-management chat service."""

from __future__ import annotations

from pathlib import Path

from flask import Flask


def create_app(config_path: str | Path | None = None) -> Flask:
    """Create chat_service without starting its development server."""
    project_root = Path(__file__).resolve().parents[2]
    app = Flask(__name__)
    app.config["RAILROAD_CONFIG"] = str(
        config_path or project_root / "config" / "railroad-conf.json"
    )
    app.config.setdefault("CHAT_SLM_URL", None)
    app.config.setdefault("CHAT_SLM_MODEL", "local-model")

    from chat.routes import web

    app.register_blueprint(web)
    return app


__all__ = ["create_app"]

