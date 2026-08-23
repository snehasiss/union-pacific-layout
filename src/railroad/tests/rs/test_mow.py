#!/usr/bin/env python3
#
# railroad/tests/rs/test_mow.py
#

"""
Tests for the Maintenance-of-Way domain entity.
"""

from __future__ import annotations

from datetime import date

import pytest

from railroad.domain.asset import Asset, AssetStatus
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.mow import MOW
from railroad.rs.mow_type import MOWType


def create_mow() -> MOW:
    """Create a valid MOW asset for testing."""

    identity = Identity(
        id="M001",
        entity_type=EntityType.MOW,
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number="100",
    )

    prototype = Prototype(
        builder="Plasser & Theurer",
        model="Tamper",
        nickname=None,
        purpose=Purpose.FREIGHT,
    )

    model = Model(
        maker="Kibri",
        product="MOW Tamper",
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
        price=89.99,
        acquired=date(2026, 1, 1),
    )

    return MOW(
        identity=identity,
        prototype=prototype,
        model=model,
        control=control,
        asset=asset,
        mow_type=MOWType.TAMPER,
        self_propelled=True,
    )


def test_mow_creation() -> None:
    """A valid MOW asset can be created."""

    mow = create_mow()

    assert isinstance(mow, MOW)


def test_mow_components() -> None:
    """An MOW asset contains the expected domain components."""

    mow = create_mow()

    assert isinstance(mow.identity, Identity)
    assert isinstance(mow.prototype, Prototype)
    assert isinstance(mow.model, Model)
    assert isinstance(mow.control, Control)
    assert isinstance(mow.asset, Asset)
    assert isinstance(mow.mow_type, MOWType)


def test_mow_properties() -> None:
    """MOW properties expose identity and prototype information."""

    mow = create_mow()

    assert mow.id == "M001"
    assert mow.entity_type == EntityType.MOW
    assert mow.railroad == "Union Pacific"
    assert mow.reporting_mark == "UP"
    assert mow.road_number == "100"
    assert mow.prototype_model == "Tamper"
    assert mow.nickname is None


def test_mow_control() -> None:
    """MOW control information is preserved."""

    mow = create_mow()

    assert mow.control.type == ControlType.DC
    assert mow.control.light is True
    assert mow.control.sound is False
    assert mow.control.smoke is False
    assert mow.control.decoder is None
    assert mow.control.address == 0


def test_mow_asset() -> None:
    """MOW asset information is preserved."""

    mow = create_mow()

    assert mow.asset.status == AssetStatus.OWNED
    assert mow.asset.source == "Model Train Stuff"
    assert mow.asset.price == 89.99
    assert mow.asset.acquired == date(2026, 1, 1)


def test_mow_type() -> None:
    """MOW type is preserved."""

    mow = create_mow()

    assert mow.mow_type == MOWType.TAMPER
    assert mow.self_propelled is True


def test_mow_rejects_invalid_identity() -> None:
    """MOW requires an Identity object."""

    mow = create_mow()

    with pytest.raises(TypeError):
        MOW(
            identity="invalid",
            prototype=mow.prototype,
            model=mow.model,
            control=mow.control,
            asset=mow.asset,
            mow_type=mow.mow_type,
            self_propelled=mow.self_propelled,
        )


def test_mow_rejects_invalid_prototype() -> None:
    """MOW requires a Prototype object."""

    mow = create_mow()

    with pytest.raises(TypeError):
        MOW(
            identity=mow.identity,
            prototype="invalid",
            model=mow.model,
            control=mow.control,
            asset=mow.asset,
            mow_type=mow.mow_type,
            self_propelled=mow.self_propelled,
        )


def test_mow_rejects_invalid_model() -> None:
    """MOW requires a Model object."""

    mow = create_mow()

    with pytest.raises(TypeError):
        MOW(
            identity=mow.identity,
            prototype=mow.prototype,
            model="invalid",
            control=mow.control,
            asset=mow.asset,
            mow_type=mow.mow_type,
            self_propelled=mow.self_propelled,
        )


def test_mow_rejects_invalid_control() -> None:
    """MOW requires a Control object."""

    mow = create_mow()

    with pytest.raises(TypeError):
        MOW(
            identity=mow.identity,
            prototype=mow.prototype,
            model=mow.model,
            control="invalid",
            asset=mow.asset,
            mow_type=mow.mow_type,
            self_propelled=mow.self_propelled,
        )


def test_mow_rejects_invalid_asset() -> None:
    """MOW requires an Asset object."""

    mow = create_mow()

    with pytest.raises(TypeError):
        MOW(
            identity=mow.identity,
            prototype=mow.prototype,
            model=mow.model,
            control=mow.control,
            asset="invalid",
            mow_type=mow.mow_type,
            self_propelled=mow.self_propelled,
        )


def test_mow_rejects_invalid_mow_type() -> None:
    """MOW requires an MOWType."""

    mow = create_mow()

    with pytest.raises(TypeError):
        MOW(
            identity=mow.identity,
            prototype=mow.prototype,
            model=mow.model,
            control=mow.control,
            asset=mow.asset,
            mow_type="tamper",
            self_propelled=mow.self_propelled,
        )


def test_mow_rejects_invalid_self_propelled() -> None:
    """MOW requires a boolean self_propelled value."""

    mow = create_mow()

    with pytest.raises(TypeError):
        MOW(
            identity=mow.identity,
            prototype=mow.prototype,
            model=mow.model,
            control=mow.control,
            asset=mow.asset,
            mow_type=mow.mow_type,
            self_propelled="yes",
        )
