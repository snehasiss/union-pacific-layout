#!/usr/bin/env python3
# test_loco.py
#

from __future__ import annotations

"""
Tests for LocoDAO.
"""

import json
from datetime import date
from pathlib import Path

import pytest

from railroad.config import Config
from railroad.dao.loco import LocoDAO
from railroad.domain.asset import Asset, AssetStatus
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.loco import Loco
from railroad.rs.loco_type import LocoType


def create_config(tmp_path: Path) -> Config:
    """Create an isolated test configuration."""

    config_dir = tmp_path / "config"
    config_dir.mkdir()

    config_file = config_dir / "railroad-conf.json"

    config_file.write_text(
        json.dumps(
            {
                "application": {
                    "name": "union-pacific-layout"
                },
                "paths": {
                    "config": "config",
                    "data": "data",
                    "resources": "resources",
                    "logs": "logs",
                },
                "data": {
                    "loco": {
                        "path": "loco",
                        "prefix": "L",
                    },
                    "car": {
                        "path": "car",
                        "prefix": "C",
                    },
                    "mow": {
                        "path": "mow",
                        "prefix": "M",
                    },
                    "signal": {
                        "path": "signal",
                        "prefix": "G",
                    },
                    "turnout": {
                        "path": "turnout",
                        "prefix": "T",
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


@pytest.fixture
def dao(tmp_path: Path) -> LocoDAO:
    """Return a LocoDAO using an isolated test configuration."""

    return LocoDAO(create_config(tmp_path))


def create_loco(
    loco_id: str = "L001",
    status: AssetStatus = AssetStatus.OWNED,
    acquired: date | None = date(2026, 1, 1),
) -> Loco:
    """Create a test locomotive."""

    identity = Identity(
        id=loco_id,
        entity_type=EntityType.LOCO,
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number="4014",
    )

    prototype = Prototype(
        builder="ALCo",
        model="4-8-8-4",
        nickname="Big Boy",
        purpose=Purpose.FREIGHT,
    )

    model = Model(
        maker="Athearn",
        # SCALE="HO",
        product="Genesis Big Boy",
    )

    control = Control(
        type=ControlType.DCC,
        light=True,
        sound=True,
        smoke=False,
        decoder="Paragon4",
        address=4014,
    )

    asset = Asset(
        status=status,
        source="Model Train Stuff",
        price=599.99,
        acquired=acquired,
    )

    return Loco(
        identity=identity,
        loco_type=LocoType.STEAM,
        prototype=prototype,
        model=model,
        control=control,
        asset=asset,
    )


def test_save_and_get(dao: LocoDAO) -> None:
    """A locomotive can be saved and retrieved."""

    loco = create_loco()

    dao.save(loco)
    result = dao.get("L001")

    assert result.id == "L001"
    assert result.entity_type == EntityType.LOCO
    assert result.loco_type == LocoType.STEAM

    assert result.railroad == "Union Pacific"
    assert result.reporting_mark == "UP"
    assert result.road_number == "4014"

    assert result.prototype.builder == "ALCo"
    assert result.prototype.model == "4-8-8-4"
    assert result.prototype.nickname == "Big Boy"
    assert result.prototype.purpose == Purpose.FREIGHT

    assert result.model.maker == "Athearn"
    #assert result.model.SCALE == "HO"
    assert result.model.product == "Genesis Big Boy"

    assert result.control.type == ControlType.DCC
    assert result.control.light is True
    assert result.control.sound is True
    assert result.control.smoke is False
    assert result.control.decoder == "Paragon4"
    assert result.control.address == 4014

    assert result.asset.status == AssetStatus.OWNED
    assert result.asset.source == "Model Train Stuff"
    assert result.asset.price == 599.99
    assert result.asset.acquired == date(2026, 1, 1)


def test_save_creates_json(dao: LocoDAO, tmp_path: Path) -> None:
    """Saving a locomotive creates its JSON persistence file."""

    dao.save(create_loco())

    path = tmp_path / "data" / "loco" / "L001.json"

    assert path.exists()


def test_json_uses_control_and_asset(
    dao: LocoDAO,
    tmp_path: Path,
) -> None:
    """Persisted JSON uses the current domain names."""

    dao.save(create_loco())

    path = tmp_path / "data" / "loco" / "L001.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert "control" in payload
    assert "asset" in payload

    assert "electronics" not in payload
    assert "ownership" not in payload


def test_json_control(dao: LocoDAO, tmp_path: Path) -> None:
    """Control data is persisted correctly."""

    dao.save(create_loco())

    path = tmp_path / "data" / "loco" / "L001.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["control"] == {
        "type": "dcc",
        "light": True,
        "sound": True,
        "smoke": False,
        "decoder": "Paragon4",
        "address": 4014,
    }


def test_json_asset(dao: LocoDAO, tmp_path: Path) -> None:
    """Asset data is persisted correctly."""

    dao.save(create_loco())

    path = tmp_path / "data" / "loco" / "L001.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["asset"] == {
        "status": "owned",
        "source": "Model Train Stuff",
        "price": 599.99,
        "acquired": "2026-01-01",
    }


def test_intent_without_acquisition_date(dao: LocoDAO) -> None:
    """An intended locomotive may have no acquisition date."""

    loco = create_loco(
        status=AssetStatus.INTENT,
        acquired=None,
    )

    dao.save(loco)

    result = dao.get("L001")

    assert result.asset.status == AssetStatus.INTENT
    assert result.asset.acquired is None


def test_dc_loco_round_trip(dao: LocoDAO) -> None:
    """A DC locomotive round-trips without decoder or address."""

    loco = create_loco()

    loco.control = Control(
        type=ControlType.DC,
        light=True,
        sound=False,
        smoke=False,
        decoder=None,
        address=0,
    )

    dao.save(loco)

    result = dao.get("L001")

    assert result.control.type == ControlType.DC
    assert result.control.light is True
    assert result.control.sound is False
    assert result.control.smoke is False
    assert result.control.decoder is None
    assert result.control.address == 0


def test_exists(dao: LocoDAO) -> None:
    """DAO reports whether a locomotive exists."""

    assert dao.exists("L001") is False

    dao.save(create_loco())

    assert dao.exists("L001") is True


def test_missing_loco(dao: LocoDAO) -> None:
    """Getting a missing locomotive raises FileNotFoundError."""

    with pytest.raises(FileNotFoundError):
        dao.get("L001")


def test_next_id(dao: LocoDAO) -> None:
    """DAO generates the next available locomotive ID."""

    assert dao.next_id() == "L001"

    dao.save(create_loco("L001"))
    assert dao.next_id() == "L002"

    dao.save(create_loco("L002"))
    assert dao.next_id() == "L003"


def test_list(dao: LocoDAO) -> None:
    """DAO lists all persisted locomotives."""

    dao.save(create_loco("L001"))
    dao.save(create_loco("L002"))
    dao.save(create_loco("L003"))

    locos = dao.list()

    assert len(locos) == 3
    assert [loco.id for loco in locos] == [
        "L001",
        "L002",
        "L003",
    ]
