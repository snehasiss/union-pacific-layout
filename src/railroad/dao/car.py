#!/usr/bin/env python3
#
# railroad/dao/car.py
#

"""
Data access object for railroad cars.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from railroad.config import Config
from railroad.dao.iostream import IOStream
from railroad.domain.electronics import Electronics
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.ownership import Ownership, OwnershipStatus
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.car import Car
from railroad.rs.car_type import CarType


class CarDAO:
    """Data access object for Car persistence."""

    def __init__(
        self,
        config: Config,
        stream: IOStream | None = None,
    ) -> None:
        self._config = config
        self._stream = stream or IOStream()
        self._data = config.data_config("car")

    def save(self, car: Car) -> None:
        """Persist a Car."""

        if not isinstance(car, Car):
            raise TypeError("car must be a Car.")

        if car.identity.entity_type != EntityType.CAR:
            raise ValueError(
                "Car identity must have EntityType.CAR."
            )

        path = self._path(car.id)
        payload = self._to_dict(car)

        self._stream.write(
            path,
            json.dumps(payload, indent=4),
        )

    def get(self, entity_id: str) -> Car:
        """Load a Car by persistent ID."""

        path = self._path(entity_id)

        if not self._stream.exists(path):
            raise FileNotFoundError(
                f"Car '{entity_id}' does not exist."
            )

        payload = json.loads(self._stream.read(path))

        return self._from_dict(payload)

    def exists(self, entity_id: str) -> bool:
        """Return True when the specified Car exists."""

        return self._stream.exists(self._path(entity_id))

    def list(self) -> list[Car]:
        """Return all persisted Cars."""

        directory = self._data.path

        if not directory.exists():
            return []

        cars = []

        for path in sorted(directory.glob("*.json")):
            cars.append(self.get(path.stem))

        return cars

    def next_id(self) -> str:
        """Return the next available Car ID."""

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
            raise ValueError(
                f"Maximum ID {prefix}999 has been reached."
            )

        return f"{prefix}{next_number:03d}"

    def _path(self, entity_id: str) -> Path:
        """Return the persistence path for a Car ID."""

        prefix, _ = self._parse_id(entity_id)

        if prefix != self._data.prefix:
            raise ValueError(
                f"Invalid car ID '{entity_id}'."
            )

        return self._data.path / f"{entity_id}.json"

    @staticmethod
    def _parse_id(entity_id: str) -> tuple[str, int]:
        """Parse a persistent entity ID."""

        if not isinstance(entity_id, str):
            raise TypeError("entity_id must be a string.")

        if len(entity_id) != 4:
            raise ValueError(
                f"Invalid entity ID '{entity_id}'."
            )

        prefix = entity_id[0]

        try:
            number = int(entity_id[1:])
        except ValueError as exc:
            raise ValueError(
                f"Invalid entity ID '{entity_id}'."
            ) from exc

        if number < 1 or number > 999:
            raise ValueError(
                f"Invalid entity ID '{entity_id}'."
            )

        return prefix, number

    @staticmethod
    def _to_dict(car: Car) -> dict:
        """Convert a Car into JSON-compatible data."""

        return {
            "identity": {
                "id": car.identity.id,
                "entity_type": car.identity.entity_type.value,
                "railroad": car.identity.railroad,
                "reporting_mark": car.identity.reporting_mark,
                "road_number": car.identity.road_number,
            },
            "car_type": car.car_type.value,
            "prototype": {
                "builder": car.prototype.builder,
                "model": car.prototype.model,
                "nickname": car.prototype.nickname,
                "purpose": car.prototype.purpose.value,
            },
            "model": {
                "manufacturer": car.model.manufacturer,
                "product": car.model.product,
            },
            "electronics": {
                "dcc": car.electronics.dcc,
                "decoder": car.electronics.decoder,
                "address": car.electronics.address,
                "sound": car.electronics.sound,
                "light": car.electronics.light,
                "smoke": car.electronics.smoke,
            },
            "ownership": {
                "status": car.ownership.status.value,
                "source": car.ownership.source,
                "price": car.ownership.price,
                "acquired": (
                    car.ownership.acquired.isoformat()
                    if car.ownership.acquired is not None
                    else None
                ),
            },
        }

    @staticmethod
    def _from_dict(payload: dict) -> Car:
        """Construct a Car from persisted JSON data."""

        identity_data = payload["identity"]
        prototype_data = payload["prototype"]
        model_data = payload["model"]
        electronics_data = payload["electronics"]
        ownership_data = payload["ownership"]

        acquired = ownership_data.get("acquired")

        if acquired is not None:
            acquired = date.fromisoformat(acquired)

        identity = Identity.from_existing(
            id=identity_data["id"],
            entity_type=EntityType(identity_data["entity_type"]),
            railroad=identity_data["railroad"],
            reporting_mark=identity_data["reporting_mark"],
            road_number=identity_data["road_number"],
        )

        prototype = Prototype(
            builder=prototype_data["builder"],
            model=prototype_data["model"],
            nickname=prototype_data.get("nickname"),
            purpose=Purpose(prototype_data["purpose"]),
        )

        model = Model(
            manufacturer=model_data.get("manufacturer"),
            product=model_data.get("product"),
        )

        electronics = Electronics(
            dcc=electronics_data["dcc"],
            decoder=electronics_data.get("decoder"),
            address=electronics_data.get("address"),
            sound=electronics_data["sound"],
            light=electronics_data["light"],
            smoke=electronics_data["smoke"],
        )

        ownership = Ownership(
            status=OwnershipStatus(ownership_data["status"]),
            source=ownership_data.get("source"),
            price=ownership_data.get("price"),
            acquired=acquired,
        )

        return Car(
            identity=identity,
            prototype=prototype,
            model=model,
            electronics=electronics,
            ownership=ownership,
            car_type=CarType(payload["car_type"]),
        )
