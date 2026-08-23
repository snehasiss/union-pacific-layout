#!/usr/bin/env python3
# railroad/tests/rs/test_car.py

from __future__ import annotations

import pytest

from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.car import Car, CarType


def create_car() -> Car:
    return Car(
        identity=Identity(id="C001", entity_type=EntityType.CAR, railroad="Union Pacific", reporting_mark="UP", road_number="12345"),
        prototype=Prototype(builder="ACF", model="Covered Hopper", nickname=None, purpose=Purpose.FREIGHT),
        model=Model(maker="Athearn", product="Genesis Covered Hopper"),
        control=Control(type=ControlType.DC, light=True, sound=False, smoke=False),
        car_type=CarType.HOPPER,
    )


def test_car_creation():
    assert isinstance(create_car(), Car)


def test_car_components():
    car = create_car()
    assert isinstance(car.identity, Identity)
    assert isinstance(car.prototype, Prototype)
    assert isinstance(car.model, Model)
    assert isinstance(car.control, Control)
    assert isinstance(car.car_type, CarType)


def test_car_properties():
    car = create_car()
    assert (car.id, car.entity_type, car.railroad, car.reporting_mark, car.road_number) == ("C001", EntityType.CAR, "Union Pacific", "UP", "12345")
    assert car.prototype_model == "Covered Hopper"
    assert car.nickname is None


def test_car_control():
    car = create_car()
    assert car.control.type == ControlType.DC
    assert car.control.light is True
    assert car.control.sound is False
    assert car.control.smoke is False
    assert car.control.decoder is None
    assert car.control.address == 0


def test_car_type():
    assert create_car().car_type == CarType.HOPPER


def test_car_rejects_invalid_identity():
    car = create_car()
    with pytest.raises(TypeError):
        Car("invalid", car.prototype, car.model, car.control, car.car_type)


def test_car_rejects_invalid_prototype():
    car = create_car()
    with pytest.raises(TypeError):
        Car(car.identity, "invalid", car.model, car.control, car.car_type)


def test_car_rejects_invalid_model():
    car = create_car()
    with pytest.raises(TypeError):
        Car(car.identity, car.prototype, "invalid", car.control, car.car_type)


def test_car_rejects_invalid_control():
    car = create_car()
    with pytest.raises(TypeError):
        Car(car.identity, car.prototype, car.model, "invalid", car.car_type)


def test_car_rejects_invalid_car_type():
    car = create_car()
    with pytest.raises(TypeError):
        Car(car.identity, car.prototype, car.model, car.control, "hopper")
