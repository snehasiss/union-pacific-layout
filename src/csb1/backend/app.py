from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

from .api import api
from .config import load_config
from .serial.controller import SerialController
from .serial.parser import ProtocolEvent
from .state import StateStore


def create_app(profile: str | None = None) -> tuple[Flask, SocketIO]:
    config = load_config(profile)
    frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    app = Flask(
        __name__,
        static_folder=str(frontend_dist / "assets"),
        static_url_path="/assets",
    )
    app.config["CSB1_CONFIG"] = config
    app.config["SECRET_KEY"] = config["server"]["secretKey"]

    socketio = SocketIO(app, cors_allowed_origins=config["server"]["allowedOrigins"], async_mode="threading")
    state = StateStore(config["profile"])

    def broadcast_state() -> None:
        socketio.emit("state:changed", state.snapshot(), namespace="/csb1")

    def on_connection(status: str, port: str | None, error: str | None) -> None:
        state.set_connection(status, port, error)
        broadcast_state()

    def on_protocol_event(event: ProtocolEvent) -> None:
        if event.type == "power":
            state.update(trackPower=event.data["state"])
            if event.data["state"] == "off":
                state.update(emergencyStop=False)
        elif event.type == "system":
            state.update(commandStation=event.data)
        elif event.type == "locomotive":
            locomotive = dict(event.data)
            address = int(locomotive.pop("address"))
            state.update_locomotive(address, **locomotive)
        socketio.emit(
            "protocol:event",
            {"type": event.type, "data": event.data, "raw": event.raw},
            namespace="/csb1",
        )
        broadcast_state()

    controller = SerialController(config["serial"], on_protocol_event, on_connection)
    app.extensions["socketio"] = socketio
    app.extensions["csb1_state"] = state
    app.extensions["csb1_controller"] = controller
    app.register_blueprint(api)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "profile": config["profile"]})

    @app.get("/")
    @app.get("/<path:path>")
    def frontend(path: str = "index.html"):
        requested = frontend_dist / path
        if path != "index.html" and requested.is_file():
            return send_from_directory(frontend_dist, path)
        if (frontend_dist / "index.html").is_file():
            return send_from_directory(frontend_dist, "index.html")
        return jsonify({"error": "React application has not been built"}), 404

    @socketio.on("connect", namespace="/csb1")
    def socket_connect():
        emit("state:snapshot", state.snapshot())

    if config["serial"]["connectOnStartup"]:
        try:
            controller.connect()
        except RuntimeError:
            pass

    return app, socketio
