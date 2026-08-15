#!/usr/bin/env python3
# test_roster.py

"""
Tests for the car Roster.
"""

import pytest

from railroad.car.car import Car
from railroad.car.car_type import CarType
from railroad.car.roster import Roster
from railroad.domain.electronics import Electronics
from railroad.domain.identity import Identity
from railroad.domain.model import Model
from railroad.domain.ownership import Ownership, OwnershipStatus
from railroad.domain.prototype import Prototype, Purpose


def create_car(
    road_number: int,
    car_type: CarType = CarType.WAGON,
) -> Car:
    """Create a representative car for roster tests."""

    identity = Identity.create(
        prefix="C",
        entity_type="car",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=road_number,
    )

    prototype = Prototype(
        builder="ACF",
        model="box wagon",
        nickname=None,
        purpose=Purpose.FREIGHT,
    )

    model = Model(
        manufacturer="Atlas",
        product=f"UP {road_number}",
    )

    electronics = Electronics(
        dcc=False,
    )

    ownership = Ownership(
        status=OwnershipStatus.OWNED,
    )

    return Car(
        identity=identity,
        prototype=prototype,
        model=model,
        electronics=electronics,
        ownership=ownership,
        car_type=car_type,
    )


def test_empty_roster() -> None:
    """A newly created roster is empty."""

    roster = Roster()

    assert len(roster) == 0
    assert list(roster) == []


def test_roster_can_be_initialized_with_cars() -> None:
    """A roster can be initialized with cars."""

    car = create_car(12345)
    roster = Roster([car])

    assert len(roster) == 1
    assert roster.get(car.id) is car


def test_add_car() -> None:
    """A car can be added to a roster."""

    roster = Roster()
    car = create_car(12345)

    roster.add(car)

    assert len(roster) == 1
    assert roster.get(car.id) is car


def test_add_duplicate_car_id_is_rejected() -> None:
    """Duplicate car IDs are not allowed."""

    roster = Roster()
    car = create_car(12345)

    roster.add(car)

    with pytest.raises(ValueError):
        roster.add(car)


def test_get_missing_car() -> None:
    """Getting a missing car raises KeyError."""

    roster = Roster()

    with pytest.raises(KeyError):
        roster.get("C999")


def test_contains_id() -> None:
    """Roster can determine whether a car ID exists."""

    roster = Roster()
    car = create_car(12345)

    assert not roster.contains_id(car.id)

    roster.add(car)

    assert roster.contains_id(car.id)


def test_remove_car() -> None:
    """A car can be removed from the roster."""

    roster = Roster()
    car = create_car(12345)

    roster.add(car)

    removed = roster.remove(car.id)

    assert removed is car
    assert len(roster) == 0
    assert not roster.contains_id(car.id)


def test_remove_missing_car() -> None:
    """Removing a missing car raises KeyError."""

    roster = Roster()

    with pytest.raises(KeyError):
        roster.remove("C999")


def test_roster_iteration() -> None:
    """Roster iteration preserves insertion order."""

    first = create_car(12345, CarType.WAGON)
    second = create_car(67890, CarType.HOPPER)

    roster = Roster()
    roster.add(first)
    roster.add(second)

    cars = list(roster)

    assert cars == [first, second]


def test_roster_rejects_non_car() -> None:
    """Roster accepts only Car objects."""

    roster = Roster()

    with pytest.raises(TypeError):
        roster.add("not a car")


def test_roster_rejects_invalid_initial_contents() -> None:
    """Roster cannot be initialized with non-Car objects."""

    with pytest.raises(TypeError):
        Roster(["not a car"])
