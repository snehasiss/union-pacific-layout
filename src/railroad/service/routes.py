"""Server-rendered Flask routes backed by railroad operations."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass, replace
from datetime import date
from enum import Enum

from flask import Blueprint, abort, current_app, jsonify, redirect, render_template, request, url_for

from railroad.config import Config
from railroad.domain.control import Control
from railroad.domain.identity import EntityType
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.operation import Asset, Roster
from railroad.rs.car import Car, CarType
from railroad.rs.loco import Loco, LocoType
from railroad.rs.mow import MOW, MOWType


web = Blueprint("web", __name__)


def _config() -> Config:
    return Config(current_app.config["RAILROAD_CONFIG"])


@web.get("/")
def roster():
    criteria = {}
    if reporting_mark := request.args.get("reporting_mark"):
        criteria["reporting_mark"] = reporting_mark.upper()
    if status := request.args.get("status"):
        criteria["model.status"] = Status(status)
    collection = Roster.from_config(_config())
    ids = collection.search(criteria)
    return render_template("roster.html", ids=ids, statuses=Status, selected=request.args)


@web.get("/assets/<entity_id>")
def view_asset(entity_id: str):
    try:
        asset = Asset(_config()).view(entity_id)
    except (FileNotFoundError, ValueError, TypeError):
        abort(404)
    return render_template("asset.html", asset=asset, payload=json.dumps(_jsonable(asset.object), indent=2))


@web.post("/assets/<entity_id>/retire")
def retire_asset(entity_id: str):
    try:
        Asset(_config()).view(entity_id).retire()
    except (FileNotFoundError, ValueError, TypeError):
        abort(404)
    return redirect(url_for("web.view_asset", entity_id=entity_id))


@web.post("/assets/<entity_id>/update")
def update_asset(entity_id: str):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="JSON object required."), 400
    try:
        asset = Asset(_config()).view(entity_id)
        _apply_patch(asset.object, payload)
        asset.update()
    except (FileNotFoundError, ValueError, TypeError, KeyError) as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(_jsonable(asset.object))


@web.post("/assets")
def create_asset():
    payload = request.get_json(silent=True) or {}
    try:
        entity_type = EntityType(payload["type"])
        patch = payload.get("patch", {})
        if not isinstance(patch, dict):
            raise TypeError("patch must be a JSON object.")
        asset = Asset(_config()).create(
            entity_type,
            lambda identity: _build(entity_type, identity, patch),
            railroad=payload.get("railroad", "Union Pacific"),
            reporting_mark=payload.get("reporting_mark", "UP"),
            road_number=payload.get("road_number", "UNASSIGNED"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(_jsonable(asset.object)), 201


def _build(entity_type, identity, patch):
    prototype = Prototype("Unknown", "Unknown", None, Purpose.FREIGHT)
    if entity_type == EntityType.LOCO:
        obj = Loco(identity, LocoType.DIESEL, prototype, Model(), Control())
    elif entity_type == EntityType.CAR:
        obj = Car(identity, prototype, Model(), Control(), CarType.WAGON)
    elif entity_type == EntityType.MOW:
        obj = MOW(identity, prototype, Model(), Control(), MOWType.MPV, False)
    else:
        raise ValueError(f"Unsupported creation type '{entity_type.value}'.")
    _apply_patch(obj, patch)
    return obj


def _apply_patch(target, patch):
    if "identity" in patch:
        raise ValueError("identity cannot be updated.")
    for name, value in patch.items():
        if not hasattr(target, name):
            raise KeyError(f"Unknown field '{name}'.")
        current = getattr(target, name)
        if is_dataclass(current) and isinstance(value, dict):
            setattr(target, name, _patched_dataclass(current, value))
        else:
            setattr(target, name, _coerce(current, value))


def _patched_dataclass(value, patch):
    return replace(value, **{name: _coerce(getattr(value, name), item) for name, item in patch.items()})


def _coerce(current, value):
    if isinstance(current, Enum):
        return type(current)(value)
    if isinstance(current, date) and isinstance(value, str):
        return date.fromisoformat(value)
    return value


def _jsonable(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, date):
        return value.isoformat()
    if is_dataclass(value):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    return value
