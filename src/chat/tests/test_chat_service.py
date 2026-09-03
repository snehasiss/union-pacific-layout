from __future__ import annotations

import json

import pytest

from chat import create_app
from chat.interpreter import RuleInterpreter
from railroad.config import Config
from railroad.dao.loco import LocoDAO
from railroad.domain.control import Control
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.loco import Loco, LocoType
from railroad.service import create_app as create_roster_app


def make_config(tmp_path) -> Config:
    (tmp_path / "config").mkdir()
    path = tmp_path / "config" / "railroad-conf.json"
    path.write_text(json.dumps({"application": {"name": "test"}, "paths": {"config": "config", "data": "data", "resources": "resources", "logs": "logs"}, "data": {"loco": {"path": "loco", "prefix": "L"}, "car": {"path": "car", "prefix": "C"}, "mow": {"path": "mow", "prefix": "M"}}, "resources": {"drawings": "resources/drawings", "media": "resources/media"}}))
    return Config(path)


def save_loco(config: Config) -> None:
    LocoDAO(config).save(Loco(Identity("L001", EntityType.LOCO, "Union Pacific", "UP", "4014"), LocoType.STEAM, Prototype("ALCo", "4-8-8-4", "Big Boy", Purpose.FREIGHT), Model(status=Status.ACTIVE), Control()))


@pytest.fixture
def client(tmp_path):
    config = make_config(tmp_path)
    save_loco(config)
    app = create_app(config._path)
    app.testing = True
    return app.test_client(), config


def test_page_and_health(client):
    web, _ = client
    page = web.get("/")
    assert page.status_code == 200
    assert b"Asset assistant" in page.data
    assert b"union-pacific-logo.png" in page.data
    assert b'id="inspector"' not in page.data
    assert web.get("/health").json == {
        "ok": True,
        "service": "chat_service",
        "interpreter": "rules",
        "slm_configured": False,
    }


def test_chat_search_uses_core_roster_fields(client):
    web, _ = client
    for query in ("4014", "ALCo", "Big Boy", "steam"):
        response = web.post("/api/chat", json={"message": query})
        assert response.status_code == 200
        assert response.json["count"] == 1
        assert response.json["assets"][0]["identity"]["id"] == "L001"


@pytest.mark.parametrize("query", ["diesel", "gondola", "cleaner", "Athearn"])
def test_app_and_chat_search_return_the_same_asset_ids(query):
    app_response = create_roster_app().test_client().get("/api/assets", query_string={"q": query})
    chat_response = create_app().test_client().post("/api/chat", json={"message": query})

    assert app_response.status_code == chat_response.status_code == 200
    app_ids = [asset["identity"]["id"] for asset in app_response.json["assets"]]
    chat_ids = [asset["identity"]["id"] for asset in chat_response.json["assets"]]
    assert chat_ids == app_ids


def test_natural_search_and_detail(client):
    web, _ = client
    response = web.post("/api/chat", json={"message": "Find locomotives with road number 4014"})
    assert response.json["count"] == 1
    detail = web.post("/api/chat", json={"message": "show L001"})
    assert detail.json["intent"] == "detail"
    assert detail.json["asset"]["prototype"]["nickname"] == "Big Boy"


def test_asset_media_reuses_curated_app_service_media():
    app = create_app()
    web = app.test_client()
    media = web.get("/api/assets/L124/media")
    assert media.status_code == 200
    assert media.json["media"]
    assert media.json["media"][0]["url"].startswith("/photos/")
    assert web.get(media.json["media"][0]["url"]).status_code == 200


def test_asset_without_media_returns_empty_list(client):
    web, _ = client
    assert web.get("/api/assets/L001/media").json == {"media": []}


def test_update_and_create(client):
    web, config = client
    updated = web.patch("/api/assets/L001", json={"model": {"note": "Inspected"}})
    assert updated.status_code == 200
    assert LocoDAO(config).get("L001").model.note == "Inspected"
    created = web.post("/api/assets", json={"type": "loco", "road_number": "844", "patch": {"prototype": {"builder": "ALCo", "model": "FEF-3", "nickname": None}}})
    assert created.status_code == 201
    assert created.json["identity"]["id"] == "L002"


def test_rule_interpreter_exposes_form_actions():
    interpreter = RuleInterpreter()
    assert interpreter.interpret("create a locomotive").operation == "create"
    intent = interpreter.interpret("update L001")
    assert (intent.operation, intent.entity_id) == ("update", "L001")
