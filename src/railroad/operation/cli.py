"""Command-line adapter for railroad operating functions."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass, replace
from datetime import date
from enum import Enum
from pathlib import Path

from railroad.config import Config
from railroad.domain.control import Control
from railroad.domain.identity import EntityType
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.operation import Asset, Roster
from railroad.rs.car import Car, CarType
from railroad.rs.loco import Loco, LocoType
from railroad.rs.mow import MOW, MOWType


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="railroad")
    result.add_argument("--config", default="config/railroad-conf.json")
    commands = result.add_subparsers(dest="command", required=True)

    view = commands.add_parser("view")
    view.add_argument("id")

    retire = commands.add_parser("retire")
    retire.add_argument("id")

    update = commands.add_parser("update")
    update.add_argument("id")
    update_source = update.add_mutually_exclusive_group(required=True)
    update_source.add_argument("--input", type=Path)
    update_source.add_argument("--set", action="append", default=[], metavar="ATTRIBUTE=VALUE")

    create = commands.add_parser("create")
    create.add_argument("--type", required=True, choices=("loco", "car", "mow"))
    create.add_argument("--input", type=Path)
    create.add_argument("--railroad", default="Union Pacific")
    create.add_argument("--reporting-mark", default="UP")
    create.add_argument("--road-number", default="UNASSIGNED")

    search = commands.add_parser("search")
    search.add_argument("--where", action="append", default=[], metavar="PATH=VALUE")
    return result


def run(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    config = Config(args.config)
    try:
        if args.command == "view":
            print(json.dumps(_jsonable(Asset(config).view(args.id).object), indent=2))
        elif args.command == "retire":
            print(Asset(config).view(args.id).retire().id)
        elif args.command == "update":
            asset = Asset(config).view(args.id)
            patch = _read_patch(args.input) if args.input else _set_patch(args.set)
            _apply_patch(asset.object, patch)
            print(asset.update().id)
        elif args.command == "create":
            entity_type = EntityType(args.type)
            patch = _read_patch(args.input) if args.input else {}
            asset = Asset(config).create(
                entity_type,
                lambda identity: _build(entity_type, identity, patch),
                railroad=args.railroad,
                reporting_mark=args.reporting_mark,
                road_number=args.road_number,
            )
            print(asset.id)
        else:
            criteria = _criteria(args.where)
            print("\n".join(Roster.from_config(config).search(criteria)))
    except (FileNotFoundError, TypeError, ValueError, KeyError) as exc:
        parser().error(str(exc))
    return 0


def _build(entity_type: EntityType, identity, patch: dict):
    prototype = Prototype(builder="Unknown", model="Unknown", nickname=None, purpose=Purpose.FREIGHT)
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


def _read_patch(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("JSON input must be an object.")
    if "identity" in value:
        raise ValueError("identity is assigned by the create command and cannot be patched.")
    return value


def _apply_patch(target, patch: dict) -> None:
    for name, value in patch.items():
        if not hasattr(target, name):
            raise KeyError(f"Unknown field '{name}'.")
        current = getattr(target, name)
        if is_dataclass(current) and isinstance(value, dict):
            if name == "identity":
                raise ValueError("identity cannot be updated.")
            setattr(target, name, _patched_dataclass(current, value))
        else:
            setattr(target, name, _coerce(current, value))


def _patched_dataclass(value, patch: dict):
    changes = {}
    for name, replacement in patch.items():
        current = getattr(value, name)
        changes[name] = _patched_dataclass(current, replacement) if is_dataclass(current) and isinstance(replacement, dict) else _coerce(current, replacement)
    return replace(value, **changes)


def _coerce(current, value):
    if isinstance(current, Enum):
        return type(current)(value)
    if isinstance(current, date) and isinstance(value, str):
        return date.fromisoformat(value)
    if isinstance(current, bool) and isinstance(value, str):
        if value.lower() in {"true", "yes"}:
            return True
        if value.lower() in {"false", "no"}:
            return False
        raise ValueError(f"Invalid boolean value '{value}'.")
    if isinstance(current, int) and isinstance(value, str):
        return int(value)
    if isinstance(current, float) and isinstance(value, str):
        return float(value)
    return value


def _criteria(items: list[str]) -> dict[str, object]:
    result = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid criterion '{item}'. Expected PATH=VALUE.")
        path, value = item.split("=", 1)
        result[path] = Status(value) if path == "model.status" else value
    return result


def _set_patch(items: list[str]) -> dict:
    result = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid assignment '{item}'. Expected ATTRIBUTE=VALUE.")
        path, value = item.split("=", 1)
        target = result
        parts = path.split(".")
        for part in parts[:-1]:
            target = target.setdefault(part, {})
            if not isinstance(target, dict):
                raise ValueError(f"Conflicting assignment for '{path}'.")
        target[parts[-1]] = value
    return result


def _jsonable(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, date):
        return value.isoformat()
    if is_dataclass(value):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


if __name__ == "__main__":
    run()
