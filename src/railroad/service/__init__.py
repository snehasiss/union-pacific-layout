"""Flask application factory for the railroad web interface."""

from __future__ import annotations

from pathlib import Path

from flask import Flask


def create_app(config_path: str | Path | None = None) -> Flask:
    """Create the web application without starting a development server."""
    default_config = Path(__file__).resolve().parents[3] / "config" / "railroad-conf.json"
    app = Flask(__name__)
    app.config["RAILROAD_CONFIG"] = str(config_path or default_config)

    from railroad.service.routes import web

    app.register_blueprint(web)
    return app
