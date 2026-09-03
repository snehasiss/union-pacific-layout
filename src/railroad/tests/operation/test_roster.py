#!/usr/bin/env python3
# test_roster.py

import pytest
from types import SimpleNamespace

from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.operation.roster import Roster
from railroad.rs.loco import Loco, LocoType


def loco(entity_id: str, reporting_mark: str, road_number: str, status: Status) -> Loco:
    return Loco(
        identity=Identity(id=entity_id, entity_type=EntityType.LOCO, railroad="Union Pacific", reporting_mark=reporting_mark, road_number=road_number),
        loco_type=LocoType.STEAM,
        prototype=Prototype(builder="ALCo", model="4-8-8-4", nickname="Big Boy", purpose=Purpose.FREIGHT),
        model=Model(maker="Athearn", product="Genesis Big Boy", status=status),
        control=Control(type=ControlType.DCC, light=True, sound=True, smoke=False, decoder="Paragon4", address=int(road_number)),
    )


def test_retired_objects_are_not_added():
    roster = Roster([
        loco("L001", "UP", "4014", Status.STORED),
        loco("L002", "UP", "844", Status.RETIRED),
    ])
    assert [obj.id for obj in roster] == ["L001"]
    assert len(roster) == 1


def test_search_returns_ids():
    roster = Roster([
        loco("L001", "UP", "4014", Status.ACTIVE),
        loco("L002", "UP", "844", Status.STORED),
        loco("L003", "SP", "4449", Status.ACTIVE),
    ])
    assert roster.search({"reporting_mark": "UP"}) == ["L001", "L002"]
    assert roster.search({"reporting_mark": "UP", "road_number": "844"}) == ["L002"]


def test_search_can_match_nested_model_attributes():
    roster = Roster([
        loco("L001", "UP", "4014", Status.ACTIVE),
        loco("L002", "UP", "844", Status.REPAIR),
    ])
    assert roster.search({"model.status": Status.ACTIVE}) == ["L001"]


@pytest.mark.parametrize(
    "query",
    ["l001", "4014", "up", "steam", "alco", "big boy", "athearn", "genesis"],
)
def test_free_text_search_uses_canonical_attributes(query):
    roster = Roster([loco("L001", "UP", "4014", Status.ACTIVE)])

    assert roster.search_text(query) == ["L001"]


def test_free_text_search_is_case_insensitive_and_ignores_missing_type_fields():
    roster = Roster([loco("L001", "UP", "4014", Status.ACTIVE)])

    assert roster.search_text("BiG BoY") == ["L001"]
    assert roster.search_text("gondola") == []
    assert roster.search_text("") == ["L001"]


def test_free_text_search_rejects_non_string_query():
    roster = Roster([loco("L001", "UP", "4014", Status.ACTIVE)])

    with pytest.raises(TypeError, match="query must be a string"):
        roster.search_text(None)


def test_search_without_criteria_returns_all_active_ids():
    roster = Roster([
        loco("L001", "UP", "4014", Status.ACTIVE),
        loco("L002", "UP", "844", Status.RETIRED),
        loco("L003", "SP", "4449", Status.STORED),
    ])
    assert roster.search() == ["L001", "L003"]


def test_search_rejects_non_mapping_criteria():
    roster = Roster([loco("L001", "UP", "4014", Status.ACTIVE)])
    with pytest.raises(TypeError, match="criteria must be a mapping"):
        roster.search([("reporting_mark", "UP")])


def test_search_rejects_duplicate_mapping_and_keyword_criteria():
    roster = Roster([loco("L001", "UP", "4014", Status.ACTIVE)])
    with pytest.raises(ValueError, match="criteria specified more than once"):
        roster.search({"reporting_mark": "UP"}, reporting_mark="UP")


def test_from_config_loads_supported_types_and_excludes_retired_objects():
    config = object()
    daos = {
        EntityType.LOCO: FakeDAO([loco("L001", "UP", "4014", Status.ACTIVE)]),
        EntityType.CAR: FakeDAO([SimpleNamespace(id="C001", model=Model(status=Status.STORED))]),
        EntityType.MOW: FakeDAO([SimpleNamespace(id="M001", model=Model(status=Status.RETIRED))]),
    }
    calls = []

    def dao_factory(entity_type, received_config):
        calls.append((entity_type, received_config))
        return daos[entity_type]

    roster = Roster.from_config(config, dao_factory=dao_factory)

    assert roster.search() == ["L001", "C001"]
    assert calls == [
        (EntityType.LOCO, config),
        (EntityType.CAR, config),
        (EntityType.MOW, config),
    ]


def test_from_config_rejects_an_unknown_entity_type():
    with pytest.raises(TypeError, match="entity_types must contain only EntityType"):
        Roster.from_config(object(), entity_types=["loco"])


class FakeDAO:
    def __init__(self, objects):
        self._objects = objects

    def list(self):
        return self._objects
