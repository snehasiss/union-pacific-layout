#!/usr/bin/env python3
# test_roster.py

"""
Tests for the MOW Roster.
"""

import pytest

from railroad.domain.electronics import Electronics
from railroad.domain.identity import Identity
from railroad.domain.model import Model
from railroad.domain.ownership import Ownership, OwnershipStatus
from railroad.domain.prototype import Prototype, Purpose
from railroad.mow.mow import MOW
from railroad.mow.mow_type import MOWType
from railroad.mow.roster import Roster


def create_mow(
    road_number: int,
    mow_type: MOWType = MOWType.TAMPER,
    self_propelled: bool = True,
) -> MOW:
    """Create an MOW asset for roster tests."""

    identity = Identity.create(
        prefix="M",
        entity_type="mow",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=road_number,
    )

    prototype = Prototype(
        builder="Plasser",
        model="Tamper",
        nickname=None,
        purpose=Purpose.MACHINE,
    )

    model = Model(
        manufacturer="Plasser",
        product="Tamper",
    )

    electronics = Electronics(
        dcc=True,
        decoder="LokSound",
        sound=True,
    )

    ownership = Ownership(
        status=OwnershipStatus.OWNED,
    )

    return MOW(
        identity=identity,
        prototype=prototype,
        model=model,
        electronics=electronics,
        ownership=ownership,
        mow_type=mow_type,
        self_propelled=self_propelled,
    )


def test_empty_roster() -> None:
    """A newly created roster is empty."""

    roster = Roster()

    assert len(roster) == 0
    assert list(roster) == []


def test_roster_can_be_initialized_with_mow() -> None:
    """A roster can be initialized with MOW assets."""

    mow = create_mow(100)
    roster = Roster([mow])

    assert len(roster) == 1
    assert roster.get(mow.id) is mow


def test_add_mow() -> None:
    """An MOW asset can be added to a roster."""

    roster = Roster()
    mow = create_mow(100)

    roster.add(mow)

    assert len(roster) == 1
    assert roster.get(mow.id) is mow


def test_add_duplicate_mow_id_is_rejected() -> None:
    """Duplicate MOW IDs are not allowed."""

    roster = Roster()
    mow = create_mow(100)

    roster.add(mow)

    with pytest.raises(ValueError):
        roster.add(mow)


def test_get_missing_mow() -> None:
    """Getting a missing MOW asset raises KeyError."""

    roster = Roster()

    with pytest.raises(KeyError):
        roster.get("M999")


def test_contains_id() -> None:
    """Roster can determine whether an MOW ID exists."""

    roster = Roster()
    mow = create_mow(100)

    assert not roster.contains_id(mow.id)

    roster.add(mow)

    assert roster.contains_id(mow.id)


def test_remove_mow() -> None:
    """An MOW asset can be removed from a roster."""

    roster = Roster()
    mow = create_mow(100)

    roster.add(mow)

    removed = roster.remove(mow.id)

    assert removed is mow
    assert len(roster) == 0
    assert not roster.contains_id(mow.id)


def test_remove_missing_mow() -> None:
    """Removing a missing MOW asset raises KeyError."""

    roster = Roster()

    with pytest.raises(KeyError):
        roster.remove("M999")


def test_roster_iteration() -> None:
    """Roster iteration preserves insertion order."""

    first = create_mow(100, MOWType.TAMPER, True)
    second = create_mow(200, MOWType.MPV, True)

    roster = Roster()
    roster.add(first)
    roster.add(second)

    mow_assets = list(roster)

    assert mow_assets == [first, second]


def test_roster_rejects_non_mow() -> None:
    """Roster accepts only MOW objects."""

    roster = Roster()

    with pytest.raises(TypeError):
        roster.add("not an MOW")


def test_roster_rejects_invalid_initial_contents() -> None:
    """Roster cannot be initialized with non-MOW objects."""

    with pytest.raises(TypeError):
        Roster(["not an MOW"])
