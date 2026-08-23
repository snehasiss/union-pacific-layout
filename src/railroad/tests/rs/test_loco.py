#!/usr/bin/env python3
# railroad/tests/rs/test_loco.py

import pytest

from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.loco import Loco, LocoType


def make_identity() -> Identity:
    return Identity(id="L001", entity_type=EntityType.LOCO, railroad="Union Pacific", reporting_mark="UP", road_number="4014")


def make_prototype() -> Prototype:
    return Prototype(builder="ALCo", model="4-8-8-4", nickname="Big Boy", purpose=Purpose.FREIGHT)


def make_model() -> Model:
    return Model(maker="Athearn", product="Genesis Big Boy", status=Status.STORED, source="Model Train Stuff", price=599.99)


def make_control() -> Control:
    return Control(type=ControlType.DCC, light=True, sound=True, smoke=False, decoder="Paragon4", address=4014)


def make_loco() -> Loco:
    return Loco(identity=make_identity(), loco_type=LocoType.STEAM, prototype=make_prototype(), model=make_model(), control=make_control())


def test_loco_creation():
    assert isinstance(make_loco(), Loco)


def test_loco_identity_properties():
    loco = make_loco()
    assert loco.id == "L001"
    assert loco.entity_type == EntityType.LOCO
    assert loco.railroad == "Union Pacific"
    assert loco.reporting_mark == "UP"
    assert loco.road_number == "4014"


def test_loco_prototype_properties():
    loco = make_loco()
    assert loco.prototype_model == "4-8-8-4"
    assert loco.nickname == "Big Boy"


def test_loco_components():
    loco = make_loco()
    assert isinstance(loco.identity, Identity)
    assert isinstance(loco.prototype, Prototype)
    assert isinstance(loco.model, Model)
    assert isinstance(loco.control, Control)


def test_loco_control():
    loco = make_loco()
    assert loco.control.type == ControlType.DCC
    assert loco.control.decoder == "Paragon4"
    assert loco.control.address == 4014


def test_loco_model():
    loco = make_loco()
    assert loco.model.maker == "Athearn"
    assert loco.model.product == "Genesis Big Boy"
    assert loco.model.status == Status.STORED


def test_loco_accepts_diesel():
    loco = make_loco()
    loco.loco_type = LocoType.DIESEL
    assert loco.loco_type == LocoType.DIESEL


def test_loco_accepts_turbine():
    loco = make_loco()
    loco.loco_type = LocoType.TURBINE
    assert loco.loco_type == LocoType.TURBINE


def test_loco_accepts_missing_nickname():
    prototype = Prototype(builder="EMD", model="SD40-2", nickname=None, purpose=Purpose.FREIGHT)
    loco = Loco(identity=make_identity(), loco_type=LocoType.DIESEL, prototype=prototype, model=make_model(), control=make_control())
    assert loco.nickname is None


def test_loco_rejects_invalid_identity():
    with pytest.raises(TypeError):
        Loco(identity="L001", loco_type=LocoType.STEAM, prototype=make_prototype(), model=make_model(), control=make_control())


def test_loco_rejects_invalid_loco_type():
    with pytest.raises(TypeError):
        Loco(identity=make_identity(), loco_type="steam", prototype=make_prototype(), model=make_model(), control=make_control())


def test_loco_rejects_invalid_prototype():
    with pytest.raises(TypeError):
        Loco(identity=make_identity(), loco_type=LocoType.STEAM, prototype="prototype", model=make_model(), control=make_control())


def test_loco_rejects_invalid_model():
    with pytest.raises(TypeError):
        Loco(identity=make_identity(), loco_type=LocoType.STEAM, prototype=make_prototype(), model="model", control=make_control())


def test_loco_rejects_invalid_control():
    with pytest.raises(TypeError):
        Loco(identity=make_identity(), loco_type=LocoType.STEAM, prototype=make_prototype(), model=make_model(), control="control")
