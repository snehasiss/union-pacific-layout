#!/usr/bin/env python3
# railroad/tests/rs/test_roster.py

"""Tests for the locomotive Roster domain object."""

from __future__ import annotations

import pytest

from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.loco import Loco, LocoType
from railroad.rs.roster import Roster


def create_loco(loco_id: str = "L001") -> Loco:
    identity = Identity(id=loco_id, entity_type=EntityType.LOCO, railroad="Union Pacific", reporting_mark="UP", road_number="4014")
    prototype = Prototype(builder="ALCo", model="4-8-8-4", nickname="Big Boy", purpose=Purpose.FREIGHT)
    model = Model(
        maker="Athearn",
        product="Genesis Big Boy",
        status=Status.STORED,
        source="Model Train Stuff",
        price=599.99,
    )
    control = Control(type=ControlType.DCC, light=True, sound=True, smoke=False, decoder="Paragon4", address=4014)
    return Loco(identity=identity, prototype=prototype, model=model, control=control, loco_type=LocoType.STEAM)


def test_empty_roster() -> None:
    roster = Roster()
    assert len(roster) == 0
    assert list(roster) == []


def test_roster_accepts_locos() -> None:
    loco = create_loco()
    roster = Roster([loco])
    assert len(roster) == 1
    assert roster.locos == [loco]


def test_roster_rejects_non_list() -> None:
    with pytest.raises(TypeError):
        Roster("invalid")


def test_roster_rejects_non_loco() -> None:
    with pytest.raises(TypeError):
        Roster(["invalid"])


def test_add_loco() -> None:
    roster = Roster()
    loco = create_loco()
    roster.add(loco)
    assert len(roster) == 1
    assert roster.get("L001") is loco


def test_add_rejects_non_loco() -> None:
    roster = Roster()
    with pytest.raises(TypeError):
        roster.add("invalid")


def test_add_rejects_duplicate_id() -> None:
    roster = Roster()
    roster.add(create_loco("L001"))
    with pytest.raises(ValueError):
        roster.add(create_loco("L001"))


def test_get_loco() -> None:
    loco = create_loco("L001")
    roster = Roster([loco])
    assert roster.get("L001") is loco


def test_get_missing_loco() -> None:
    with pytest.raises(KeyError):
        Roster().get("L999")


def test_remove_loco() -> None:
    loco = create_loco("L001")
    roster = Roster([loco])
    result = roster.remove("L001")
    assert result is loco
    assert len(roster) == 0
    assert roster.contains_id("L001") is False


def test_remove_missing_loco() -> None:
    with pytest.raises(KeyError):
        Roster().remove("L999")


def test_contains_id() -> None:
    roster = Roster([create_loco("L001")])
    assert roster.contains_id("L001") is True
    assert roster.contains_id("L002") is False


def test_len() -> None:
    roster = Roster([create_loco("L001"), create_loco("L002"), create_loco("L003")])
    assert len(roster) == 3


def test_iteration_preserves_order() -> None:
    loco1 = create_loco("L001")
    loco2 = create_loco("L002")
    loco3 = create_loco("L003")
    roster = Roster([loco1, loco2, loco3])
    assert list(roster) == [loco1, loco2, loco3]
