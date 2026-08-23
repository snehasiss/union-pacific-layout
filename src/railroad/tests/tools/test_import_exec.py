#!/usr/bin/env python3
# railroad/tests/tools/test_import_exec.py
#

from __future__ import annotations

import json
from pathlib import Path

import pytest
from railroad.domain.identity import IdGenerator

from railroad.config import Config
from railroad.tools.import_exec import import_locos

@pytest.fixture(autouse=True)
def reset_id_generator():
    IdGenerator._next_numbers.clear()


def create_config(tmp_path: Path) -> Config:
    """Create a test configuration."""

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

@pytest.fixture(autouse=True)
def reset_id_generator():
    IdGenerator.reset()


def test_import_locos_discovers_csv_files(tmp_path):
    """All CSV files in the import directory are processed."""

    config = create_config(tmp_path)

    import_directory = tmp_path / "imports"
    import_directory.mkdir()

    (import_directory / "steam.csv").write_text(
    """purpose,locotype,builder,loco_model,nickname,railroad,reporting_mark,road_number,make,dcc,sound,light,smoke,decoder,address,status,store,price,dated
freight,steam,ALCo,4-8-8-4,Big Boy,Union Pacific,UP,4014,Athearn,yes,yes,yes,no,tsunami,3,owned,Model Train Stuff,655,2020-11-20
""",
    encoding="utf-8",
    )
    
    (import_directory / "diesel.csv").write_text(
        """purpose,locotype,builder,loco_model,nickname,railroad,reporting_mark,road_number,make,dcc,sound,light,smoke,decoder,address,status,store,price,dated
switcher,diesel,Plymouth,35T switcher,,Union Pacific,UP,6560,Broadway Limited,yes,no,yes,no,dcc,3,owned,FactoryDirect,100,2021-06-19
""",
        encoding="utf-8",
    )

    count = import_locos(
        config=config,
        import_directory=import_directory,
    )

    assert count == 2

    data_directory = config.data / "loco"

    assert (data_directory / "L001.json").exists()
    assert (data_directory / "L002.json").exists()


def test_import_locos_writes_expected_json(tmp_path):
    """Imported locomotives are persisted through LocoDAO."""

#    @pytest.fixture(autouse=True)
#    def reset_id_generator():
#        IdGenerator.reset()

    config = create_config(tmp_path)

    import_directory = tmp_path / "imports"
    import_directory.mkdir()

    (import_directory / "steam.csv").write_text(
        """purpose,locotype,builder,loco_model,nickname,railroad,reporting_mark,road_number,make,dcc,sound,light,smoke,decoder,address,status,store,price,dated
freight,steam,ALCo,4-8-8-4,Big Boy,Union Pacific,up,4014,Athearn,yes,yes,yes,no,tsunami,3,owned,Model Train Stuff,655,2020-11-20
""",
        encoding="utf-8",
    )

    count = import_locos(
        config=config,
        import_directory=import_directory,
    )

    # temp debug begins
    # print("count:", count)
    # print("data:", config.data)
    # print("loco data:", config.data_config("loco").path)
    # print("files:", list(config.data_config("loco").path.glob("*")))
    # temp debug ends
    assert count == 1

    path = config.data / "loco" / "L001.json"

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert payload["identity"]["id"] == "L001"
    assert payload["identity"]["reporting_mark"] == "UP"
    assert payload["identity"]["road_number"] == "4014"
    assert payload["loco_type"] == "steam"
    assert payload["control"]["type"] == "dcc"
    assert payload["control"]["address"] == 3

