from __future__ import annotations

from flask import current_app, jsonify, request

from . import api
from ..serial import commands
from ..serial.controller import SerialRequestTimeout
from ..serial.discovery import available_ports
from ..roster import available_locomotives


def _controller():
    return current_app.extensions["csb1_controller"]


def _state():
    return current_app.extensions["csb1_state"]


@api.get("/status")
def get_status():
    return jsonify(_state().snapshot())


@api.get("/locomotives")
def get_locomotives():
    locomotives = available_locomotives()
    return jsonify({"locomotives": locomotives, "count": len(locomotives)})


@api.get("/serial/ports")
def get_ports():
    return jsonify({"ports": available_ports()})


@api.post("/serial/connect")
def connect_serial():
    payload = request.get_json(silent=True) or {}
    try:
        port = _controller().connect(payload.get("port"))
        _controller().send(commands.status())
        return jsonify({"connected": True, "port": port})
    except (RuntimeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 409


@api.post("/serial/disconnect")
def disconnect_serial():
    _controller().disconnect()
    return jsonify({"connected": False})


@api.put("/power")
def set_power():
    payload = request.get_json(silent=True) or {}
    try:
        state = payload["state"]
        _controller().send(commands.power(state, payload.get("track")))
        return jsonify({"accepted": True, "state": state}), 202
    except KeyError:
        return jsonify({"error": "Missing required field: state"}), 400
    except (RuntimeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 409


@api.post("/programming/cv/read")
def read_cv():
    payload = request.get_json(silent=True) or {}
    try:
        cv = int(payload["cv"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Required integer field: cv"}), 400
    try:
        callback = 1
        event = _controller().request(
            commands.read_cv(cv, callback),
            lambda candidate: candidate.type == "cv"
            and candidate.data.get("cv") == cv
            and candidate.data.get("callback") == callback,
        )
        value = int(event.data["value"])
        if value < 0:
            return jsonify({"error": f"Decoder did not acknowledge CV {cv}"}), 409
        return jsonify({"cv": cv, "value": value, "confirmed": True, "mode": "service"})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except SerialRequestTimeout as exc:
        return jsonify({"error": str(exc)}), 504
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 409


@api.put("/programming/cv")
def write_cv():
    payload = request.get_json(silent=True) or {}
    try:
        cv = int(payload["cv"])
        value = int(payload["value"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Required integer fields: cv and value"}), 400
    try:
        event = _controller().request(
            commands.write_cv(cv, value),
            lambda candidate: candidate.type == "cv"
            and candidate.data.get("cv") == cv,
        )
        confirmed_value = int(event.data["value"])
        if confirmed_value != value:
            return jsonify({"error": f"Decoder did not confirm writing CV {cv}"}), 409
        return jsonify({"cv": cv, "value": value, "confirmed": True, "mode": "service"})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except SerialRequestTimeout as exc:
        return jsonify({"error": str(exc)}), 504
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 409


@api.post("/emergency-stop")
def emergency_stop():
    try:
        _controller().send(commands.emergency_stop(), priority=True)
        _state().update(emergencyStop=True)
        current_app.extensions["socketio"].emit("state:changed", _state().snapshot(), namespace="/csb1")
        return jsonify({"accepted": True}), 202
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 409


@api.put("/locomotives/<int:address>/throttle")
def set_throttle(address: int):
    payload = request.get_json(silent=True) or {}
    try:
        speed = int(payload["speed"])
        direction = payload["direction"]
        _controller().send(commands.throttle(address, speed, direction))
        locomotive = _state().update_locomotive(address, speed=speed, direction=direction)
        current_app.extensions["socketio"].emit("state:changed", _state().snapshot(), namespace="/csb1")
        return jsonify({"accepted": True, "locomotive": locomotive}), 202
    except (KeyError, TypeError):
        return jsonify({"error": "Required fields: speed and direction"}), 400
    except (RuntimeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 409


@api.post("/locomotives/<int:address>/stop")
def stop_locomotive(address: int):
    payload = request.get_json(silent=True) or {}
    direction = payload.get("direction", "forward")
    try:
        _controller().send(commands.throttle(address, 0, direction), priority=True)
        locomotive = _state().update_locomotive(address, speed=0, direction=direction)
        current_app.extensions["socketio"].emit("state:changed", _state().snapshot(), namespace="/csb1")
        return jsonify({"accepted": True, "locomotive": locomotive}), 202
    except (RuntimeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 409


@api.put("/locomotives/<int:address>/functions/<int:number>")
def set_function(address: int, number: int):
    payload = request.get_json(silent=True) or {}
    if "active" not in payload or not isinstance(payload["active"], bool):
        return jsonify({"error": "Required boolean field: active"}), 400
    try:
        active = payload["active"]
        _controller().send(commands.function(address, number, active))
        snapshot = _state().snapshot()
        existing = snapshot["locomotives"].get(str(address), {})
        functions = dict(existing.get("functions", {}))
        functions[str(number)] = active
        locomotive = _state().update_locomotive(address, functions=functions)
        current_app.extensions["socketio"].emit("state:changed", _state().snapshot(), namespace="/csb1")
        return jsonify({"accepted": True, "locomotive": locomotive}), 202
    except (RuntimeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 409
