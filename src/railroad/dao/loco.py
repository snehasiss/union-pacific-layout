#!/usr/bin/env python3
# railroad/dao/loco.py
#

"""
Data access object for locomotive persistence.
"""

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
                "maker": loco.model.maker,
                "scale": loco.model.SCALE,
                "product": loco.model.product,
                "status": loco.model.status.value,
            },
            "control": {
                "type": loco.control.type.value,
                "light": loco.control.light,
                "sound": loco.control.sound,
                "smoke": loco.control.smoke,
                "decoder": loco.control.decoder,
                "address": loco.control.address,
            },
            "asset": {
                "status": loco.asset.status.value,
                "source": loco.asset.source,
                "price": loco.asset.price,
                "acquired": (
                    loco.asset.acquired.isoformat()
                    if loco.asset.acquired is not None
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
        control_data = payload["control"]
        asset_data = payload["asset"]

        acquired = asset_data.get("acquired")

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
            maker=model_data.get("maker"),
            # SCALE=model_data.get("scale"),
            product=model_data.get("product"),
            status=ModelStatus(model_data["status"]),
        )

        control = Control(
            type=ControlType(control_data["type"]),
            light=control_data["light"],
            sound=control_data["sound"],
            smoke=control_data["smoke"],
            decoder=control_data.get("decoder"),
            address=control_data.get("address"),
        )

        asset = Asset(
            status=AssetStatus(asset_data["status"]),
            source=asset_data.get("source"),
            price=asset_data.get("price"),
            acquired=acquired,
        )

        return Loco(
            identity=identity,
            loco_type=LocoType(payload["loco_type"]),
            prototype=prototype,
            model=model,
            control=control,
            asset=asset,
        )
