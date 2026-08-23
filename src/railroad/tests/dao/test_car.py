#!/usr/bin/env python3
# railroad/tests/dao/test_car.py
#

"""
Tests for CarDAO.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from railroad.config import Config
from railroad.dao.car import CarDAO
from railroad.domain.asset import Asset, AssetStatus
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, ModelStatus
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.car import Car
from railroad.rs.car_type import CarType


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
                    "car": {
                        "path": "car",
                        "prefix": "C",
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


def create_car(
    car_id: str = "C001",
    status: AssetStatus = AssetStatus.OWNED,
    acquired: date | None = date(2026, 1, 1),
) -> Car:
    """Create a representative Car for testing."""

    identity = Identity(
        id=car_id,
        entity_type=EntityType.CAR,
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number="12345",
    )

    prototype = Prototype(
        builder="ACF",
        model="2-Bay Hopper",
        nickname=None,
        purpose=Purpose.FREIGHT,
    )

    model = Model(
        maker="Athearn",
        product="Genesis Hopper",
        status=ModelStatus.ACTIVE,
    )

    control = Control(
        type=ControlType.DCC,
        light=True,
        sound=False,
        smoke=False,
        decoder="LokSound",
        address=12345,
    )

    asset = Asset(
        status=status,
        source="Model Train Stuff",
        price=49.99,
        acquired=acquired,
    )

    return Car(
        identity=identity,
        prototype=prototype,
        model=model,
        control=control,
        asset=asset,
        car_type=CarType.HOPPER,
    )


def test_save_creates_json_file(tmp_path: Path) -> None:
    """Saving a Car creates its JSON file."""

    dao = CarDAO(create_config(tmp_path))

    dao.save(create_car())

    assert (tmp_path / "data" / "car" / "C001.json").is_file()


def test_save_writes_expected_json(tmp_path: Path) -> None:
    """Saving a Car writes the current domain structure."""

    dao = CarDAO(create_config(tmp_path))

    dao.save(create_car())

    path = tmp_path / "data" / "car" / "C001.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["identity"] == {
        "id": "C001",
        "entity_type": "car",
        "railroad": "Union Pacific",
        "reporting_mark": "UP",
        "road_number": "12345",
    }

    assert payload["car_type"] == "hopper"

    assert payload["prototype"] == {
        "builder": "ACF",
        "model": "2-Bay Hopper",
        "nickname": None,
        "purpose": "freight",
    }

    assert payload["model"] == {
        "maker": "Athearn",
        "product": "Genesis Hopper",
        "status": "active",
    }

    assert payload["control"] == {
        "type": "dcc",
        "decoder": "LokSound",
        "address": 12345,
        "sound": False,
        "light": True,
        "smoke": False,
    }

    assert payload["asset"] == {
        "status": "owned",
        "source": "Model Train Stuff",
        "price": 49.99,
        "acquired": "2026-01-01",
    }

    assert "electronics" not in payload
    assert "ownership" not in payload


def test_get_reconstructs_car(tmp_path: Path) -> None:
    """A persisted Car can be reconstructed."""

    dao = CarDAO(create_config(tmp_path))
    original = create_car()

    dao.save(original)

    car = dao.get("C001")

    assert car.id == original.id
    assert car.entity_type == EntityType.CAR
    assert car.railroad == "Union Pacific"
    assert car.reporting_mark == "UP"
    assert car.road_number == "12345"

    assert car.car_type == CarType.HOPPER

    assert car.prototype.builder == "ACF"
    assert car.prototype.model == "2-Bay Hopper"
    assert car.prototype.nickname is None
    assert car.prototype.purpose == Purpose.FREIGHT

    assert car.model.maker == "Athearn"
    assert car.model.product == "Genesis Hopper"
    assert car.model.status == ModelStatus.ACTIVE

    assert car.control.type == ControlType.DCC
    assert car.control.decoder == "LokSound"
    assert car.control.address == 12345
    assert car.control.light is True
    assert car.control.sound is False
    assert car.control.smoke is False

    assert car.asset.status == AssetStatus.OWNED
    assert car.asset.source == "Model Train Stuff"
    assert car.asset.price == 49.99
    assert car.asset.acquired == date(2026, 1, 1)


def test_get_car_without_acquisition_date(tmp_path: Path) -> None:
    """A Car without an acquisition date can be persisted."""

    dao = CarDAO(create_config(tmp_path))

    dao.save(
        create_car(
            status=AssetStatus.INTENT,
            acquired=None,
        )
    )

    car = dao.get("C001")

    assert car.asset.status == AssetStatus.INTENT
    assert car.asset.acquired is None


def test_exists(tmp_path: Path) -> None:
    """exists() correctly identifies persisted Cars."""

    dao = CarDAO(create_config(tmp_path))

    assert dao.exists("C001") is False

    dao.save(create_car())

    assert dao.exists("C001") is True


def test_list_returns_all_cars(tmp_path: Path) -> None:
    """list() returns all persisted Cars."""

    dao = CarDAO(create_config(tmp_path))

    dao.save(create_car("C001"))
    dao.save(create_car("C002"))
    dao.save(create_car("C003"))

    cars = dao.list()

    assert len(cars) == 3
    assert [car.id for car in cars] == [
        "C001",
        "C002",
        "C003",
    ]


def test_next_id(tmp_path: Path) -> None:
    """next_id() returns the next available Car ID."""

    dao = CarDAO(create_config(tmp_path))

    assert dao.next_id() == "C001"

    dao.save(create_car("C001"))
    assert dao.next_id() == "C002"

    dao.save(create_car("C002"))
    assert dao.next_id() == "C003"


def test_save_replaces_existing_car(tmp_path: Path) -> None:
    """Saving the same ID replaces the existing Car."""

    dao = CarDAO(create_config(tmp_path))

    dao.save(create_car())

    replacement = create_car()
    replacement.model = Model(
        maker="Bachmann",
        product="Hopper",
        status=ModelStatus.ACTIVE,
    )

    dao.save(replacement)

    car = dao.get("C001")

    assert car.model.maker == "Bachmann"
    assert car.model.product == "Hopper"
    assert car.model.status == ModelStatus.ACTIVE


def test_save_rejects_wrong_entity_type(tmp_path: Path) -> None:
    """CarDAO rejects a Car with a non-CAR identity."""

    dao = CarDAO(create_config(tmp_path))
    car = create_car()

    car.identity = Identity(
        id="C001",
        entity_type=EntityType.MOW,
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number="12345",
    )

    with pytest.raises(ValueError):
        dao.save(car)


def test_get_missing_car_raises(tmp_path: Path) -> None:
    """Getting a missing Car raises FileNotFoundError."""

    dao = CarDAO(create_config(tmp_path))

    with pytest.raises(FileNotFoundError):
        dao.get("C001")
