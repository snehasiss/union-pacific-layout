#!/usr/bin/env python3
# test_car_type.py

"""
Tests for CarType.
"""

from railroad.rs.car_type import CarType


def test_car_type_contains_all_defined_types() -> None:
    """CarType contains the complete agreed classification."""

    expected = {
        "PASSENGER",
        "OBSERVATION",
        "LUGGAGE",
        "BRAKEVAN",
        "HOPPER",
        "GONDOLA",
        "WAGON",
        "TANKER",
        "FLATCAR",
        "INTERMODAL",
        "REEFER",
        "POWER",
        "PANTRY",
        "CABOOSE",
    }

    actual = {car_type.name for car_type in CarType}

    assert actual == expected


def test_car_type_values_are_lowercase_strings() -> None:
    """CarType values follow the project JSON vocabulary."""

    for car_type in CarType:
        assert isinstance(car_type.value, str)
        assert car_type.value == car_type.value.lower()


def test_car_type_is_enum() -> None:
    """CarType members are enum instances."""

    assert CarType.PASSENGER.value == "passenger"
    assert CarType.HOPPER.value == "hopper"
    assert CarType.TANKER.value == "tanker"
    assert CarType.CABOOSE.value == "caboose"
