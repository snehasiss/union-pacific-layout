#!/usr/bin/env python3
#
# railroad/tests/dao/test_mow.py
#

from __future__ import annotations

import json
from datetime import date

import pytest

from railroad.config import Config
from railroad.dao.mow import MowDAO
from railroad.domain.electronics import Electronics
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.ownership import Ownership, OwnershipStatus
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.mow import MOW
from railroad.rs.mow_type import MOWType


def make_mow(
    entity_id: str = "M001",
    acquired: date | None = date(2026, 1, 1),
) -> MOW:
    identity = Identity.from_existing(
        id=entity_id,
        entity_type=EntityType.MOW,
        railroad="union pacific",
        reporting_mark="UP",
        road_number=1,
    )

    prototype = Prototype(
        builder="Plasser & Theurer",
        model="09-3X",
        nickname=None,
        purpose=Purpose.MACHINE,
    )

    model = Model(
        manufacturer="Example",
        product="Example",
    )

    electronics = Electronics(
        dcc=False,
        decoder=None,
        address=None,
        sound=False,
        light=True,
        smoke=False,
    )

    ownership = Ownership(
        status=OwnershipStatus.OWNED,
        source="model train stuff",
        price=100.0,
        acquired=acquired,
    )

    return MOW(
        identity=identity,
        prototype=prototype,
        model=model,
        electronics=electronics,
        ownership=ownership,
        mow_type=MOWType.TAMPER,
        self_propelled=True,
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
                    "mow": {
                        "path": "mow",
                        "prefix": "M",
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
    return MowDAO(config)


def test_save_creates_json_file(dao, config):
    mow = make_mow()

    dao.save(mow)

    path = config.data / "mow" / "M001.json"

    assert path.exists()


def test_save_writes_expected_json(dao, config):
    mow = make_mow()

    dao.save(mow)

    path = config.data / "mow" / "M001.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["identity"]["id"] == "M001"
    assert payload["identity"]["entity_type"] == "mow"
    assert payload["identity"]["railroad"] == "union pacific"
    assert payload["identity"]["reporting_mark"] == "UP"
    assert payload["identity"]["road_number"] == 1

    assert payload["mow_type"] == "tamper"
    assert payload["self_propelled"] is True

    assert payload["prototype"]["builder"] == "Plasser & Theurer"
    assert payload["prototype"]["model"] == "09-3X"
    assert payload["prototype"]["nickname"] is None
    assert payload["prototype"]["purpose"] == "machine"

    assert payload["model"]["manufacturer"] == "Example"
    assert payload["model"]["product"] == "Example"

    assert payload["electronics"]["dcc"] is False
    assert payload["electronics"]["decoder"] is None
    assert payload["electronics"]["address"] is None
    assert payload["electronics"]["sound"] is False
    assert payload["electronics"]["light"] is True
    assert payload["electronics"]["smoke"] is False

    assert payload["ownership"]["status"] == "owned"
    assert payload["ownership"]["source"] == "model train stuff"
    assert payload["ownership"]["price"] == 100.0
    assert payload["ownership"]["acquired"] == "2026-01-01"


def test_get_reconstructs_mow(dao):
    original = make_mow()

    dao.save(original)

    restored = dao.get("M001")

    assert restored.id == original.id
    assert restored.entity_type == EntityType.MOW
    assert restored.mow_type == MOWType.TAMPER
    assert restored.self_propelled is True
    assert restored.prototype.purpose == Purpose.MACHINE

    assert restored.electronics.dcc is False
    assert restored.electronics.light is True
    assert restored.electronics.smoke is False

    assert restored.ownership.status == OwnershipStatus.OWNED
    assert restored.ownership.acquired == date(2026, 1, 1)


def test_get_mow_without_acquisition_date(dao):
    mow = make_mow(acquired=None)

    dao.save(mow)

    restored = dao.get("M001")

    assert restored.ownership.status == OwnershipStatus.OWNED
    assert restored.ownership.acquired is None


def test_exists(dao):
    mow = make_mow()

    assert dao.exists("M001") is False

    dao.save(mow)

    assert dao.exists("M001") is True


def test_get_missing_mow_raises(dao):
    with pytest.raises(FileNotFoundError):
        dao.get("M001")


def test_list_returns_all_mow(dao):
    dao.save(make_mow("M001"))
    dao.save(make_mow("M002"))

    mow_assets = dao.list()

    assert [mow.id for mow in mow_assets] == ["M001", "M002"]


def test_next_id_empty_directory(dao):
    assert dao.next_id() == "M001"


def test_next_id_follows_existing_files(dao):
    dao.save(make_mow("M001"))
    dao.save(make_mow("M003"))

    assert dao.next_id() == "M004"


def test_save_replaces_existing_mow(dao):
    mow = make_mow()
    dao.save(mow)

    replacement = MOW(
        identity=mow.identity,
        prototype=Prototype(
            builder="Plasser & Theurer",
            model="09-3X",
            nickname="replacement",
            purpose=Purpose.MACHINE,
        ),
        model=mow.model,
        electronics=mow.electronics,
        ownership=mow.ownership,
        mow_type=mow.mow_type,
        self_propelled=mow.self_propelled,
    )

    dao.save(replacement)

    restored = dao.get("M001")

    assert restored.nickname == "replacement"


def test_save_rejects_non_mow(dao):
    with pytest.raises(TypeError):
        dao.save("not an MOW")


def test_save_rejects_wrong_entity_type(dao):
    identity = Identity.from_existing(
        id="M001",
        entity_type=EntityType.LOCO,
        railroad="union pacific",
        reporting_mark="UP",
        road_number=1,
    )

    mow = MOW(
        identity=identity,
        prototype=Prototype(
            builder="Plasser & Theurer",
            model="09-3X",
            nickname=None,
            purpose=Purpose.MACHINE,
        ),
        model=Model(
            manufacturer="Example",
            product="Example",
        ),
        electronics=Electronics(
            dcc=False,
            decoder=None,
            address=None,
            sound=False,
            light=True,
            smoke=False,
        ),
        ownership=Ownership(
            status=OwnershipStatus.OWNED,
            source="model train stuff",
            price=100.0,
            acquired=date(2026, 1, 1),
        ),
        mow_type=MOWType.TAMPER,
        self_propelled=True,
    )

    with pytest.raises(ValueError):
        dao.save(mow)
