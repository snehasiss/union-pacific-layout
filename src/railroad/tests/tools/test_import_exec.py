#!/usr/bin/env python3
# railroad/tests/tools/test_import_exec.py
#

from __future__ import annotations

import json
from pathlib import Path

import pytest

from railroad.config import Config
from railroad.domain.identity import IdGenerator
from railroad.tools.import_exec import import_locos


@pytest.fixture(autouse=True)
def reset_id_generator():
    IdGenerator.reset()


def create_config(tmp_path: Path) -> Config:
    """Create a test configuration."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "railroad-conf.json"
    config_file.write_text(
        json.dumps({
            "application": {"name": "test"},
            "paths": {"config": "config", "data": "data", "resources": "resources", "logs": "logs"},
            "data": {"loco": {"path": "loco", "prefix": "L"}},
            "resources": {"drawings": "resources/drawings", "media": "resources/media"},
        }),
        encoding="utf-8",
    )
    return Config(config_file)


def test_import_locos_discovers_csv_files(tmp_path):
    """All CSV files in the import directory are processed."""
    config = create_config(tmp_path)
    import_directory = tmp_path / "imports"
    import_directory.mkdir()
    header = "purpose,locotype,builder,loco_model,nickname,railroad,reporting_mark,road_number,make,dcc,sound,light,smoke,decoder,address,status,store,price,dated\n"
    (import_directory / "steam.csv").write_text(header + "freight,steam,ALCo,4-8-8-4,Big Boy,Union Pacific,UP,4014,Athearn,yes,yes,yes,no,tsunami,3,owned,Model Train Stuff,655,2020-11-20\n", encoding="utf-8")
    (import_directory / "diesel.csv").write_text(header + "switcher,diesel,Plymouth,35T switcher,,Union Pacific,UP,6560,Broadway Limited,yes,no,yes,no,dcc,3,owned,FactoryDirect,100,2021-06-19\n", encoding="utf-8")
    count = import_locos(config=config, import_directory=import_directory)
    assert count == 2
    data_directory = config.data / "loco"
    assert (data_directory / "L001.json").exists()
    assert (data_directory / "L002.json").exists()


def test_import_locos_writes_expected_json(tmp_path):
    """Imported locomotives are persisted through LocoDAO."""
    config = create_config(tmp_path)
    import_directory = tmp_path / "imports"
    import_directory.mkdir()
    (import_directory / "steam.csv").write_text(
        "purpose,locotype,builder,loco_model,nickname,railroad,reporting_mark,road_number,make,dcc,sound,light,smoke,decoder,address,status,store,price,dated,scale,product,note\nfreight,steam,ALCo,4-8-8-4,Big Boy,Union Pacific,up,4014,Athearn,yes,yes,yes,no,tsunami,3,spotted,Model Train Stuff,655,2020-11-20,OO,Genesis Big Boy,Sound tested\n",
        encoding="utf-8",
    )
    count = import_locos(config=config, import_directory=import_directory)
    assert count == 1
    payload = json.loads((config.data / "loco" / "L001.json").read_text(encoding="utf-8"))
    assert payload["identity"]["id"] == "L001"
    assert payload["identity"]["reporting_mark"] == "UP"
    assert payload["identity"]["road_number"] == "4014"
    assert payload["loco_type"] == "steam"
    assert payload["model"] == {
        "maker": "Athearn",
        "product": "Genesis Big Boy",
        "scale": "OO",
        "status": "spotted",
        "source": "Model Train Stuff",
        "price": 655.0,
        "acquired": "2020-11-20",
        "note": "Sound tested",
    }
    assert payload["control"]["type"] == "dcc"
    assert payload["control"]["address"] == 3
    assert "asset" not in payload
