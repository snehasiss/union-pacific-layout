#!/usr/bin/env python3

"""
Data access object for locomotive persistence.
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
from railroad.rs.loco import Loco
from railroad.rs.loco_type import LocoType


class LocoDAO:
    """Persist and retrieve Loco domain objects."""

    def __init__(
        self,
        config: Config,
        stream: IOStream | None = None,
    ) -> None:
        self._config = config
        self._stream = stream or IOStream()
        self._data = config.data_config("loco")

    def save(self, loco: Loco) -> None:
        """Persist a locomotive using its existing identity."""

        if not isinstance(loco, Loco):
            raise TypeError("loco must be a Loco.")

        if loco.identity.entity_type != EntityType.LOCO:
            raise ValueError(
                "Loco identity must have EntityType.LOCO."
            )

        path = self._path(loco.id)
        payload = self._to_dict(loco)
        data = json.dumps(payload, indent=4)

        self._stream.write(path, data)

    def get(self, entity_id: str) -> Loco:
        """Load a locomotive by persistent ID."""

        path = self._path(entity_id)

        if not self._stream.exists(path):
            raise FileNotFoundError(
                f"Loco '{entity_id}' does not exist."
            )

        data = self._stream.read(path)
        payload = json.loads(data)

        return self._from_dict(payload)

    def exists(self, entity_id: str) -> bool:
        """Return True if a locomotive exists."""

        return self._stream.exists(self._path(entity_id))

    def list(self) -> list[Loco]:
        """Load all persisted locomotives."""

        directory = self._data.path

        if not directory.exists():
            return []

        locos = []

        for path in sorted(directory.glob("*.json")):
            locos.append(self.get(path.stem))

        return locos

    def next_id(self) -> str:
        """Return the next available locomotive ID."""

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
        """Return the persistence path for an entity ID."""

        prefix, _ = self._parse_id(entity_id)

        if prefix != self._data.prefix:
            raise ValueError(
                f"Invalid locomotive ID '{entity_id}'."
            )

        return self._data.path / f"{entity_id}.json"

    @staticmethod
    def _parse_id(entity_id: str) -> tuple[str, int]:
        """Parse a persistent entity ID."""

        if not isinstance(entity_id, str):
            raise TypeError("entity_id must be a string.")

        if len(entity_id) < 4:
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

        if (
            len(entity_id[1:]) != 3
            or number < 1
            or number > 999
        ):
            raise ValueError(
                f"Invalid entity ID '{entity_id}'."
            )

        return prefix, number

    @staticmethod
    def _to_dict(loco: Loco) -> dict:
        """Convert a Loco domain object to JSON-compatible data."""

        return {
            "identity": {
                "id": loco.identity.id,
                "entity_type": loco.identity.entity_type.value,
                "railroad": loco.identity.railroad,
                "reporting_mark": loco.identity.reporting_mark,
                "road_number": loco.identity.road_number,
            },
            "loco_type": loco.loco_type.value,
            "prototype": {
                "builder": loco.prototype.builder,
                "model": loco.prototype.model,
                "nickname": loco.prototype.nickname,
                "purpose": loco.prototype.purpose.value,
            },
            "model": {
                "manufacturer": loco.model.manufacturer,
                "product": loco.model.product,
            },
            "electronics": {
                "dcc": loco.electronics.dcc,
                "decoder": loco.electronics.decoder,
                "address": loco.electronics.address,
                "sound": loco.electronics.sound,
                "light": loco.electronics.light,
                "smoke": loco.electronics.smoke,
            },
            "ownership": {
                "status": loco.ownership.status.value,
                "source": loco.ownership.source,
                "price": loco.ownership.price,
                "acquired": (
                    loco.ownership.acquired.isoformat()
                    if loco.ownership.acquired is not None
                    else None
                ),
            },
        }

    @staticmethod
    def _from_dict(payload: dict) -> Loco:
        """Construct a Loco from persisted JSON data."""

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
            nickname=prototype_data["nickname"],
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

        return Loco(
            identity=identity,
            loco_type=LocoType(payload["loco_type"]),
            prototype=prototype,
            model=model,
            electronics=electronics,
            ownership=ownership,
        )
