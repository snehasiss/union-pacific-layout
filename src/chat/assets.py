"""Asset operations used by the chat-facing adapter."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass, replace
from datetime import date
from enum import Enum
from typing import Any

from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType
from railroad.domain.model import Model
from railroad.domain.prototype import Prototype, Purpose
from railroad.operation import Asset, Roster
from railroad.rs.car import Car, CarType
from railroad.rs.loco import Loco, LocoType
from railroad.rs.mow import MOW, MOWType

SUPPORTED_TYPES = (EntityType.LOCO, EntityType.CAR, EntityType.MOW)


def search_assets(config, query: str = "", entity_type: EntityType | None = None) -> list[dict[str, Any]]:
    """Apply the same case-insensitive substring search used by app_service."""
    types = (entity_type,) if entity_type else SUPPORTED_TYPES
    roster = Roster.from_config(config, types)
    ids = set(roster.search_text(query))
    return [jsonable(obj) for obj in roster.objects if obj.id in ids]


def get_asset(config, entity_id: str) -> dict[str, Any]:
    return jsonable(Asset(config).view(entity_id).object)


def create_asset(config, payload: dict[str, Any]) -> dict[str, Any]:
    entity_type = EntityType(payload["type"])
    if entity_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported creation type '{entity_type.value}'.")
    patch = payload.get("patch", {})
    if not isinstance(patch, dict):
        raise TypeError("patch must be a JSON object.")
    asset = Asset(config).create(
        entity_type,
        lambda identity: _build(entity_type, identity, patch),
        railroad=payload.get("railroad", "Union Pacific"),
        reporting_mark=payload.get("reporting_mark", "UP"),
        road_number=payload.get("road_number", "UNASSIGNED"),
    )
    return jsonable(asset.object)


def update_asset(config, entity_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    asset = Asset(config).view(entity_id)
    apply_patch(asset.object, patch)
    asset.update()
    return jsonable(asset.object)


def _build(entity_type: EntityType, identity, patch: dict[str, Any]):
    prototype = Prototype("Unknown", "Unknown", None, Purpose.FREIGHT)
    if entity_type == EntityType.LOCO:
        obj = Loco(identity, LocoType.DIESEL, prototype, Model(), Control())
    elif entity_type == EntityType.CAR:
        obj = Car(identity, prototype, Model(), Control(type=ControlType.UNPOWERED), CarType.WAGON)
    else:
        obj = MOW(identity, prototype, Model(), Control(type=ControlType.UNPOWERED), MOWType.MPV, False)
    apply_patch(obj, patch)
    return obj


def apply_patch(target: Any, patch: dict[str, Any]) -> None:
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


def _patched_dataclass(value: Any, patch: dict[str, Any]):
    unknown = patch.keys() - {field.name for field in value.__dataclass_fields__.values()}
    if unknown:
        raise KeyError(f"Unknown field '{sorted(unknown)[0]}'.")
    return replace(
        value,
        **{name: _coerce(name, getattr(value, name), item) for name, item in patch.items()},
    )


def _coerce(name: str, current: Any, value: Any):
    if value is None or value == "":
        return None if current is None or name in {"nickname", "maker", "product", "source", "price", "acquired", "note"} else value
    if isinstance(current, Enum):
        return type(current)(value)
    if isinstance(current, date) and isinstance(value, str):
        return date.fromisoformat(value)
    if current is None and name == "acquired" and isinstance(value, str):
        return date.fromisoformat(value)
    if current is None and name == "price" and isinstance(value, (int, float, str)):
        return float(value)
    return value


def jsonable(value: Any):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, date):
        return value.isoformat()
    if is_dataclass(value):
        return {key: jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    return value
