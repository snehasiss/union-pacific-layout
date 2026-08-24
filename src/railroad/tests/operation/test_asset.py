#!/usr/bin/env python3
# test_asset.py

from __future__ import annotations

import pytest

from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model, Status
from railroad.domain.prototype import Prototype, Purpose
from railroad.operation.asset import Asset
from railroad.rs.loco import Loco, LocoType


class FakeDAO:
    def __init__(self):
        self.objects = {}

    def get(self, entity_id):
        if entity_id not in self.objects:
            raise FileNotFoundError(entity_id)
        return self.objects[entity_id]

    def save(self, obj):
        self.objects[obj.id] = obj

    def next_id(self):
        return "L001"


def make_loco(identity: Identity | None = None, status: Status = Status.STORED) -> Loco:
    identity = identity or Identity(id="L001", entity_type=EntityType.LOCO, railroad="Union Pacific", reporting_mark="UP", road_number="4014")
    return Loco(
        identity=identity,
        loco_type=LocoType.STEAM,
        prototype=Prototype(builder="ALCo", model="4-8-8-4", nickname="Big Boy", purpose=Purpose.FREIGHT),
        model=Model(maker="Athearn", product="Genesis Big Boy", status=status),
        control=Control(type=ControlType.DCC, light=True, sound=True, smoke=False, decoder="Paragon4", address=4014),
    )


def make_ops():
    dao = FakeDAO()
    return Asset(None, dao_factory=lambda entity_type, config: dao), dao


def test_view_returns_domain_object():
    ops, dao = make_ops()
    loco = make_loco()
    dao.save(loco)
    assert ops.view("L001").object is loco


def test_view_can_return_retired_object():
    ops, dao = make_ops()
    loco = make_loco(status=Status.RETIRED)
    dao.save(loco)
    assert ops.view("L001").model.status == Status.RETIRED


def test_view_rejects_object_with_a_type_mismatched_to_its_id():
    ops, dao = make_ops()
    mismatched_identity = Identity(id="C001", entity_type=EntityType.CAR, railroad="Union Pacific", reporting_mark="UP", road_number="4014")
    dao.objects["L001"] = make_loco(mismatched_identity)
    with pytest.raises(ValueError, match="EntityType.LOCO"):
        ops.view("L001")


def test_view_rejects_unbound_prefix():
    ops, _ = make_ops()
    with pytest.raises(ValueError):
        ops.view("X001")


def test_update_persists_same_object():
    ops, dao = make_ops()
    loco = make_loco()
    dao.save(loco)
    asset = ops.view("L001")
    asset.model.note = "updated"
    assert asset.update().model.note == "updated"
    assert dao.objects["L001"].model.note == "updated"


def test_retire_updates_model_status():
    ops, dao = make_ops()
    loco = make_loco()
    dao.save(loco)
    result = ops.view("L001").retire()
    assert result.model.status == Status.RETIRED
    assert dao.objects["L001"].model.status == Status.RETIRED


def test_unbound_asset_cannot_persist_or_retire():
    ops, _ = make_ops()
    with pytest.raises(RuntimeError):
        ops.update()
    with pytest.raises(RuntimeError):
        ops.retire()


def test_create_allocates_id_and_saves():
    ops, dao = make_ops()

    def builder(identity):
        return make_loco(identity)

    result = ops.create(EntityType.LOCO, builder, railroad="Union Pacific", reporting_mark="UP", road_number="4014")
    assert result.id == "L001"
    assert dao.objects["L001"] is result.object
