#!/usr/bin/env python3
# test_prototype.py
#

from railroad.domain.prototype import Prototype
from railroad.domain.prototype import Purpose


SHOW_TEST_OUTPUT = True


def _log(message: str) -> None:
    if SHOW_TEST_OUTPUT:
        print(f"[PrototypeTest] {message}")


def test_create_steam_prototype():
    prototype = Prototype(
        builder="ALCO",
        model="4-8-8-4",
        nickname="Big Boy",
        purpose=Purpose.FREIGHT,
    )

    assert prototype.builder == "ALCO"
    assert prototype.model == "4-8-8-4"
    assert prototype.nickname == "Big Boy"
    assert prototype.purpose == Purpose.FREIGHT

    _log(f"Steam prototype created: {prototype}")


def test_create_diesel_prototype():
    prototype = Prototype(
        builder="EMD",
        model="SD90MAC",
        nickname=None,
        purpose=Purpose.FREIGHT,
    )

    assert prototype.builder == "EMD"
    assert prototype.model == "SD90MAC"
    assert prototype.nickname is None
    assert prototype.purpose == Purpose.FREIGHT

    _log(f"Diesel prototype created: {prototype}")


def test_create_turbine_prototype():
    prototype = Prototype(
        builder="GE",
        model="GTEL8500",
        nickname="Big Blow",
        purpose=Purpose.FREIGHT,
    )

    assert prototype.builder == "GE"
    assert prototype.model == "GTEL8500"
    assert prototype.nickname is "Big Blow"
    assert prototype.purpose == Purpose.FREIGHT

    _log(f"Diesel prototype created: {prototype}")


def test_purpose_values():
    assert Purpose.PASSENGER.value == "passenger"
    assert Purpose.FREIGHT.value == "freight"
    assert Purpose.SWITCHER.value == "switcher"
    assert Purpose.LOGGER.value == "logger"
    assert Purpose.MACHINE.value == "machine"
    assert Purpose.SPECIAL.value == "special"

    _log("Purpose enum values validated")


def test_purpose_is_enum():
    prototype = Prototype(
        builder="EMD",
        model="GP30",
        nickname=None,
        purpose=Purpose.SWITCHER,
    )

    assert isinstance(prototype.purpose, Purpose)

    _log(
        f"Purpose enum validated: "
        f"{prototype.model} -> {prototype.purpose.value}"
    )


def test_nickname_is_optional():
    prototype = Prototype(
        builder="EMD",
        model="GP30",
        nickname=None,
        purpose=Purpose.SWITCHER,
    )

    assert prototype.nickname is None

    _log("Optional nickname validated")


def test_invalid_builder_is_rejected():
    try:
        Prototype(
            builder="",
            model="4-8-8-4",
            nickname="Big Boy",
            purpose=Purpose.FREIGHT,
        )
        assert False, "Empty builder should be rejected."
    except ValueError:
        pass

    _log("Invalid builder correctly rejected")


def test_invalid_model_is_rejected():
    try:
        Prototype(
            builder="ALCO",
            model="",
            nickname="Big Boy",
            purpose=Purpose.FREIGHT,
        )
        assert False, "Empty model should be rejected."
    except ValueError:
        pass

    _log("Invalid model correctly rejected")


def test_invalid_nickname_is_rejected():
    try:
        Prototype(
            builder="ALCO",
            model="4-8-8-4",
            nickname="",
            purpose=Purpose.FREIGHT,
        )
        assert False, "Empty nickname should be rejected."
    except ValueError:
        pass

    _log("Invalid nickname correctly rejected")


def test_invalid_purpose_is_rejected():
    try:
        Prototype(
            builder="ALCO",
            model="4-8-8-4",
            nickname="Big Boy",
            purpose="freight",
        )
        assert False, "Purpose string should be rejected."
    except TypeError:
        pass

    _log("Invalid purpose correctly rejected")


def test_prototype_is_immutable():
    prototype = Prototype(
        builder="ALCO",
        model="4-8-8-4",
        nickname="Big Boy",
        purpose=Purpose.FREIGHT,
    )

    try:
        prototype.model = "4-6-6-4"
        assert False, "Prototype should be immutable."
    except AttributeError:
        pass

    _log("Prototype immutability validated")

