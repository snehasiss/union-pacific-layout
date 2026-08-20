#!/usr/bin/env python3
#
# railroad/dao/mow.py
#

"""
Data access object for Maintenance-of-Way assets.
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
from railroad.domain.model import Model
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.mow import MOW
from railroad.rs.mow_type import MOWType


class MowDAO:
    """Data access object for MOW persistence."""

    def __init__(
        self,
        config: Config,
        stream: IOStream | None = None,
    ) -> None:
        self._config = config
        self._stream = stream or IOStream()
        self._data = config.data_config("mow")

    def save(self, mow: MOW) -> None:
        """Persist an MOW asset."""

        if not isinstance(mow, MOW):
            raise TypeError("mow must be an MOW.")

        if mow.identity.entity_type != EntityType.MOW:
            raise ValueError(
                "MOW identity must have EntityType.MOW."
            )

        path = self._path(mow.id)
        payload = self._to_dict(mow)

        self._stream.write(
            path,
            json.dumps(payload, indent=4),
        )

    def get(self, entity_id: str) -> MOW:
        """Load an MOW asset by persistent ID."""

        path = self._path(entity_id)

        if not self._stream.exists(path):
            raise FileNotFoundError(
                f"MOW '{entity_id}' does not exist."
            )

        payload = json.loads(self._stream.read(path))

        return self._from_dict(payload)

    def exists(self, entity_id: str) -> bool:
        """Return True when the specified MOW exists."""

        return self._stream.exists(self._path(entity_id))

    def list(self) -> list[MOW]:
        """Return all persisted MOW assets."""

        directory = self._data.path

        if not directory.exists():
            return []

        mow_assets = []

        for path in sorted(directory.glob("*.json")):
            mow_assets.append(self.get(path.stem))

        return mow_assets

    def next_id(self) -> str:
        """Return the next available MOW ID."""

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
        """Return the persistence path for an MOW ID."""

        prefix, _ = self._parse_id(entity_id)

        if prefix != self._data.prefix:
            raise ValueError(
                f"Invalid MOW ID '{entity_id}'."
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
    def _to_dict(mow: MOW) -> dict:
        """Convert an MOW asset into JSON-compatible data."""

        return {
            "identity": {
                "id": mow.identity.id,
                "entity_type": mow.identity.entity_type.value,
                "railroad": mow.identity.railroad,
                "reporting_mark": mow.identity.reporting_mark,
                "road_number": mow.identity.road_number,
            },
            "mow_type": mow.mow_type.value,
            "self_propelled": mow.self_propelled,
            "prototype": {
                "builder": mow.prototype.builder,
                "model": mow.prototype.model,
                "nickname": mow.prototype.nickname,
                "purpose": mow.prototype.purpose.value,
            },
            "model": {
                "manufacturer": mow.model.manufacturer,
                "product": mow.model.product,
            },
            "control": {
                "type": mow.control.type.value,
                "decoder": mow.control.decoder,
                "address": mow.control.address,
                "sound": mow.control.sound,
                "light": mow.control.light,
                "smoke": mow.control.smoke,
            },
            "asset": {
                "status": mow.asset.status.value,
                "source": mow.asset.source,
                "price": mow.asset.price,
                "acquired": (
                    mow.asset.acquired.isoformat()
                    if mow.asset.acquired is not None
                    else None
                ),
            },
        }

    @staticmethod
    def _from_dict(payload: dict) -> MOW:
        """Construct an MOW asset from persisted JSON data."""

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
            manufacturer=model_data.get("manufacturer"),
            product=model_data.get("product"),
        )

        control = Control(
            type=ControlType(control_data["type"]),
            decoder=control_data.get("decoder"),
            address=control_data.get("address"),
            sound=control_data["sound"],
            light=control_data["light"],
            smoke=control_data["smoke"],
        )

        asset = Asset(
            status=AssetStatus(asset_data["status"]),
            source=asset_data.get("source"),
            price=asset_data.get("price"),
            acquired=acquired,
        )

        return MOW(
            identity=identity,
            prototype=prototype,
            model=model,
            control=control,
            asset=asset,
            mow_type=MOWType(payload["mow_type"]),
            self_propelled=payload["self_propelled"],
        )
