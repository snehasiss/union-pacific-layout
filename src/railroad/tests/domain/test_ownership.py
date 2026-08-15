#!/usr/bin/env python3
# test_ownership.py
#

from datetime import date

from railroad.domain.ownership import (
    Ownership,
    OwnershipStatus,
)


SHOW_TEST_OUTPUT = True


def _log(message: str) -> None:
    if SHOW_TEST_OUTPUT:
        print(f"[OwnershipTest] {message}")


def test_default_ownership():
    ownership = Ownership()

    assert ownership.status == OwnershipStatus.OWNED
    assert ownership.source is None
    assert ownership.price is None
    assert ownership.acquired is None

    _log("Default ownership validated")


def test_owned_model():
    ownership = Ownership(
        status=OwnershipStatus.OWNED,
        source="TrainWorld",
        price=299.99,
        acquired=date(2026, 8, 12),
    )

    assert ownership.status == OwnershipStatus.OWNED
    assert ownership.source == "TrainWorld"
    assert ownership.price == 299.99
    assert ownership.acquired == date(2026, 8, 12)

    _log(
        f"Owned model validated: "
        f"{ownership.source}, "
        f"${ownership.price:.2f}, "
        f"{ownership.acquired}"
    )


def test_intent_model():
    ownership = Ownership(
        status=OwnershipStatus.INTENT,
    )

    assert ownership.status == OwnershipStatus.INTENT
    assert ownership.source is None
    assert ownership.price is None
    assert ownership.acquired is None

    _log("Intent model validated")


def test_retired_model():
    ownership = Ownership(
        status=OwnershipStatus.RETIRED,
        source="eBay",
        price=250.00,
        acquired=date(2025, 5, 10),
    )

    assert ownership.status == OwnershipStatus.RETIRED
    assert ownership.source == "eBay"
    assert ownership.price == 250.00
    assert ownership.acquired == date(2025, 5, 10)

    _log("Retired model validated")


def test_source_can_be_assigned_later():
    ownership = Ownership()

    ownership.source = "Lombard Hobbies"

    assert ownership.source == "Lombard Hobbies"

    _log("Late source assignment validated")


def test_invalid_status_is_rejected():
    try:
        Ownership(status="owned")
        assert False, "status must be an OwnershipStatus."
    except TypeError:
        pass

    _log("Invalid status correctly rejected")


def test_invalid_source_is_rejected():
    try:
        Ownership(source="")
        assert False, "Empty source should be rejected."
    except ValueError:
        pass

    _log("Invalid source correctly rejected")


def test_negative_price_is_rejected():
    try:
        Ownership(price=-10.00)
        assert False, "Negative price should be rejected."
    except ValueError:
        pass

    _log("Negative price correctly rejected")


def test_invalid_price_is_rejected():
    try:
        Ownership(price="299.99")
        assert False, "Price must be numeric."
    except TypeError:
        pass

    _log("Invalid price correctly rejected")


def test_invalid_acquisition_date_is_rejected():
    try:
        Ownership(acquired="2026-08-12")
        assert False, "acquired must be a date."
    except TypeError:
        pass

    _log("Invalid acquisition date correctly rejected")

