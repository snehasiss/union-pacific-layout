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
    response = web.get("/")
    assert response.status_code == 200
    assert b"Operations desk" in response.data
    assert b"Create equipment" in response.data
    assert b'id="create-dialog"' in response.data
    assert b"static/css/railroad.css" in response.data
    assert b"static/img/union-pacific-logo.png" in response.data
    response = web.get("/assets/L001")
    assert response.status_code == 200
    assert b'data-asset-id="L001"' in response.data


def test_roster_and_asset_json_api(client):
    web, _ = client
    response = web.get("/api/assets?type=loco&status=stored&reporting_mark=up")
    assert response.status_code == 200
    assert response.json["count"] == 1
    assert response.json["assets"][0]["identity"]["id"] == "L001"
    assert web.get("/api/assets?type=signal").status_code == 400
    assert web.get("/api/assets/L001").json["prototype"]["model"] == "4-8-8-4"
    assert web.get("/api/assets/L001/media").json == {"media": []}


def test_owner_photos_are_available_in_media(client):
    web, _ = client
    # The test fixture contains L001 only; verify the application media manifest
    # through its default configuration separately.
    app = create_app()
    response = app.test_client().get("/api/assets/L124/media")
    assert response.status_code == 200
    assert any(entry["kind"] == "model" for entry in response.json["media"])
    assert any(entry["url"] == "/photos/L124-UP3826-1.jpg" for entry in response.json["media"])
    assert all(entry["credit"] == "(C) Snehasis Sinha" for entry in response.json["media"])
    assert all(app.test_client().get(entry["url"]).status_code == 200 for entry in response.json["media"])
    media = app.test_client().get("/api/assets/L012/media").json["media"]
    assert {entry["kind"] for entry in media} == {"model", "prototype"}
    assert all(app.test_client().get(entry["url"]).status_code == 200 for entry in media)
    mow_media = app.test_client().get("/api/assets/M002/media").json["media"]
    assert mow_media[0]["url"] == "/photos/M002-NR73208-1.jpg"
    assert app.test_client().get(mow_media[0]["url"]).status_code == 200


def test_newly_imported_locomotive_photos_are_mapped_and_served():
    app = create_app()
    web = app.test_client()
    expected_urls = {
        "L014": ["/photos/L014-UP7928-1.jpg", "/photos/L014-UP7928-2.jpg"],
        "L036": ["/photos/L036-UP971-1.jpg"],
        "L040": ["/photos/L040-UP523-1.jpg"],
        "L041": ["/photos/L041-UP523B-1.jpg"],
        "L042": ["/photos/L042-UP517B-1.jpg"],
        "L046": [
            "/photos/L046-UP903999-1.jpg",
            "/photos/L046-UP903999-2.jpg",
            "/photos/L046-UP903999-3.jpg",
            "/photos/L046-UP903999-4.jpg",
        ],
        "L054": ["/photos/L054-UP700-1.jpg", "/photos/L054-UP700-2.jpg"],
        "L062": ["/photos/L062-UP66-1.jpg", "/photos/L062-UP66-2.jpg", "/photos/L062-UP66-3.jpg"],
        "L102": ["/photos/L102-UP8503-1.jpg"],
        "L115": ["/photos/L115-UP627-1.jpg", "/photos/L115-UP627-2.jpg"],
        "L148": ["/photos/L148-BO5311-1.jpg", "/photos/L148-BO5311-2.jpg"],
    }
    for asset_id, urls in expected_urls.items():
        media = web.get(f"/api/assets/{asset_id}/media").json["media"]
        assert [entry["url"] for entry in media] == urls
        assert all(web.get(url).status_code == 200 for url in urls)


def test_default_configuration_renders_roster():
    app = create_app()
    app.testing = True
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert b"Operations desk" in response.data


def test_update_retire_and_view_retired_asset(client):
    web, railway = client
    response = web.post("/assets/L001/update", json={"model": {"note": "checked"}})
    assert response.status_code == 200
    assert response.json["model"]["note"] == "checked"
    assert web.post("/assets/L001/retire").status_code == 302
    assert web.get("/api/assets").json["count"] == 0
    assert web.get("/assets/L001").status_code == 200
    assert web.get("/api/assets/L001").status_code == 200
    assert LocoDAO(railway).get("L001").model.status == Status.RETIRED


def test_update_allows_identity_details_but_not_record_id(client):
    web, railway = client
    response = web.post("/assets/L001/update", json={"identity": {"road_number": "4014"}})
    assert response.status_code == 200
    assert response.json["identity"]["road_number"] == "4014"
    assert LocoDAO(railway).get("L001").road_number == "4014"
    assert web.post("/assets/L001/update", json={"identity": {"id": "L002"}}).status_code == 400


def test_create_default_locomotive_with_json_patch(client):
    web, _ = client
    response = web.post("/assets", json={"type": "loco", "road_number": "844", "patch": {"model": {"note": "new"}}})
    assert response.status_code == 201
    assert response.json["identity"]["id"] == "L002"
    assert response.json["model"]["note"] == "new"
