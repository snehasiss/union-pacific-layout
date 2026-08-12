#!/usr/bin/env python3
# test_identity.py
# 

from src.railroad.domain.identity import Identity
from src.railroad.domain.identity import IdGenerator


SHOW_TEST_OUTPUT = True


def _log(message: str) -> None:
    if SHOW_TEST_OUTPUT:
        print(f"[IdentityTest] {message}")


def test_create_generates_id():
    identity = Identity.create(
        prefix="L",
        entity_type="steam",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=4014,
    )

    assert identity.id.startswith("L")
    assert len(identity.id) == 4

    _log(
        f"Created identity: {identity.id} "
        f"({identity.entity_type}, "
        f"{identity.reporting_mark} {identity.road_number})"
    )


def test_identity_contains_all_fields():
    identity = Identity.create(
        prefix="L",
        entity_type="steam",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=4014,
    )

    assert identity.entity_type == "steam"
    assert identity.railroad == "Union Pacific"
    assert identity.reporting_mark == "UP"
    assert identity.road_number == 4014

    _log(f"Identity fields validated: {identity}")


def test_generated_ids_are_sequential():
    first = Identity.create(
        prefix="L",
        entity_type="steam",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=4014,
    )

    second = Identity.create(
        prefix="L",
        entity_type="diesel",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=7082,
    )

    first_number = int(first.id[1:])
    second_number = int(second.id[1:])

    assert second_number == first_number + 1

    _log(f"Sequential IDs validated: {first.id} -> {second.id}")


def test_different_entity_namespaces_are_independent():
    locomotive = Identity.create(
        prefix="L",
        entity_type="steam",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=844,
    )

    car = Identity.create(
        prefix="C",
        entity_type="hopper",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=123456,
    )

    assert locomotive.id.startswith("L")
    assert car.id.startswith("C")

    _log(
        f"Independent namespaces validated: "
        f"{locomotive.id}, {car.id}"
    )


def test_existing_identity_retains_id():
    identity = Identity.from_existing(
        id="L100",
        entity_type="steam",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=4014,
    )

    assert identity.id == "L100"

    _log(f"Existing identity retained: {identity.id}")


def test_existing_id_advances_generator():
    Identity.from_existing(
        id="L200",
        entity_type="steam",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=4014,
    )

    identity = Identity.create(
        prefix="L",
        entity_type="diesel",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=7082,
    )

    assert identity.id == "L201"

    _log(f"Generator advanced correctly: {identity.id}")


def test_identity_is_immutable():
    identity = Identity.from_existing(
        id="L300",
        entity_type="steam",
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=4014,
    )

    try:
        identity.id = "L301"
        assert False, "Identity should be immutable."
    except AttributeError:
        pass

    _log("Identity immutability validated")


def test_invalid_id_is_rejected():
    try:
        Identity.from_existing(
            id="X0001",
            entity_type="steam",
            railroad="Union Pacific",
            reporting_mark="UP",
            road_number=4014,
        )
        assert False, "Invalid ID should be rejected."
    except ValueError:
        pass

    _log("Invalid ID correctly rejected")


def test_maximum_id_is_three_digits():
    assert IdGenerator.MAX_NUMBER == 999
    assert IdGenerator.MIN_DIGITS == 3

    _log("ID range validated: L001 through L999")

