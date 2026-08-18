#!/usr/bin/env python3
# test_mow_type.py

"""
Tests for MOWType.
"""

from railroad.rs.mow_type import MOWType


def test_mow_type_contains_all_defined_types() -> None:
    """MOWType contains the complete agreed classification."""

    expected = {
        "CRANE",
        "SNOWPLOW",
        "CLEANER",
        "TAMPER",
        "MPV",
    }

    actual = {mow_type.name for mow_type in MOWType}

    assert actual == expected


def test_mow_type_values_are_lowercase_strings() -> None:
    """MOWType values follow the project JSON vocabulary."""

    for mow_type in MOWType:
        assert isinstance(mow_type.value, str)
        assert mow_type.value == mow_type.value.lower()


def test_mow_type_is_enum() -> None:
    """MOWType members have the expected values."""

    assert MOWType.CRANE.value == "crane"
    assert MOWType.SNOWPLOW.value == "snowplow"
    assert MOWType.CLEANER.value == "cleaner"
    assert MOWType.TAMPER.value == "tamper"
    assert MOWType.MPV.value == "mpv"

