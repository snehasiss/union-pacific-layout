#!/usr/bin/env python3

import json
from datetime import date

import pytest

from railroad.config import Config
from railroad.dao.loco import LocoDAO
from railroad.domain.electronics import Electronics
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.ownership import Ownership, OwnershipStatus
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.loco import Loco
from railroad.rs.loco_type import LocoType


def make_loco(entity_id="L001") -> Loco:
    identity = Identity.from_existing(
        id=entity_id,
        entity_type=EntityType.LOCO,
        railroad="union pacific",
        reporting_mark="UP",
        road_number="4014",
    )

    prototype = Prototype(
        builder="ALCo",
        model="4-8-8-4",
        nickname="big boy",
        purpose=Purpose.FREIGHT,
    )

    model = Model(
        manufacturer="Athearn",
        product="Genesis",
    )

    electronics = Electronics(
        dcc=True,
        decoder="tsunami",
        address=3,
        sound=True,
        light=False,
        smoke=False,
    )

    ownership = Ownership(
        status=OwnershipStatus.OWNED,
        source="model train stuff",
        price=655.0,
        acquired=date(2020, 11, 20),
    )

    return Loco(
        identity=identity,
        loco_type=LocoType.STEAM,
        prototype=prototype,
        model=model,
        electronics=electronics,
        ownership=ownership,
    )


@pytest.fixture
def config(tmp_path):
    root = tmp_path
    config_dir = root / "config"
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
                    "loco": {
                        "path": "loco",
                        "prefix": "L",
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
    return LocoDAO(config)


def test_save_creates_json_file(dao, config):
    loco = make_loco()

    dao.save(loco)

    path = config.data / "loco" / "L001.json"

    assert path.exists()


def test_save_writes_expected_json(dao, config):
    loco = make_loco()

    dao.save(loco)

    path = config.data / "loco" / "L001.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["identity"]["id"] == "L001"
    assert payload["identity"]["entity_type"] == "loco"
    assert payload["identity"]["reporting_mark"] == "UP"
    assert payload["identity"]["road_number"] == "4014"

    assert payload["loco_type"] == "steam"

    assert payload["prototype"]["builder"] == "ALCo"
    assert payload["prototype"]["model"] == "4-8-8-4"
    assert payload["prototype"]["nickname"] == "big boy"
    assert payload["prototype"]["purpose"] == "freight"

    assert payload["model"]["manufacturer"] == "Athearn"
    assert payload["model"]["product"] == "Genesis"

    assert payload["electronics"]["dcc"] is True
    assert payload["electronics"]["decoder"] == "tsunami"
    assert payload["electronics"]["address"] == 3
    assert payload["electronics"]["sound"] is True
    assert payload["electronics"]["light"] is False
    assert payload["electronics"]["smoke"] is False

    assert payload["ownership"]["status"] == "owned"
    assert payload["ownership"]["source"] == "model train stuff"
    assert payload["ownership"]["price"] == 655.0
    assert payload["ownership"]["acquired"] == "2020-11-20"


def test_get_reconstructs_loco(dao):
    original = make_loco()

    dao.save(original)
    restored = dao.get("L001")

    assert restored.id == original.id
    assert restored.entity_type == EntityType.LOCO
    assert restored.loco_type == LocoType.STEAM
    assert restored.prototype.purpose == Purpose.FREIGHT
    assert restored.electronics.smoke is False
    assert restored.ownership.acquired == date(2020, 11, 20)


def test_exists(dao):
    loco = make_loco()

    assert dao.exists("L001") is False

    dao.save(loco)

    assert dao.exists("L001") is True


def test_get_missing_loco_raises(dao):
    with pytest.raises(FileNotFoundError):
        dao.get("L001")


def test_list_returns_all_locos(dao):
    dao.save(make_loco("L001"))
    dao.save(make_loco("L002"))

    locos = dao.list()

    assert [loco.id for loco in locos] == ["L001", "L002"]


def test_next_id_empty_directory(dao):
    assert dao.next_id() == "L001"


def test_next_id_follows_existing_files(dao):
    dao.save(make_loco("L001"))
    dao.save(make_loco("L003"))

    assert dao.next_id() == "L004"


def test_save_replaces_existing_loco(dao):
    loco = make_loco()
    dao.save(loco)

    replacement = Loco(
        identity=loco.identity,
        loco_type=loco.loco_type,
        prototype=Prototype(
            builder="ALCo",
            model="4-8-8-4",
            nickname="updated",
            purpose=Purpose.FREIGHT,
        ),
        model=loco.model,
        electronics=loco.electronics,
        ownership=loco.ownership,
    )

    dao.save(replacement)

    restored = dao.get("L001")

    assert restored.nickname == "updated"

def test_get_loco_without_acquisition_date(dao):
    loco = make_loco()

    loco.ownership = Ownership(
        status=OwnershipStatus.INTENT,
        source="model train stuff",
        price=0,
        acquired=None,
    )

    dao.save(loco)

    restored = dao.get("L001")

    assert restored.ownership.status == OwnershipStatus.INTENT
    assert restored.ownership.acquired is None
