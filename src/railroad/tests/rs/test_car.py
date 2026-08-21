#!/usr/bin/env python3
#
# railroad/tests/rs/test_car.py
#

"""
Tests for the Car domain entity.
"""

from __future__ import annotations

from datetime import date

import pytest

from railroad.domain.asset import Asset, AssetStatus
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.car import Car
from railroad.rs.car_type import CarType


def create_car() -> Car:
    """Create a valid Car for testing."""

    identity = Identity(
        id="C001",
        entity_type=EntityType.CAR,
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number="12345",
    )

    prototype = Prototype(
        builder="ACF",
        model="Covered Hopper",
        nickname=None,
        purpose=Purpose.FREIGHT,
    )

    model = Model(
        manufacturer="Athearn",
        product="Genesis Covered Hopper",
    )

    control = Control(
        type=ControlType.DC,
        light=True,
        sound=False,
        smoke=False,
    )

    asset = Asset(
        status=AssetStatus.OWNED,
        source="Model Train Stuff",
        price=49.99,
        acquired=date(2026, 1, 1),
    )

    return Car(
        identity=identity,
        prototype=prototype,
        model=model,
        control=control,
        asset=asset,
        car_type=CarType.HOPPER,
    )


def test_car_creation() -> None:
    """A valid Car can be created."""

    car = create_car()

    assert isinstance(car, Car)


def test_car_components() -> None:
    """A Car contains the expected domain components."""

    car = create_car()

    assert isinstance(car.identity, Identity)
    assert isinstance(car.prototype, Prototype)
    assert isinstance(car.model, Model)
    assert isinstance(car.control, Control)
    assert isinstance(car.asset, Asset)
    assert isinstance(car.car_type, CarType)


def test_car_properties() -> None:
    """Car properties expose identity and prototype information."""

    car = create_car()

    assert car.id == "C001"
    assert car.entity_type == EntityType.CAR
    assert car.railroad == "Union Pacific"
    assert car.reporting_mark == "UP"
    assert car.road_number == "12345"
    assert car.prototype_model == "Covered Hopper"
    assert car.nickname is None


def test_car_control() -> None:
    """Car control information is preserved."""

    car = create_car()

    assert car.control.type == ControlType.DC
    assert car.control.light is True
    assert car.control.sound is False
    assert car.control.smoke is False
    assert car.control.decoder is None
    assert car.control.address == 0


def test_car_asset() -> None:
    """Car asset information is preserved."""

    car = create_car()

    assert car.asset.status == AssetStatus.OWNED
    assert car.asset.source == "Model Train Stuff"
    assert car.asset.price == 49.99
    assert car.asset.acquired == date(2026, 1, 1)


def test_car_type() -> None:
    """Car type is preserved."""

    car = create_car()

    assert car.car_type == CarType.HOPPER


def test_car_rejects_invalid_identity() -> None:
    """Car requires an Identity object."""

    car = create_car()

    with pytest.raises(TypeError):
        Car(
            identity="invalid",
            prototype=car.prototype,
            model=car.model,
            control=car.control,
            asset=car.asset,
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
            control=car.control,
            asset=car.asset,
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
            control=car.control,
            asset=car.asset,
            car_type=car.car_type,
        )


def test_car_rejects_invalid_control() -> None:
    """Car requires a Control object."""

    car = create_car()

    with pytest.raises(TypeError):
        Car(
            identity=car.identity,
            prototype=car.prototype,
            model=car.model,
            control="invalid",
            asset=car.asset,
            car_type=car.car_type,
        )


def test_car_rejects_invalid_asset() -> None:
    """Car requires an Asset object."""

    car = create_car()

    with pytest.raises(TypeError):
        Car(
            identity=car.identity,
            prototype=car.prototype,
            model=car.model,
            control=car.control,
            asset="invalid",
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
            control=car.control,
            asset=car.asset,
            car_type="hopper",
        )
