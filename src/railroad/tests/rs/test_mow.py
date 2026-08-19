#!/usr/bin/env python3
# test_mow.py

"""
Tests for the MOW domain entity.
"""

import pytest

from railroad.domain.electronics import Electronics
from railroad.domain.identity import Identity, EntityType
from railroad.domain.model import Model
from railroad.domain.ownership import Ownership, OwnershipStatus
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.mow import MOW
from railroad.rs.mow_type import MOWType


def create_mow(
    road_number: int = 100,
    mow_type: MOWType = MOWType.TAMPER,
    self_propelled: bool = True,
) -> MOW:
    """Create a representative MOW asset for testing."""

    identity = Identity.create(
        prefix="M",
        entity_type=EntityType.MOW,
        railroad="Union Pacific",
        reporting_mark="UP",
        road_number=road_number,
    )

    prototype = Prototype(
        builder="Plasser",
        model="Tamper",
        nickname=None,
        purpose=Purpose.MACHINE,
    )

    model = Model(
        manufacturer="Plasser",
        product="Tamper",
    )

    electronics = Electronics(
        dcc=True,
        decoder="LokSound",
        sound=True,
    )

    ownership = Ownership(
        status=OwnershipStatus.OWNED,
    )

    return MOW(
        identity=identity,
        prototype=prototype,
        model=model,
        electronics=electronics,
        ownership=ownership,
        mow_type=mow_type,
        self_propelled=self_propelled,
    )


def test_mow_can_be_created() -> None:
    """An MOW asset can be constructed."""

    mow = create_mow()

    assert isinstance(mow, MOW)


def test_mow_contains_domain_components() -> None:
    """An MOW asset contains all required domain components."""

    mow = create_mow()

    assert isinstance(mow.identity, Identity)
    assert isinstance(mow.prototype, Prototype)
    assert isinstance(mow.model, Model)
    assert isinstance(mow.electronics, Electronics)
    assert isinstance(mow.ownership, Ownership)
    assert isinstance(mow.mow_type, MOWType)


def test_mow_identity_properties() -> None:
    """Identity information is exposed through MOW."""

    mow = create_mow(road_number=123)

    assert mow.id.startswith("M")
    assert mow.entity_type == EntityType.MOW
    assert mow.railroad == "Union Pacific"
    assert mow.reporting_mark == "UP"
    assert mow.road_number == 123


def test_mow_prototype_properties() -> None:
    """Prototype information is exposed through MOW."""

    mow = create_mow()

    assert mow.prototype_model == "Tamper"
    assert mow.nickname is None


def test_mow_type() -> None:
    """MOW exposes its MOWType."""

    mow = create_mow(mow_type=MOWType.MPV)

    assert mow.mow_type is MOWType.MPV


def test_self_propelled() -> None:
    """Self-propelled capability is represented correctly."""

    powered = create_mow(self_propelled=True)
    unpowered = create_mow(
        road_number=200,
        mow_type=MOWType.CRANE,
        self_propelled=False,
    )

    assert powered.self_propelled is True
    assert unpowered.self_propelled is False


def test_mow_rejects_invalid_identity() -> None:
    """MOW requires an Identity object."""

    mow = create_mow()

    with pytest.raises(TypeError):
        MOW(
            identity="invalid",
            prototype=mow.prototype,
            model=mow.model,
            electronics=mow.electronics,
            ownership=mow.ownership,
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
            electronics=mow.electronics,
            ownership=mow.ownership,
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
            electronics=mow.electronics,
            ownership=mow.ownership,
            mow_type=mow.mow_type,
            self_propelled=mow.self_propelled,
        )


def test_mow_rejects_invalid_electronics() -> None:
    """MOW requires an Electronics object."""

    mow = create_mow()

    with pytest.raises(TypeError):
        MOW(
            identity=mow.identity,
            prototype=mow.prototype,
            model=mow.model,
            electronics="invalid",
            ownership=mow.ownership,
            mow_type=mow.mow_type,
            self_propelled=mow.self_propelled,
        )


def test_mow_rejects_invalid_ownership() -> None:
    """MOW requires an Ownership object."""

    mow = create_mow()

    with pytest.raises(TypeError):
        MOW(
            identity=mow.identity,
            prototype=mow.prototype,
            model=mow.model,
            electronics=mow.electronics,
            ownership="invalid",
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
            electronics=mow.electronics,
            ownership=mow.ownership,
            mow_type="tamper",
            self_propelled=mow.self_propelled,
        )


def test_mow_rejects_invalid_self_propelled() -> None:
    """MOW requires self_propelled to be a bool."""

    mow = create_mow()

    with pytest.raises(TypeError):
        MOW(
            identity=mow.identity,
            prototype=mow.prototype,
            model=mow.model,
            electronics=mow.electronics,
            ownership=mow.ownership,
            mow_type=mow.mow_type,
            self_propelled="true",
        )

