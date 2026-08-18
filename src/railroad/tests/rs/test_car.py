#!/usr/bin/env python3
# test_car.py

"""
Tests for the Car domain entity.
"""

import pytest

from railroad.rs.car import Car
from railroad.rs.car_type import CarType
from railroad.domain.electronics import Electronics
from railroad.domain.identity import Identity
from railroad.domain.model import Model
from railroad.domain.ownership import Ownership, OwnershipStatus
from railroad.domain.prototype import Prototype, Purpose


def create_car(
    road_number: int = 12345,
    car_type: CarType = CarType.WAGON,
) -> Car:
    """Create a representative car for testing."""

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


def test_car_can_be_created() -> None:
    """A car can be constructed from domain components."""

    car = create_car()

    assert isinstance(car, Car)


def test_car_contains_domain_components() -> None:
    """A car contains all required domain components."""

    car = create_car()

    assert isinstance(car.identity, Identity)
    assert isinstance(car.prototype, Prototype)
    assert isinstance(car.model, Model)
    assert isinstance(car.electronics, Electronics)
    assert isinstance(car.ownership, Ownership)
    assert isinstance(car.car_type, CarType)


def test_car_identity_properties() -> None:
    """Identity information is exposed through the car."""

    car = create_car(road_number=54321)

    assert car.id.startswith("C")
    assert car.entity_type == "car"
    assert car.railroad == "Union Pacific"
    assert car.reporting_mark == "UP"
    assert car.road_number == 54321


def test_car_prototype_properties() -> None:
    """Prototype information is exposed through the car."""

    car = create_car()

    assert car.prototype_model == "box wagon"
    assert car.nickname is None


def test_car_type() -> None:
    """The car exposes its CarType."""

    car = create_car(car_type=CarType.HOPPER)

    assert car.car_type is CarType.HOPPER


def test_car_rejects_invalid_identity() -> None:
    """Car requires an Identity object."""

    car = create_car()

    with pytest.raises(TypeError):
        Car(
            identity="invalid",
            prototype=car.prototype,
            model=car.model,
            electronics=car.electronics,
            ownership=car.ownership,
            car_type=car.car_type,
        )


def test_car_rejects_invalid_prototype() -> None:
    """Car requires a Prototype object."""

    car = create_car()

    with pytest.raises(TypeError):
        Car(
            identity=car.identity,
            prototype="invalid",
            model=car.model,
            electronics=car.electronics,
            ownership=car.ownership,
            car_type=car.car_type,
        )


def test_car_rejects_invalid_model() -> None:
    """Car requires a Model object."""

    car = create_car()

    with pytest.raises(TypeError):
        Car(
            identity=car.identity,
            prototype=car.prototype,
            model="invalid",
            electronics=car.electronics,
            ownership=car.ownership,
            car_type=car.car_type,
        )


def test_car_rejects_invalid_electronics() -> None:
    """Car requires an Electronics object."""

    car = create_car()

    with pytest.raises(TypeError):
        Car(
            identity=car.identity,
            prototype=car.prototype,
            model=car.model,
            electronics="invalid",
            ownership=car.ownership,
            car_type=car.car_type,
        )


def test_car_rejects_invalid_ownership() -> None:
    """Car requires an Ownership object."""

    car = create_car()

    with pytest.raises(TypeError):
        Car(
            identity=car.identity,
            prototype=car.prototype,
            model=car.model,
            electronics=car.electronics,
            ownership="invalid",
            car_type=car.car_type,
        )


def test_car_rejects_invalid_car_type() -> None:
    """Car requires a CarType."""

    car = create_car()

    with pytest.raises(TypeError):
        Car(
            identity=car.identity,
            prototype=car.prototype,
            model=car.model,
            electronics=car.electronics,
            ownership=car.ownership,
            car_type="wagon",
        )
