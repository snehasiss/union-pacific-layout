from __future__ import annotations

import json

import pytest

from railroad.config import Config
from railroad.dao.loco import LocoDAO
from railroad.domain.control import Control
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.loco import Loco, LocoType
from railroad.service import create_app


def config(tmp_path) -> Config:
    (tmp_path / "config").mkdir()
    path = tmp_path / "config" / "railroad-conf.json"
    path.write_text(json.dumps({"application": {"name": "test"}, "paths": {"config": "config", "data": "data", "resources": "resources", "logs": "logs"}, "data": {"loco": {"path": "loco", "prefix": "L"}, "car": {"path": "car", "prefix": "C"}, "mow": {"path": "mow", "prefix": "M"}}, "resources": {"drawings": "resources/drawings", "media": "resources/media"}}))
    return Config(path)


def save_loco(railway):
    LocoDAO(railway).save(Loco(Identity("L001", EntityType.LOCO, "Union Pacific", "UP", "4014"), LocoType.STEAM, Prototype("ALCo", "4-8-8-4", "Big Boy", Purpose.FREIGHT), Model(), Control()))


@pytest.fixture
def client(tmp_path):
    railway = config(tmp_path); save_loco(railway)
    return create_app(railway._path).test_client(), railway


def test_roster_and_asset_pages(client):
    web, _ = client
    assert b"L001" in web.get("/").data
    response = web.get("/assets/L001")
    assert response.status_code == 200
    assert b"<h1>L001</h1>" in response.data


def test_default_configuration_renders_roster():
    app = create_app()
    app.testing = True
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert b"Operational roster" in response.data


def test_update_retire_and_view_retired_asset(client):
    web, railway = client
    response = web.post("/assets/L001/update", json={"model": {"note": "checked"}})
    assert response.status_code == 200
    assert response.json["model"]["note"] == "checked"
    assert web.post("/assets/L001/retire").status_code == 302
    assert b"L001" not in web.get("/").data
    assert web.get("/assets/L001").status_code == 200
    assert LocoDAO(railway).get("L001").model.status == Status.RETIRED


def test_create_default_locomotive_with_json_patch(client):
    web, _ = client
    response = web.post("/assets", json={"type": "loco", "road_number": "844", "patch": {"model": {"note": "new"}}})
    assert response.status_code == 201
    assert response.json["identity"]["id"] == "L002"
    assert response.json["model"]["note"] == "new"
