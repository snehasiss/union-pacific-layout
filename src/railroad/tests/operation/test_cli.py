from __future__ import annotations

import json

import pytest

from railroad.config import Config
from railroad.dao.loco import LocoDAO
from railroad.domain.control import Control
from railroad.domain.identity import EntityType, IdGenerator, Identity
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.loco import Loco, LocoType
from railroad.operation.cli import run


@pytest.fixture(autouse=True)
def reset_ids():
    IdGenerator.reset()


def config(tmp_path) -> Config:
    (tmp_path / "config").mkdir()
    path = tmp_path / "config" / "railroad-conf.json"
    path.write_text(json.dumps({"application": {"name": "test"}, "paths": {"config": "config", "data": "data", "resources": "resources", "logs": "logs"}, "data": {"loco": {"path": "loco", "prefix": "L"}, "car": {"path": "car", "prefix": "C"}, "mow": {"path": "mow", "prefix": "M"}}, "resources": {"drawings": "resources/drawings", "media": "resources/media"}}))
    return Config(path)


def save_loco(config, status=Status.STORED):
    loco = Loco(Identity("L001", EntityType.LOCO, "Union Pacific", "UP", "4014"), LocoType.STEAM, Prototype("ALCo", "4-8-8-4", "Big Boy", Purpose.FREIGHT), Model(status=status), Control())
    LocoDAO(config).save(loco)


def args(config, *command):
    return ["--config", str(config._path), *command]


def test_view_outputs_json(tmp_path, capsys):
    railway = config(tmp_path); save_loco(railway)
    assert run(args(railway, "view", "L001")) == 0
    assert json.loads(capsys.readouterr().out)["identity"]["id"] == "L001"


def test_update_and_retire_persist_changes(tmp_path, capsys):
    railway = config(tmp_path); save_loco(railway)
    patch = tmp_path / "patch.json"; patch.write_text('{"model": {"note": "checked"}}')
    run(args(railway, "update", "L001", "--input", str(patch)))
    run(args(railway, "retire", "L001"))
    saved = LocoDAO(railway).get("L001")
    assert saved.model.note == "checked"
    assert saved.model.status == Status.RETIRED
    assert capsys.readouterr().out == "L001\nL001\n"


def test_update_accepts_set_assignments(tmp_path):
    railway = config(tmp_path); save_loco(railway)
    run(args(railway, "update", "L001", "--set", "model.note=checked", "--set", "model.status=active", "--set", "control.light=true"))
    saved = LocoDAO(railway).get("L001")
    assert saved.model.note == "checked"
    assert saved.model.status == Status.ACTIVE
    assert saved.control.light is True


def test_search_excludes_retired_and_create_accepts_json_patch(tmp_path, capsys):
    railway = config(tmp_path); save_loco(railway, Status.RETIRED)
    patch = tmp_path / "create.json"; patch.write_text('{"loco_type": "steam", "model": {"note": "new"}}')
    run(args(railway, "create", "--type", "loco", "--input", str(patch), "--road-number", "844"))
    run(args(railway, "search", "--where", "model.status=stored"))
    assert capsys.readouterr().out == "L002\nL002\n"
    assert LocoDAO(railway).get("L002").model.note == "new"
