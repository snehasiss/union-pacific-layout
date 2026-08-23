#!/usr/bin/env python3
# test_car.py

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from railroad.config import Config
from railroad.dao.car import CarDAO
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.car import Car, CarType


def create_config(tmp_path: Path) -> Config:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "railroad-conf.json"
    config_file.write_text(json.dumps({"application": {"name": "test-railroad"}, "paths": {"config": "config", "data": "data", "resources": "resources", "logs": "logs"}, "data": {"car": {"path": "car", "prefix": "C"}}, "resources": {"drawings": "resources/drawings", "media": "resources/media"}}), encoding="utf-8")
    return Config(config_file)


def create_car(car_id: str = "C001", status: Status = Status.STORED, acquired: date | None = date(2026, 1, 1)) -> Car:
    return Car(identity=Identity(id=car_id, entity_type=EntityType.CAR, railroad="Union Pacific", reporting_mark="UP", road_number="12345"), prototype=Prototype(builder="ACF", model="2-Bay Hopper", nickname=None, purpose=Purpose.FREIGHT), model=Model(maker="Athearn", product="Genesis Hopper", scale="HO", status=status, source="Model Train Stuff", price=49.99, acquired=acquired), control=Control(type=ControlType.DCC, light=True, sound=False, smoke=False, decoder="LokSound", address=12345), car_type=CarType.HOPPER)


def test_save_and_get(tmp_path: Path):
    dao = CarDAO(create_config(tmp_path)); dao.save(create_car()); car = dao.get("C001")
    assert car.id == "C001"
    assert car.model.scale == "HO"
    assert car.model.status == Status.STORED
    assert car.model.source == "Model Train Stuff"
    assert car.model.acquired == date(2026, 1, 1)


def test_save_writes_consolidated_model(tmp_path: Path):
    dao = CarDAO(create_config(tmp_path)); dao.save(create_car())
    payload = json.loads((tmp_path / "data" / "car" / "C001.json").read_text(encoding="utf-8"))
    assert payload["model"]["status"] == "stored"
    assert payload["model"]["scale"] == "HO"
    assert payload["model"]["source"] == "Model Train Stuff"
    assert "asset" not in payload


def test_exists_list_and_next_id(tmp_path: Path):
    dao = CarDAO(create_config(tmp_path))
    assert dao.exists("C001") is False
    assert dao.next_id() == "C001"
    dao.save(create_car("C001")); dao.save(create_car("C002"))
    assert dao.exists("C001") is True
    assert dao.next_id() == "C003"
    assert [car.id for car in dao.list()] == ["C001", "C002"]


def test_get_missing_car_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        CarDAO(create_config(tmp_path)).get("C001")
