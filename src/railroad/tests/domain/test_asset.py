#!/usr/bin/env python3
# test_asset.py
#

from datetime import date

import pytest

from railroad.domain.asset import Asset, AssetStatus


def test_default_asset():
    asset = Asset()

    assert asset.status == AssetStatus.OWNED
    assert asset.source is None
    assert asset.price is None
    assert asset.acquired is None


def test_owned_asset():
    acquired = date(2026, 8, 1)

    asset = Asset(
        status=AssetStatus.OWNED,
        source="Broadway Limited Imports",
        price=599.99,
        acquired=acquired,
    )

    assert asset.status == AssetStatus.OWNED
    assert asset.source == "Broadway Limited Imports"
    assert asset.price == 599.99
    assert asset.acquired == acquired


@pytest.mark.parametrize(
    "status",
    [
        AssetStatus.OWNED,
        AssetStatus.INTENT,
        AssetStatus.RETIRED,
    ],
)
def test_valid_statuses(status):
    asset = Asset(status=status)

    assert asset.status == status


def test_invalid_status():
    with pytest.raises(TypeError):
        Asset(status="owned")


def test_source_must_be_string():
    with pytest.raises(ValueError):
        Asset(source="")


def test_source_must_not_be_whitespace():
    with pytest.raises(ValueError):
        Asset(source="   ")


def test_price_must_be_numeric():
    with pytest.raises(TypeError):
        Asset(price="599.99")


def test_price_cannot_be_negative():
    with pytest.raises(ValueError):
        Asset(price=-1)


def test_acquired_must_be_date():
    with pytest.raises(TypeError):
        Asset(acquired="2026-08-01")

