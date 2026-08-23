#!/usr/bin/env python3
#
# railroad/tests/rs/test_roster.py
#

"""
Tests for the locomotive Roster domain object.
"""

from __future__ import annotations

from datetime import date

import pytest

from railroad.domain.asset import Asset, AssetStatus
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.loco import Loco
from railroad.rs.loco_type import LocoType
from railroad.rs.roster import Roster


def create_loco(loco_id: str = "L001") -> Loco:
    """Create a valid locomotive for roster testing."""

    identity = Identity(
        id=loco_id,
        entity_type=EntityType.LOCO,
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number="4014",
    )

    prototype = Prototype(
        builder="ALCo",
        model="4-8-8-4",
        nickname="Big Boy",
        purpose=Purpose.FREIGHT,
    )

    model = Model(
        maker="Athearn",
        product="Genesis Big Boy",
    )

    control = Control(
        type=ControlType.DCC,
        light=True,
        sound=True,
        smoke=False,
        decoder="Paragon4",
        address=4014,
    )

    asset = Asset(
        status=AssetStatus.OWNED,
        source="Model Train Stuff",
        price=599.99,
        acquired=date(2026, 1, 1),
    )

    return Loco(
        identity=identity,
        prototype=prototype,
        model=model,
        control=control,
        asset=asset,
        loco_type=LocoType.STEAM,
    )


def test_empty_roster() -> None:
    """A new roster is empty."""

    roster = Roster()

    assert len(roster) == 0
    assert list(roster) == []


def test_roster_accepts_locos() -> None:
    """A roster can be initialized with locomotives."""

    loco = create_loco()
    roster = Roster([loco])

    assert len(roster) == 1
    assert roster.locos == [loco]


def test_roster_rejects_non_list() -> None:
    """Roster contents must be a list."""

    with pytest.raises(TypeError):
        Roster("invalid")


def test_roster_rejects_non_loco() -> None:
    """Roster can contain only Loco objects."""

    with pytest.raises(TypeError):
        Roster(["invalid"])


def test_add_loco() -> None:
    """A locomotive can be added to a roster."""

    roster = Roster()
    loco = create_loco()

    roster.add(loco)

    assert len(roster) == 1
    assert roster.get("L001") is loco


def test_add_rejects_non_loco() -> None:
    """Only Loco objects can be added."""

    roster = Roster()

    with pytest.raises(TypeError):
        roster.add("invalid")


def test_add_rejects_duplicate_id() -> None:
    """A duplicate locomotive ID is rejected."""

    roster = Roster()
    roster.add(create_loco("L001"))

    with pytest.raises(ValueError):
        roster.add(create_loco("L001"))


def test_get_loco() -> None:
    """A locomotive can be retrieved by ID."""

    loco = create_loco("L001")
    roster = Roster([loco])

    result = roster.get("L001")

    assert result is loco


def test_get_missing_loco() -> None:
    """Getting an unknown locomotive raises KeyError."""

    roster = Roster()

    with pytest.raises(KeyError):
        roster.get("L999")


def test_remove_loco() -> None:
    """A locomotive can be removed and returned."""

    loco = create_loco("L001")
    roster = Roster([loco])

    result = roster.remove("L001")

    assert result is loco
    assert len(roster) == 0
    assert roster.contains_id("L001") is False


def test_remove_missing_loco() -> None:
    """Removing an unknown locomotive raises KeyError."""

    roster = Roster()

    with pytest.raises(KeyError):
        roster.remove("L999")


def test_contains_id() -> None:
    """Roster can determine whether an ID exists."""

    roster = Roster([create_loco("L001")])

    assert roster.contains_id("L001") is True
    assert roster.contains_id("L002") is False


def test_len() -> None:
    """Roster length reflects the number of locomotives."""

    roster = Roster(
        [
            create_loco("L001"),
            create_loco("L002"),
            create_loco("L003"),
        ]
    )

    assert len(roster) == 3


def test_iteration_preserves_order() -> None:
    """Roster iteration follows insertion order."""

    loco1 = create_loco("L001")
    loco2 = create_loco("L002")
    loco3 = create_loco("L003")

    roster = Roster([loco1, loco2, loco3])

    assert list(roster) == [loco1, loco2, loco3]
