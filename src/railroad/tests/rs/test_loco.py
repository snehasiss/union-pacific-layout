#!/usr/bin/env python3
# test_roster.py
#

"""
Tests for the locomotive Roster.
"""

import pytest

from railroad.domain.electronics import Electronics
from railroad.domain.identity import Identity
from railroad.domain.model import Model
from railroad.domain.ownership import Ownership, OwnershipStatus
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.loco import Loco
from railroad.rs.roster import Roster
from railroad.rs.loco_type import LocoType


def create_loco(
    road_number: int,
) -> Loco:
    """Create a representative loco for testing."""

    identity = Identity.create(
        prefix="L",
        entity_type="steam",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=road_number,
    )

    prototype = Prototype(
        builder="ALCo",
        model="4-8-4",
        nickname="Northern",
        purpose=Purpose.PASSENGER,
    )

    model = Model(
        manufacturer="Broadway Limited Imports",
        product=f"UP {road_number}",
    )

    electronics = Electronics(
        dcc=True,
        decoder="LokSound",
        sound=True,
    )

    ownership = Ownership(
        status=OwnershipStatus.OWNED,
    )

    return Loco(
        identity=identity,
		loco_type: LocoType.STEAM
		prototype=prototype,
        model=model,
        electronics=electronics,
        ownership=ownership,
    )


def test_empty_roster() -> None:
    """A newly created roster is empty."""

    roster = Roster()

    assert len(roster) == 0
    assert list(roster) == []


def test_roster_can_be_initialized_with_locos() -> None:
    """A roster can be initialized with locomotives."""

    loco = create_loco(844)
    roster = Roster([loco])

    assert len(roster) == 1
    assert roster.get(loco.id) is loco


def test_add_loco() -> None:
    """A locomotive can be added to a roster."""

    roster = Roster()
    loco = create_loco(844)

    roster.add(loco)

    assert len(roster) == 1
    assert roster.get(loco.id) is loco


def test_add_duplicate_loco_id_is_rejected() -> None:
    """Duplicate locomotive IDs are not allowed."""

    roster = Roster()
    loco = create_loco(844)

    roster.add(loco)

    with pytest.raises(ValueError):
        roster.add(loco)


def test_get_missing_loco() -> None:
    """Getting a missing locomotive raises KeyError."""

    roster = Roster()

    with pytest.raises(KeyError):
        roster.get("L999")


def test_contains_id() -> None:
    """Roster can determine whether an ID exists."""

    roster = Roster()
    loco = create_loco(844)

    assert not roster.contains_id(loco.id)

    roster.add(loco)

    assert roster.contains_id(loco.id)


def test_remove_loco() -> None:
    """A locomotive can be removed from the roster."""

    roster = Roster()
    loco = create_loco(844)

    roster.add(loco)

    removed = roster.remove(loco.id)

    assert removed is loco
    assert len(roster) == 0
    assert not roster.contains_id(loco.id)


def test_remove_missing_loco() -> None:
    """Removing a missing locomotive raises KeyError."""

    roster = Roster()

    with pytest.raises(KeyError):
        roster.remove("L999")


def test_roster_iteration() -> None:
    """Roster iteration preserves insertion order."""

    first = create_loco(844)
    second = create_loco(4014)

    roster = Roster()
    roster.add(first)
    roster.add(second)

    locos = list(roster)

    assert locos == [first, second]


def test_roster_rejects_non_loco() -> None:
    """Roster accepts only Locomotive objects."""

    roster = Roster()

    with pytest.raises(TypeError):
        roster.add("not a locomotive")


def test_roster_rejects_invalid_initial_contents() -> None:
    """Roster cannot be initialized with non-locomotive objects."""

    with pytest.raises(TypeError):
        Roster(["not a locomotive"])

def test_loco_rejects_invalid_loco_type() -> None:
    """Loco rejects a value that is not a LocoType."""

    with pytest.raises(TypeError):
        Loco(
            identity=identity,
            loco_type="steam",
            prototype=prototype,
            model=model,
            electronics=electronics,
            ownership=ownership,
        )

