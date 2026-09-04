from __future__ import annotations

import json

import pytest

from chat import create_app
from chat.interpreter import Intent, RuleInterpreter, SlmInterpreter
from railroad.config import Config
from railroad.dao.loco import LocoDAO
from railroad.domain.control import Control, ControlType
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


def test_locomotive_subtype_is_preserved_as_a_structured_filter():
    web = create_app().test_client()
    all_baldwin = web.post("/api/chat", json={"message": "show locomotives made by baldwin"}).json
    diesel = web.post("/api/chat", json={"message": "show diesel locomotives made by baldwin"}).json
    steam = web.post("/api/chat", json={"message": "show steam locomotives made by baldwin"}).json

    all_ids = {asset["identity"]["id"] for asset in all_baldwin["assets"]}
    diesel_ids = {asset["identity"]["id"] for asset in diesel["assets"]}
    steam_ids = {asset["identity"]["id"] for asset in steam["assets"]}
    assert diesel_ids and steam_ids
    assert diesel_ids.isdisjoint(steam_ids)
    assert diesel_ids | steam_ids == all_ids
    assert {asset["loco_type"] for asset in diesel["assets"]} == {"diesel"}
    assert {asset["loco_type"] for asset in steam["assets"]} == {"steam"}


@pytest.mark.parametrize(
    ("message", "control_type", "sound"),
    [
        ("show locomotives with DCC sound", "dcc", True),
        ("show locomotives with DC", "dc", None),
    ],
)
def test_control_capabilities_are_structured_filters(message, control_type, sound):
    intent = RuleInterpreter().interpret(message)
    assert intent.entity_type == EntityType.LOCO
    assert intent.control_type == ControlType(control_type)
    assert intent.sound is sound
    assert intent.query == ""

    response = create_app().test_client().post("/api/chat", json={"message": message})
    assert response.status_code == 200
    assert response.json["count"] > 0
    assert {asset["control"]["type"] for asset in response.json["assets"]} == {control_type}
    if sound is not None:
        assert {asset["control"]["sound"] for asset in response.json["assets"]} == {sound}


def test_debug_response_shows_raw_slm_output_and_fallback(monkeypatch, client):
    web, _ = client
    app = web.application
    app.config.update(CHAT_SLM_URL="http://unused", CHAT_SLM_MODEL="test-model", CHAT_SLM_DEBUG=True)

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            response = {"choices": [{"message": {"content": "not valid JSON"}}]}
            return json.dumps(response).encode("utf-8")

    monkeypatch.setattr("chat.interpreter.request.urlopen", lambda *_args, **_kwargs: FakeResponse())
    response = web.post("/api/chat", json={"message": "show steam locomotives made by ALCo"})

    assert response.status_code == 200
    assert response.json["debug"]["source"] == "rules-fallback"
    assert response.json["debug"]["raw_response"] == "not valid JSON"
    assert response.json["debug"]["intent"]["subtype"] == "steam"
    assert {asset["loco_type"] for asset in response.json["assets"]} == {"steam"}


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


@pytest.mark.parametrize(
    ("message", "entity_type"),
    [
        ("show locomotives", EntityType.LOCO),
        ("show all cars", EntityType.CAR),
        ("list MOW", EntityType.MOW),
        ("show assets", None),
        ("show equipment", None),
        ("show equipments", None),
        ("show the roster", None),
    ],
)
def test_exhaustive_list_commands_are_deterministic(message, entity_type, monkeypatch):
    def unexpected_slm_call(*_args, **_kwargs):
        raise AssertionError("An exhaustive list command must not call the SLM.")

    monkeypatch.setattr("chat.interpreter.request.urlopen", unexpected_slm_call)
    intent = SlmInterpreter("http://unused", "unused").interpret(message)

    assert intent == Intent("search", entity_type=entity_type)


@pytest.mark.parametrize(
    ("message", "asset_type"),
    [
        ("show locomotives", "loco"),
        ("show all cars", "car"),
        ("show MOW", "mow"),
        ("show assets", None),
        ("show equipments", None),
    ],
)
def test_exhaustive_chat_lists_match_the_complete_app_roster(message, asset_type):
    query = {"type": asset_type} if asset_type else None
    expected = create_roster_app().test_client().get("/api/assets", query_string=query).json
    actual = create_app().test_client().post("/api/chat", json={"message": message}).json

    assert actual["count"] == expected["count"]
    assert [asset["identity"]["id"] for asset in actual["assets"]] == [
        asset["identity"]["id"] for asset in expected["assets"]
    ]
