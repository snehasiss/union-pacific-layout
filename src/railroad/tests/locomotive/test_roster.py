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
from railroad.locomotive.locomotive import Locomotive
from railroad.locomotive.roster import Roster


def create_locomotive(
    road_number: int,
) -> Locomotive:
    """Create a representative locomotive for testing."""

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

    return Locomotive(
        identity=identity,
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


def test_roster_can_be_initialized_with_locomotives() -> None:
    """A roster can be initialized with locomotives."""

    locomotive = create_locomotive(844)
    roster = Roster([locomotive])

    assert len(roster) == 1
    assert roster.get(locomotive.id) is locomotive


def test_add_locomotive() -> None:
    """A locomotive can be added to a roster."""

    roster = Roster()
    locomotive = create_locomotive(844)

    roster.add(locomotive)

    assert len(roster) == 1
    assert roster.get(locomotive.id) is locomotive


def test_add_duplicate_locomotive_id_is_rejected() -> None:
    """Duplicate locomotive IDs are not allowed."""

    roster = Roster()
    locomotive = create_locomotive(844)

    roster.add(locomotive)

    with pytest.raises(ValueError):
        roster.add(locomotive)


def test_get_missing_locomotive() -> None:
    """Getting a missing locomotive raises KeyError."""

    roster = Roster()

    with pytest.raises(KeyError):
        roster.get("L999")


def test_contains_id() -> None:
    """Roster can determine whether an ID exists."""

    roster = Roster()
    locomotive = create_locomotive(844)

    assert not roster.contains_id(locomotive.id)

    roster.add(locomotive)

    assert roster.contains_id(locomotive.id)


def test_remove_locomotive() -> None:
    """A locomotive can be removed from the roster."""

    roster = Roster()
    locomotive = create_locomotive(844)

    roster.add(locomotive)

    removed = roster.remove(locomotive.id)

    assert removed is locomotive
    assert len(roster) == 0
    assert not roster.contains_id(locomotive.id)


def test_remove_missing_locomotive() -> None:
    """Removing a missing locomotive raises KeyError."""

    roster = Roster()

    with pytest.raises(KeyError):
        roster.remove("L999")


def test_roster_iteration() -> None:
    """Roster iteration preserves insertion order."""

    first = create_locomotive(844)
    second = create_locomotive(4014)

    roster = Roster()
    roster.add(first)
    roster.add(second)

    locomotives = list(roster)

    assert locomotives == [first, second]


def test_roster_rejects_non_locomotive() -> None:
    """Roster accepts only Locomotive objects."""

    roster = Roster()

    with pytest.raises(TypeError):
        roster.add("not a locomotive")


def test_roster_rejects_invalid_initial_contents() -> None:
    """Roster cannot be initialized with non-locomotive objects."""

    with pytest.raises(TypeError):
        Roster(["not a locomotive"])

