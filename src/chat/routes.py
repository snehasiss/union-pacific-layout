"""HTTP and HTML routes for chat_service."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, current_app, jsonify, render_template, request, send_from_directory

from chat.assets import create_asset, get_asset, search_assets, update_asset
from chat.interpreter import interpreter_for
from railroad.config import Config
from railroad.operation import Asset
from railroad.service.media import media_for

web = Blueprint("chat", __name__)


def _config() -> Config:
    return Config(current_app.config["RAILROAD_CONFIG"])


@web.get("/")
def index():
    return render_template("index.html", slm_enabled=bool(current_app.config.get("CHAT_SLM_URL")))


@web.get("/health")
def health():
    slm_enabled = bool(current_app.config.get("CHAT_SLM_URL"))
    return jsonify(
        ok=True,
        service="chat_service",
        interpreter="slm" if slm_enabled else "rules",
        slm_configured=slm_enabled,
    )


@web.get("/shared-static/<path:filename>")
def shared_static(filename: str):
    directory = Path(__file__).resolve().parents[1] / "railroad" / "service" / "static" / "img"
    return send_from_directory(directory, filename)


@web.get("/photos/<path:filename>")
def optimized_photo(filename: str):
    """Serve the same optimized roster media used by app_service."""
    return send_from_directory(_config().resources / "photos" / "optimized", filename)


@web.post("/api/chat")
def chat():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("message"), str):
        return jsonify(error="A JSON message string is required."), 400
    message = payload["message"].strip()
    if not message:
        return jsonify(error="Message cannot be empty."), 400

    interpreter = interpreter_for(
        current_app.config.get("CHAT_SLM_URL"),
        current_app.config.get("CHAT_SLM_MODEL", "local-model"),
    )
    intent = interpreter.interpret(message)
    try:
        if intent.operation == "detail" and intent.entity_id:
            asset = get_asset(_config(), intent.entity_id)
            return jsonify(intent="detail", reply=f"Opened {intent.entity_id}.", asset=asset)
        if intent.operation == "create":
            return jsonify(intent="create", reply="Complete the new asset form before saving.")
        if intent.operation == "update":
            asset = get_asset(_config(), intent.entity_id) if intent.entity_id else None
            return jsonify(intent="update", reply="Review the asset fields before saving.", asset=asset)

        assets = search_assets(_config(), intent.query, intent.entity_type)
        count = len(assets)
        reply = f"Found {count} matching {'asset' if count == 1 else 'assets'}."
        return jsonify(intent="search", query=intent.query, reply=reply, assets=assets, count=count)
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        return jsonify(error=str(exc)), 400


@web.get("/api/assets/<entity_id>")
def asset_detail(entity_id: str):
    try:
        return jsonify(get_asset(_config(), entity_id))
    except (FileNotFoundError, TypeError, ValueError):
        return jsonify(error=f"Asset '{entity_id}' was not found."), 404


@web.get("/api/assets/<entity_id>/media")
def asset_media(entity_id: str):
    try:
        Asset(_config()).view(entity_id)
    except (FileNotFoundError, TypeError, ValueError):
        return jsonify(error=f"Asset '{entity_id}' was not found."), 404
    return jsonify(media=media_for(_config(), entity_id))


@web.patch("/api/assets/<entity_id>")
def asset_update(entity_id: str):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="A JSON patch object is required."), 400
    try:
        return jsonify(update_asset(_config(), entity_id, payload))
    except FileNotFoundError:
        return jsonify(error=f"Asset '{entity_id}' was not found."), 404
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify(error=str(exc)), 400


@web.post("/api/assets")
def asset_create():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="A JSON object is required."), 400
    try:
        return jsonify(create_asset(_config(), payload)), 201
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify(error=str(exc)), 400
