#!/usr/bin/env python3
# railroad/tests/dao/test_mow.py

"""Tests for MowDAO."""

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
from railroad.rs.mow import MOW, MOWType


def create_config(tmp_path: Path) -> Config:
    config_dir = tmp_path / "config"; config_dir.mkdir(); config_file = config_dir / "railroad-conf.json"
    config_file.write_text(json.dumps({"application": {"name": "test-railroad"}, "paths": {"config": "config", "data": "data", "resources": "resources", "logs": "logs"}, "data": {"mow": {"path": "mow", "prefix": "M"}}, "resources": {"drawings": "resources/drawings", "media": "resources/media"}}), encoding="utf-8")
    return Config(config_file)


def create_mow(mow_id: str = "M001", status: AssetStatus = AssetStatus.OWNED, acquired: date | None = date(2026, 1, 1)) -> MOW:
    return MOW(identity=Identity(id=mow_id, entity_type=EntityType.MOW, railroad="Union Pacific", reporting_mark="UP", road_number="1001"), prototype=Prototype(builder="Jordan Spreader", model="MOW Spreader", nickname=None, purpose=Purpose.FREIGHT), model=Model(maker="Athearn", product="MOW Spreader", status=ModelStatus.ACTIVE), control=Control(type=ControlType.DC, light=True, sound=False, smoke=False, decoder=None, address=0), asset=Asset(status=status, source="Model Train Stuff", price=79.99, acquired=acquired), mow_type=MOWType.CLEANER, self_propelled=False)


def test_save_creates_json_file(tmp_path: Path) -> None:
    dao = MowDAO(create_config(tmp_path)); dao.save(create_mow()); assert (tmp_path / "data" / "mow" / "M001.json").is_file()


def test_save_writes_expected_json(tmp_path: Path) -> None:
    dao = MowDAO(create_config(tmp_path)); dao.save(create_mow()); payload = json.loads((tmp_path / "data" / "mow" / "M001.json").read_text(encoding="utf-8"))
    assert payload["identity"] == {"id": "M001", "entity_type": "mow", "railroad": "Union Pacific", "reporting_mark": "UP", "road_number": "1001"}
    assert payload["mow_type"] == "cleaner" and payload["self_propelled"] is False
    assert payload["prototype"] == {"builder": "Jordan Spreader", "model": "MOW Spreader", "nickname": None, "purpose": "freight"}
    assert payload["model"] == {"maker": "Athearn", "product": "MOW Spreader", "status": "active"}
    assert payload["control"] == {"type": "dc", "decoder": None, "address": 0, "sound": False, "light": True, "smoke": False}
    assert payload["asset"] == {"status": "owned", "source": "Model Train Stuff", "price": 79.99, "acquired": "2026-01-01"}
    assert "electronics" not in payload and "ownership" not in payload


def test_get_reconstructs_mow(tmp_path: Path) -> None:
    dao = MowDAO(create_config(tmp_path)); dao.save(create_mow()); mow = dao.get("M001")
    assert mow.id == "M001" and mow.entity_type == EntityType.MOW and mow.railroad == "Union Pacific" and mow.reporting_mark == "UP" and mow.road_number == "1001"
    assert mow.mow_type == MOWType.CLEANER and mow.self_propelled is False
    assert mow.prototype.builder == "Jordan Spreader" and mow.prototype.model == "MOW Spreader" and mow.prototype.nickname is None and mow.prototype.purpose == Purpose.FREIGHT
    assert mow.model.maker == "Athearn" and mow.model.product == "MOW Spreader" and mow.model.status == ModelStatus.ACTIVE
    assert mow.control.type == ControlType.DC and mow.control.decoder is None and mow.control.address == 0 and mow.control.light is True and mow.control.sound is False and mow.control.smoke is False
    assert mow.asset.status == AssetStatus.OWNED and mow.asset.source == "Model Train Stuff" and mow.asset.price == 79.99 and mow.asset.acquired == date(2026, 1, 1)


def test_get_mow_without_acquisition_date(tmp_path: Path) -> None:
    dao = MowDAO(create_config(tmp_path)); dao.save(create_mow(status=AssetStatus.INTENT, acquired=None)); mow = dao.get("M001")
    assert mow.asset.status == AssetStatus.INTENT and mow.asset.acquired is None


def test_exists(tmp_path: Path) -> None:
    dao = MowDAO(create_config(tmp_path)); assert dao.exists("M001") is False; dao.save(create_mow()); assert dao.exists("M001") is True


def test_list_returns_all_mow(tmp_path: Path) -> None:
    dao = MowDAO(create_config(tmp_path)); [dao.save(create_mow(f"M{i:03d}")) for i in range(1, 4)]; mow_assets = dao.list(); assert len(mow_assets) == 3 and [mow.id for mow in mow_assets] == ["M001", "M002", "M003"]


def test_next_id(tmp_path: Path) -> None:
    dao = MowDAO(create_config(tmp_path)); assert dao.next_id() == "M001"; dao.save(create_mow("M001")); assert dao.next_id() == "M002"; dao.save(create_mow("M002")); assert dao.next_id() == "M003"


def test_save_replaces_existing_mow(tmp_path: Path) -> None:
    dao = MowDAO(create_config(tmp_path)); dao.save(create_mow()); replacement = create_mow(); replacement.model = Model(maker="Bachmann", product="MOW Equipment"); dao.save(replacement); mow = dao.get("M001")
    assert mow.model.maker == "Bachmann" and mow.model.product == "MOW Equipment"


def test_save_rejects_wrong_entity_type(tmp_path: Path) -> None:
    dao = MowDAO(create_config(tmp_path)); mow = create_mow(); mow.identity = Identity(id="M001", entity_type=EntityType.CAR, railroad="Union Pacific", reporting_mark="UP", road_number="1001")
    with pytest.raises(ValueError): dao.save(mow)


def test_get_missing_mow_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError): MowDAO(create_config(tmp_path)).get("M001")
