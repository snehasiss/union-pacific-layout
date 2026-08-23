#!/usr/bin/env python3
# railroad/tests/dao/test_mow.py
#

"""
Tests for MowDAO.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from railroad.config import Config
from railroad.dao.mow import MowDAO
from railroad.domain.asset import Asset, AssetStatus
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, ModelStatus
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.mow import MOW
from railroad.rs.mow_type import MOWType


def create_config(tmp_path: Path) -> Config:
    """Create an isolated test configuration."""

    config_dir = tmp_path / "config"
    config_dir.mkdir()

    config_file = config_dir / "railroad-conf.json"

    config_file.write_text(
        json.dumps(
            {
                "application": {
                    "name": "test-railroad",
                },
                "paths": {
                    "config": "config",
                    "data": "data",
                    "resources": "resources",
                    "logs": "logs",
                },
                "data": {
                    "mow": {
                        "path": "mow",
                        "prefix": "M",
                    },
                },
                "resources": {
                    "drawings": "resources/drawings",
                    "media": "resources/media",
                },
            }
        ),
        encoding="utf-8",
    )

    return Config(config_file)


def create_mow(
    mow_id: str = "M001",
    status: AssetStatus = AssetStatus.OWNED,
    acquired: date | None = date(2026, 1, 1),
) -> MOW:
    """Create a representative MOW asset for testing."""

    identity = Identity(
        id=mow_id,
        entity_type=EntityType.MOW,
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number="1001",
    )

    prototype = Prototype(
        builder="Jordan Spreader",
        model="MOW Spreader",
        nickname=None,
        purpose=Purpose.FREIGHT,
    )

    model = Model(
        maker="Athearn",
        # scale="HO",
        product="MOW Spreader",
        status=ModelStatus.ACTIVE,
    )

    control = Control(
        type=ControlType.DC,
        light=True,
        sound=False,
        smoke=False,
        decoder=None,
        address=0,
    )

    asset = Asset(
        status=status,
        #status=AssetStatus.OWNED,
        source="Model Train Stuff",
        price=79.99,
        acquired=acquired,
    )

    return MOW(
        identity=identity,
        prototype=prototype,
        model=model,
        control=control,
        asset=asset,
        mow_type=MOWType.CLEANER,
        self_propelled=False,
    )


def test_save_creates_json_file(tmp_path: Path) -> None:
    """Saving an MOW asset creates its JSON file."""

    dao = MowDAO(create_config(tmp_path))

    dao.save(create_mow())

    assert (tmp_path / "data" / "mow" / "M001.json").is_file()


def test_save_writes_expected_json(tmp_path: Path) -> None:
    """Saving an MOW asset writes the current domain structure."""

    dao = MowDAO(create_config(tmp_path))

    dao.save(create_mow())

    path = tmp_path / "data" / "mow" / "M001.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["identity"] == {
        "id": "M001",
        "entity_type": "mow",
        "railroad": "Union Pacific",
        "reporting_mark": "UP",
        "road_number": "1001",
    }

    assert payload["mow_type"] == "cleaner"
    assert payload["self_propelled"] is False

    assert payload["prototype"] == {
        "builder": "Jordan Spreader",
        "model": "MOW Spreader",
        "nickname": None,
        "purpose": "freight",
    }

    assert payload["model"] == {
        "maker": "Athearn",
        # "scale": "HO",
        "product": "MOW Spreader",
        "status": "active",
    }

    assert payload["control"] == {
        "type": "dc",
        "decoder": None,
        "address": 0,
        "sound": False,
        "light": True,
        "smoke": False,
    }

    assert payload["asset"] == {
        "status": "owned",
        "source": "Model Train Stuff",
        "price": 79.99,
        "acquired": "2026-01-01",
    }

    assert "electronics" not in payload
    assert "ownership" not in payload


def test_get_reconstructs_mow(tmp_path: Path) -> None:
    """A persisted MOW asset can be reconstructed."""

    dao = MowDAO(create_config(tmp_path))
    dao.save(create_mow())

    mow = dao.get("M001")

    assert mow.id == "M001"
    assert mow.entity_type == EntityType.MOW
    assert mow.railroad == "Union Pacific"
    assert mow.reporting_mark == "UP"
    assert mow.road_number == "1001"

    assert mow.mow_type == MOWType.CLEANER
    assert mow.self_propelled is False

    assert mow.prototype.builder == "Jordan Spreader"
    assert mow.prototype.model == "MOW Spreader"
    assert mow.prototype.nickname is None
    assert mow.prototype.purpose == Purpose.FREIGHT

    assert mow.model.maker == "Athearn"
    # assert mow.model.scale == "HO"
    assert mow.model.product == "MOW Spreader"
    assert mow.model.status == ModelStatus.ACTIVE

    assert mow.control.type == ControlType.DC
    assert mow.control.decoder is None
    assert mow.control.address == 0
    assert mow.control.light is True
    assert mow.control.sound is False
    assert mow.control.smoke is False

    assert mow.asset.status == AssetStatus.OWNED
    assert mow.asset.source == "Model Train Stuff"
    assert mow.asset.price == 79.99
    assert mow.asset.acquired == date(2026, 1, 1)


def test_get_mow_without_acquisition_date(tmp_path: Path) -> None:
    """An MOW asset without an acquisition date can be persisted."""

    dao = MowDAO(create_config(tmp_path))

    dao.save(
        create_mow(
            status=AssetStatus.INTENT,
            acquired=None,
        )
    )

    mow = dao.get("M001")

    assert mow.asset.status == AssetStatus.INTENT
    assert mow.asset.acquired is None


def test_exists(tmp_path: Path) -> None:
    """exists() correctly identifies persisted MOW assets."""

    dao = MowDAO(create_config(tmp_path))

    assert dao.exists("M001") is False

    dao.save(create_mow())

    assert dao.exists("M001") is True


def test_list_returns_all_mow(tmp_path: Path) -> None:
    """list() returns all persisted MOW assets."""

    dao = MowDAO(create_config(tmp_path))

    dao.save(create_mow("M001"))
    dao.save(create_mow("M002"))
    dao.save(create_mow("M003"))

    mow_assets = dao.list()

    assert len(mow_assets) == 3
    assert [mow.id for mow in mow_assets] == [
        "M001",
        "M002",
        "M003",
    ]


def test_next_id(tmp_path: Path) -> None:
    """next_id() returns the next available MOW ID."""

    dao = MowDAO(create_config(tmp_path))

    assert dao.next_id() == "M001"

    dao.save(create_mow("M001"))
    assert dao.next_id() == "M002"

    dao.save(create_mow("M002"))
    assert dao.next_id() == "M003"


def test_save_replaces_existing_mow(tmp_path: Path) -> None:
    """Saving the same ID replaces the existing MOW asset."""

    dao = MowDAO(create_config(tmp_path))

    dao.save(create_mow())

    replacement = create_mow()
    replacement.model = Model(
        maker="Bachmann",
        # scale="HO",
        product="MOW Equipment",
    )

    dao.save(replacement)

    mow = dao.get("M001")

    assert mow.model.maker == "Bachmann"
    # assert mow.model.scale == "HO"
    assert mow.model.product == "MOW Equipment"


def test_save_rejects_wrong_entity_type(tmp_path: Path) -> None:
    """MowDAO rejects an MOW with a non-MOW identity."""

    dao = MowDAO(create_config(tmp_path))
    mow = create_mow()

    mow.identity = Identity(
        id="M001",
        entity_type=EntityType.CAR,
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number="1001",
    )

    with pytest.raises(ValueError):
        dao.save(mow)


def test_get_missing_mow_raises(tmp_path: Path) -> None:
    """Getting a missing MOW raises FileNotFoundError."""

    dao = MowDAO(create_config(tmp_path))

    with pytest.raises(FileNotFoundError):
        dao.get("M001")
