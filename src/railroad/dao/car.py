#!/usr/bin/env python3
# railroad/dao/car.py

"""Data access object for railroad cars."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from railroad.config import Config
from railroad.dao.iostream import IOStream
from railroad.domain.asset import Asset, AssetStatus
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, ModelStatus
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.car import Car, CarType


class CarDAO:
    """Data access object for Car persistence."""

    def __init__(self, config: Config, stream: IOStream | None = None) -> None:
        self._config = config
        self._stream = stream or IOStream()
        self._data = config.data_config("car")

    def save(self, car: Car) -> None:
        if not isinstance(car, Car):
            raise TypeError("car must be a Car.")
        if car.identity.entity_type != EntityType.CAR:
            raise ValueError("Car identity must have EntityType.CAR.")
        self._stream.write(self._path(car.id), json.dumps(self._to_dict(car), indent=4))

    def get(self, entity_id: str) -> Car:
        path = self._path(entity_id)
        if not self._stream.exists(path):
            raise FileNotFoundError(f"Car '{entity_id}' does not exist.")
        return self._from_dict(json.loads(self._stream.read(path)))

    def exists(self, entity_id: str) -> bool:
        return self._stream.exists(self._path(entity_id))

    def list(self) -> list[Car]:
        directory = self._data.path
        if not directory.exists():
            return []
        return [self.get(path.stem) for path in sorted(directory.glob("*.json"))]

    def next_id(self) -> str:
        directory = self._data.path
        prefix = self._data.prefix
        if not directory.exists():
            return f"{prefix}001"
        numbers = []
        for path in directory.glob(f"{prefix}*.json"):
            try:
                _, number = self._parse_id(path.stem)
                numbers.append(number)
            except ValueError:
                continue
        next_number = max(numbers, default=0) + 1
        if next_number > 999:
            raise ValueError(f"Maximum ID {prefix}999 has been reached.")
        return f"{prefix}{next_number:03d}"

    def _path(self, entity_id: str) -> Path:
        prefix, _ = self._parse_id(entity_id)
        if prefix != self._data.prefix:
            raise ValueError(f"Invalid car ID '{entity_id}'.")
        return self._data.path / f"{entity_id}.json"

    @staticmethod
    def _parse_id(entity_id: str) -> tuple[str, int]:
        if not isinstance(entity_id, str):
            raise TypeError("entity_id must be a string.")
        if len(entity_id) != 4:
            raise ValueError(f"Invalid entity ID '{entity_id}'.")
        prefix = entity_id[0]
        try:
            number = int(entity_id[1:])
        except ValueError as exc:
            raise ValueError(f"Invalid entity ID '{entity_id}'.") from exc
        if number < 1 or number > 999:
            raise ValueError(f"Invalid entity ID '{entity_id}'.")
        return prefix, number

    @staticmethod
    def _to_dict(car: Car) -> dict:
        return {
            "identity": {"id": car.identity.id, "entity_type": car.identity.entity_type.value, "railroad": car.identity.railroad, "reporting_mark": car.identity.reporting_mark, "road_number": car.identity.road_number},
            "car_type": car.car_type.value,
            "prototype": {"builder": car.prototype.builder, "model": car.prototype.model, "nickname": car.prototype.nickname, "purpose": car.prototype.purpose.value},
            "model": {"maker": car.model.maker, "product": car.model.product, "status": car.model.status.value},
            "control": {"type": car.control.type.value, "decoder": car.control.decoder, "address": car.control.address, "sound": car.control.sound, "light": car.control.light, "smoke": car.control.smoke},
            "asset": {"status": car.asset.status.value, "source": car.asset.source, "price": car.asset.price, "acquired": car.asset.acquired.isoformat() if car.asset.acquired is not None else None},
        }

    @staticmethod
    def _from_dict(payload: dict) -> Car:
        identity_data = payload["identity"]
        prototype_data = payload["prototype"]
        model_data = payload["model"]
        control_data = payload["control"]
        asset_data = payload["asset"]
        acquired = asset_data.get("acquired")
        if acquired is not None:
            acquired = date.fromisoformat(acquired)
        identity = Identity.from_existing(id=identity_data["id"], entity_type=EntityType(identity_data["entity_type"]), railroad=identity_data["railroad"], reporting_mark=identity_data["reporting_mark"], road_number=identity_data["road_number"])
        prototype = Prototype(builder=prototype_data["builder"], model=prototype_data["model"], nickname=prototype_data.get("nickname"), purpose=Purpose(prototype_data["purpose"]))
        model = Model(maker=model_data.get("maker"), product=model_data.get("product"), status=ModelStatus(model_data["status"]))
        control = Control(type=ControlType(control_data["type"]), decoder=control_data.get("decoder"), address=control_data.get("address"), sound=control_data["sound"], light=control_data["light"], smoke=control_data["smoke"])
        asset = Asset(status=AssetStatus(asset_data["status"]), source=asset_data.get("source"), price=asset_data.get("price"), acquired=acquired)
        return Car(identity=identity, prototype=prototype, model=model, control=control, asset=asset, car_type=CarType(payload["car_type"])
