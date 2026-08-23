#!/usr/bin/env python3
# railroad/tests/rs/test_mow.py

from __future__ import annotations
from datetime import date
import pytest
from railroad.domain.asset import Asset, AssetStatus
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.mow import MOW, MOWType


def create_mow() -> MOW:
    return MOW(
        identity=Identity(id="M001", entity_type=EntityType.MOW, railroad="Union Pacific", reporting_mark="UP", road_number="100"),
        prototype=Prototype(builder="Plasser & Theurer", model="Tamper", nickname=None, purpose=Purpose.FREIGHT),
        model=Model(maker="Kibri", product="MOW Tamper"),
        control=Control(type=ControlType.DC, light=True, sound=False, smoke=False),
        asset=Asset(status=AssetStatus.OWNED, source="Model Train Stuff", price=89.99, acquired=date(2026, 1, 1)),
        mow_type=MOWType.TAMPER,
        self_propelled=True,
    )


def test_mow_creation():
    assert isinstance(create_mow(), MOW)


def test_mow_components():
    mow = create_mow()
    assert isinstance(mow.identity, Identity)
    assert isinstance(mow.prototype, Prototype)
    assert isinstance(mow.model, Model)
    assert isinstance(mow.control, Control)
    assert isinstance(mow.asset, Asset)
    assert isinstance(mow.mow_type, MOWType)


def test_mow_properties():
    mow = create_mow()
    assert (mow.id, mow.entity_type, mow.railroad, mow.reporting_mark, mow.road_number) == ("M001", EntityType.MOW, "Union Pacific", "UP", "100")
    assert mow.prototype_model == "Tamper"
    assert mow.nickname is None


def test_mow_control():
    mow = create_mow()
    assert mow.control.type == ControlType.DC
    assert mow.control.light is True
    assert mow.control.sound is False
    assert mow.control.smoke is False
    assert mow.control.decoder is None
    assert mow.control.address == 0


def test_mow_asset():
    mow = create_mow()
    assert mow.asset.status == AssetStatus.OWNED
    assert mow.asset.source == "Model Train Stuff"
    assert mow.asset.price == 89.99
    assert mow.asset.acquired == date(2026, 1, 1)


def test_mow_type():
    mow = create_mow()
    assert mow.mow_type == MOWType.TAMPER
    assert mow.self_propelled is True


def test_mow_rejects_invalid_identity():
    mow = create_mow()
    with pytest.raises(TypeError):
        MOW("invalid", mow.prototype, mow.model, mow.control, mow.asset, mow.mow_type, mow.self_propelled)


def test_mow_rejects_invalid_prototype():
    mow = create_mow()
    with pytest.raises(TypeError):
        MOW(mow.identity, "invalid", mow.model, mow.control, mow.asset, mow.mow_type, mow.self_propelled)


def test_mow_rejects_invalid_model():
    mow = create_mow()
    with pytest.raises(TypeError):
        MOW(mow.identity, mow.prototype, "invalid", mow.control, mow.asset, mow.mow_type, mow.self_propelled)


def test_mow_rejects_invalid_control():
    mow = create_mow()
    with pytest.raises(TypeError):
        MOW(mow.identity, mow.prototype, mow.model, "invalid", mow.asset, mow.mow_type, mow.self_propelled)


def test_mow_rejects_invalid_asset():
    mow = create_mow()
    with pytest.raises(TypeError):
        MOW(mow.identity, mow.prototype, mow.model, mow.control, "invalid", mow.mow_type, mow.self_propelled)


def test_mow_rejects_invalid_mow_type():
    mow = create_mow()
    with pytest.raises(TypeError):
        MOW(mow.identity, mow.prototype, mow.model, mow.control, mow.asset, "tamper", mow.self_propelled)


def test_mow_rejects_invalid_self_propelled():
    mow = create_mow()
    with pytest.raises(TypeError):
        MOW(mow.identity, mow.prototype, mow.model, mow.control, mow.asset, mow.mow_type, "yes")
