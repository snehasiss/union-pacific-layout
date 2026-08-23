#!/usr/bin/env python3
# test_mow.py

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from railroad.config import Config
from railroad.dao.mow import MowDAO
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.mow import MOW, MOWType


def create_config(tmp_path: Path) -> Config:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "railroad-conf.json"
    config_file.write_text(json.dumps({"application": {"name": "test-railroad"}, "paths": {"config": "config", "data": "data", "resources": "resources", "logs": "logs"}, "data": {"mow": {"path": "mow", "prefix": "M"}}, "resources": {"drawings": "resources/drawings", "media": "resources/media"}}), encoding="utf-8")
    return Config(config_file)


def create_mow(mow_id: str = "M001", status: Status = Status.STORED, acquired: date | None = date(2026, 1, 1)) -> MOW:
    return MOW(identity=Identity(id=mow_id, entity_type=EntityType.MOW, railroad="Union Pacific", reporting_mark="UP", road_number="1001"), prototype=Prototype(builder="Jordan Spreader", model="MOW Spreader", nickname=None, purpose=Purpose.FREIGHT), model=Model(maker="Athearn", product="MOW Spreader", scale="HO", status=status, source="Model Train Stuff", price=79.99, acquired=acquired), control=Control(type=ControlType.DC, light=True, sound=False, smoke=False, decoder=None, address=0), mow_type=MOWType.CLEANER, self_propelled=False)


def test_save_and_get(tmp_path: Path):
    dao = MowDAO(create_config(tmp_path)); dao.save(create_mow()); mow = dao.get("M001")
    assert mow.id == "M001"
    assert mow.model.scale == "HO"
    assert mow.model.status == Status.STORED
    assert mow.model.source == "Model Train Stuff"
    assert mow.model.acquired == date(2026, 1, 1)


def test_save_writes_consolidated_model(tmp_path: Path):
    dao = MowDAO(create_config(tmp_path)); dao.save(create_mow())
    payload = json.loads((tmp_path / "data" / "mow" / "M001.json").read_text(encoding="utf-8"))
    assert payload["model"]["status"] == "stored"
    assert payload["model"]["scale"] == "HO"
    assert payload["model"]["source"] == "Model Train Stuff"
    assert "asset" not in payload


def test_exists_list_and_next_id(tmp_path: Path):
    dao = MowDAO(create_config(tmp_path))
    assert dao.exists("M001") is False
    assert dao.next_id() == "M001"
    dao.save(create_mow("M001")); dao.save(create_mow("M002"))
    assert dao.exists("M001") is True
    assert dao.next_id() == "M003"
    assert [mow.id for mow in dao.list()] == ["M001", "M002"]


def test_get_missing_mow_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        MowDAO(create_config(tmp_path)).get("M001")
