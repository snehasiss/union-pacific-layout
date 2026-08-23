#!/usr/bin/env python3
# test_loco.py

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from railroad.config import Config
from railroad.dao.loco import LocoDAO
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.loco import Loco, LocoType


def create_config(tmp_path: Path) -> Config:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "railroad-conf.json"
    config_file.write_text(json.dumps({"application": {"name": "union-pacific-layout"}, "paths": {"config": "config", "data": "data", "resources": "resources", "logs": "logs"}, "data": {"loco": {"path": "loco", "prefix": "L"}, "car": {"path": "car", "prefix": "C"}, "mow": {"path": "mow", "prefix": "M"}}, "resources": {"drawings": "resources/drawings", "media": "resources/media"}}), encoding="utf-8")
    return Config(config_file)


def create_loco(loco_id: str = "L001", status: Status = Status.STORED, acquired: date | None = date(2026, 1, 1)) -> Loco:
    return Loco(
        identity=Identity(id=loco_id, entity_type=EntityType.LOCO, railroad="Union Pacific", reporting_mark="UP", road_number="4014"),
        loco_type=LocoType.STEAM,
        prototype=Prototype(builder="ALCo", model="4-8-8-4", nickname="Big Boy", purpose=Purpose.FREIGHT),
        model=Model(maker="Athearn", product="Genesis Big Boy", scale="HO", status=status, source="Model Train Stuff", price=599.99, acquired=acquired),
        control=Control(type=ControlType.DCC, light=True, sound=True, smoke=False, decoder="Paragon4", address=4014),
    )


def test_save_and_get(tmp_path: Path):
    dao = LocoDAO(create_config(tmp_path))
    dao.save(create_loco())
    result = dao.get("L001")
    assert result.id == "L001"
    assert result.model.scale == "HO"
    assert result.model.status == Status.STORED
    assert result.model.source == "Model Train Stuff"
    assert result.model.price == 599.99
    assert result.model.acquired == date(2026, 1, 1)


def test_save_json_uses_consolidated_model(tmp_path: Path):
    dao = LocoDAO(create_config(tmp_path))
    dao.save(create_loco())
    payload = json.loads((tmp_path / "data" / "loco" / "L001.json").read_text(encoding="utf-8"))
    assert payload["model"] == {"maker": "Athearn", "product": "Genesis Big Boy", "scale": "HO", "status": "stored", "source": "Model Train Stuff", "price": 599.99, "acquired": "2026-01-01", "note": None}
    assert "asset" not in payload


def test_legacy_owned_status_is_read_as_stored(tmp_path: Path):
    dao = LocoDAO(create_config(tmp_path))
    dao.save(create_loco())
    path = tmp_path / "data" / "loco" / "L001.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["model"]["status"] = "owned"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert dao.get("L001").model.status == Status.STORED


def test_intent_without_acquisition_date(tmp_path: Path):
    dao = LocoDAO(create_config(tmp_path))
    dao.save(create_loco(status=Status.INTENT, acquired=None))
    result = dao.get("L001")
    assert result.model.status == Status.INTENT
    assert result.model.acquired is None


def test_exists_and_list(tmp_path: Path):
    dao = LocoDAO(create_config(tmp_path))
    assert dao.exists("L001") is False
    dao.save(create_loco("L001"))
    dao.save(create_loco("L002"))
    assert dao.exists("L001") is True
    assert [loco.id for loco in dao.list()] == ["L001", "L002"]


def test_next_id(tmp_path: Path):
    dao = LocoDAO(create_config(tmp_path))
    assert dao.next_id() == "L001"
    dao.save(create_loco("L001"))
    assert dao.next_id() == "L002"


def test_missing_loco(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        LocoDAO(create_config(tmp_path)).get("L001")
