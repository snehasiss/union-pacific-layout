#!/usr/bin/env python3
# test_loco_type.py

"""
Tests for LocoType.
"""

from railroad.rs.loco_type import LocoType


def test_loco_type_steam() -> None:
    """Steam is a valid locomotive type."""

    assert LocoType.STEAM.value == "steam"


def test_loco_type_diesel() -> None:
    """Diesel is a valid locomotive type."""

    assert LocoType.DIESEL.value == "diesel"


def test_loco_type_turbine() -> None:
    """Diesel is a valid locomotive type."""

    assert LocoType.TURBINE.value == "turbine"
