#!/usr/bin/env python3
#
# railroad/tests/dao/test_car.py
#

from __future__ import annotations

import json
from datetime import date

import pytest

from railroad.config import Config
from railroad.dao.car import CarDAO
from railroad.domain.electronics import Electronics
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.ownership import Ownership, OwnershipStatus
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.car import Car
from railroad.rs.car_type import CarType


def make_car(
    entity_id: str = "C001",
    acquired: date | None = date(2026, 1, 1),
) -> Car:
    identity = Identity.from_existing(
        id=entity_id,
        entity_type=EntityType.CAR,
        railroad="union pacific",
        reporting_mark="UP",
        road_number="12345",
    )

    prototype = Prototype(
        builder="ACF",
        model="70-ton covered hopper",
        nickname=None,
        purpose=Purpose.FREIGHT,
    )

    model = Model(
        manufacturer="Athearn",
        product="Genesis",
    )

    electronics = Electronics(
        dcc=False,
        decoder=None,
        address=None,
        sound=False,
        light=False,
        smoke=False,
    )

    ownership = Ownership(
        status=OwnershipStatus.OWNED,
        source="model train stuff",
        price=45.0,
        acquired=acquired,
    )

    return Car(
        identity=identity,
        prototype=prototype,
        model=model,
        electronics=electronics,
        ownership=ownership,
        car_type=CarType.HOPPER,
    )


@pytest.fixture
def config(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    config_file = config_dir / "railroad-conf.json"

    config_file.write_text(
        json.dumps(
            {
                "application": {
                    "name": "test"
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
                    }
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
def dao(config):
    return CarDAO(config)


def test_save_creates_json_file(dao, config):
    car = make_car()

    dao.save(car)

    path = config.data / "car" / "C001.json"

    assert path.exists()


def test_save_writes_expected_json(dao, config):
    car = make_car()

    dao.save(car)

    path = config.data / "car" / "C001.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["identity"]["id"] == "C001"
    assert payload["identity"]["entity_type"] == "car"
    assert payload["identity"]["railroad"] == "union pacific"
    assert payload["identity"]["reporting_mark"] == "UP"
    assert payload["identity"]["road_number"] == "12345"

    assert payload["car_type"] == "hopper"

    assert payload["prototype"]["builder"] == "ACF"
    assert payload["prototype"]["model"] == "70-ton covered hopper"
    assert payload["prototype"]["nickname"] is None
    assert payload["prototype"]["purpose"] == "freight"

    assert payload["model"]["manufacturer"] == "Athearn"
    assert payload["model"]["product"] == "Genesis"

    assert payload["electronics"]["dcc"] is False
    assert payload["electronics"]["decoder"] is None
    assert payload["electronics"]["address"] is None
    assert payload["electronics"]["sound"] is False
    assert payload["electronics"]["light"] is False
    assert payload["electronics"]["smoke"] is False

    assert payload["ownership"]["status"] == "owned"
    assert payload["ownership"]["source"] == "model train stuff"
    assert payload["ownership"]["price"] == 45.0
    assert payload["ownership"]["acquired"] == "2026-01-01"


def test_get_reconstructs_car(dao):
    original = make_car()

    dao.save(original)

    restored = dao.get("C001")

    assert restored.id == original.id
    assert restored.entity_type == EntityType.CAR
    assert restored.car_type == CarType.HOPPER
    assert restored.prototype.purpose == Purpose.FREIGHT

    assert restored.electronics.dcc is False
    assert restored.electronics.smoke is False

    assert restored.ownership.status == OwnershipStatus.OWNED
    assert restored.ownership.acquired == date(2026, 1, 1)


def test_get_car_without_acquisition_date(dao):
    car = make_car(acquired=None)

    dao.save(car)

    restored = dao.get("C001")

    assert restored.ownership.status == OwnershipStatus.OWNED
    assert restored.ownership.acquired is None


def test_exists(dao):
    car = make_car()

    assert dao.exists("C001") is False

    dao.save(car)

    assert dao.exists("C001") is True


def test_get_missing_car_raises(dao):
    with pytest.raises(FileNotFoundError):
        dao.get("C001")


def test_list_returns_all_cars(dao):
    dao.save(make_car("C001"))
    dao.save(make_car("C002"))

    cars = dao.list()

    assert [car.id for car in cars] == ["C001", "C002"]


def test_next_id_empty_directory(dao):
    assert dao.next_id() == "C001"


def test_next_id_follows_existing_files(dao):
    dao.save(make_car("C001"))
    dao.save(make_car("C003"))

    assert dao.next_id() == "C004"


def test_save_replaces_existing_car(dao):
    car = make_car()
    dao.save(car)

    replacement = Car(
        identity=car.identity,
        prototype=Prototype(
            builder="ACF",
            model="70-ton covered hopper",
            nickname="replacement",
            purpose=Purpose.FREIGHT,
        ),
        model=car.model,
        electronics=car.electronics,
        ownership=car.ownership,
        car_type=car.car_type,
    )

    dao.save(replacement)

    restored = dao.get("C001")

    assert restored.nickname == "replacement"


def test_save_rejects_non_car(dao):
    with pytest.raises(TypeError):
        dao.save("not a car")


def test_save_rejects_wrong_entity_type(dao):
    identity = Identity.from_existing(
        id="C001",
        entity_type=EntityType.LOCO,
        railroad="union pacific",
        reporting_mark="UP",
        road_number="12345",
    )

    car = Car(
        identity=identity,
        prototype=Prototype(
            builder="ACF",
            model="70-ton covered hopper",
            nickname=None,
            purpose=Purpose.FREIGHT,
        ),
        model=Model(
            manufacturer="Athearn",
            product="Genesis",
        ),
        electronics=Electronics(
            dcc=False,
            decoder=None,
            address=None,
            sound=False,
            light=False,
            smoke=False,
        ),
        ownership=Ownership(
            status=OwnershipStatus.OWNED,
            source="model train stuff",
            price=45.0,
            acquired=date(2026, 1, 1),
        ),
        car_type=CarType.HOPPER,
    )

    with pytest.raises(ValueError):
        dao.save(car)

