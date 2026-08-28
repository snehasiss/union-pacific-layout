"""Server-rendered Flask routes backed by railroad operations."""

from __future__ import annotations

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
from railroad.service.media import media_for


web = Blueprint("web", __name__)


def _config() -> Config:
    return Config(current_app.config["RAILROAD_CONFIG"])


@web.get("/")
def roster():
    return render_template("roster.html", statuses=Status, entity_types=EntityType)


@web.get("/assets/<entity_id>")
def view_asset(entity_id: str):
    try:
        Asset(_config()).view(entity_id)
    except (FileNotFoundError, ValueError, TypeError):
        abort(404)
    return render_template("asset.html", entity_id=entity_id)


@web.get("/api/assets")
def list_assets():
    try:
        entity_types = _entity_types(request.args.get("type"))
        criteria = _criteria(request.args)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    collection = Roster.from_config(_config(), entity_types)
    ids = set(collection.search(criteria))
    return jsonify(
        assets=[_jsonable(obj) for obj in collection.objects if obj.id in ids],
        count=len(ids),
    )


@web.get("/api/assets/<entity_id>")
def get_asset(entity_id: str):
    try:
        asset = Asset(_config()).view(entity_id)
    except (FileNotFoundError, ValueError, TypeError):
        return jsonify(error=f"Asset '{entity_id}' was not found."), 404
    return jsonify(_jsonable(asset.object))


@web.get("/api/assets/<entity_id>/media")
def get_asset_media(entity_id: str):
    try:
        Asset(_config()).view(entity_id)
    except (FileNotFoundError, ValueError, TypeError):
        return jsonify(error=f"Asset '{entity_id}' was not found."), 404
    return jsonify(media=media_for(_config(), entity_id))


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


def _entity_types(value: str | None) -> tuple[EntityType, ...]:
    if not value or value == "all":
        return (EntityType.LOCO, EntityType.CAR, EntityType.MOW)
    supported = {entity_type.value: entity_type for entity_type in (EntityType.LOCO, EntityType.CAR, EntityType.MOW)}
    if value not in supported:
        raise ValueError("type must be one of: all, loco, car, mow.")
    return (supported[value],)


def _criteria(values) -> dict[str, object]:
    criteria: dict[str, object] = {}
    if reporting_mark := values.get("reporting_mark"):
        criteria["identity.reporting_mark"] = reporting_mark.upper()
    if status := values.get("status"):
        try:
            criteria["model.status"] = Status(status)
        except ValueError as exc:
            raise ValueError(f"Unknown status '{status}'.") from exc
    return criteria


def _apply_patch(target, patch):
    for name, value in patch.items():
        if not hasattr(target, name):
            raise KeyError(f"Unknown field '{name}'.")
        current = getattr(target, name)
        if is_dataclass(current) and isinstance(value, dict):
            if name == "identity" and {"id", "entity_type"} & value.keys():
                raise ValueError("identity id and entity_type cannot be updated.")
            setattr(target, name, _patched_dataclass(current, value))
        else:
            setattr(target, name, _coerce(name, current, value))


def _patched_dataclass(value, patch):
    return replace(
        value,
        **{name: _coerce(name, getattr(value, name), item) for name, item in patch.items()},
    )


def _coerce(name, current, value):
    if value is None:
        return None
    if isinstance(current, Enum):
        return type(current)(value)
    if isinstance(current, date) and isinstance(value, str):
        return date.fromisoformat(value)
    if current is None and name == "acquired" and isinstance(value, str):
        return date.fromisoformat(value)
    if current is None and name == "price" and isinstance(value, (int, float)):
        return float(value)
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
