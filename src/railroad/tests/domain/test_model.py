#!/usr/bin/env python3
# test_model.py
#

from datetime import date
from dataclasses import fields

import pytest

from railroad.domain.model import Model, ModelStatus


def test_model_scale_is_ho():
    model = Model()
    assert Model.SCALE == "HO"
    assert model.SCALE == "HO"


def test_scale_is_class_constant():
    field_names = {field.name for field in fields(Model())}
    assert "SCALE" not in field_names


def test_default_model_is_stored():
    model = Model()
    assert model.status == ModelStatus.STORED
    assert model.source is None
    assert model.price is None
    assert model.acquired is None
    assert model.note is None


def test_model_can_be_created_with_complete_data():
    acquired = date(2026, 8, 1)
    model = Model(
        maker="Broadway Limited Imports",
        product="4801",
        status=ModelStatus.STORED,
        source="Broadway Limited Imports",
        price=599.99,
        acquired=acquired,
        note="Prototype-correct model",
    )

    assert model.maker == "Broadway Limited Imports"
    assert model.product == "4801"
    assert model.status == ModelStatus.STORED
    assert model.source == "Broadway Limited Imports"
    assert model.price == 599.99
    assert model.acquired == acquired
    assert model.note == "Prototype-correct model"


@pytest.mark.parametrize(
    "status",
    [
        ModelStatus.INTENT,
        ModelStatus.SPOTTED,
        ModelStatus.SHIPPED,
        ModelStatus.STORED,
        ModelStatus.ACTIVE,
        ModelStatus.REPAIR,
        ModelStatus.RETIRED,
    ],
)
def test_valid_model_statuses(status):
    assert Model(status=status).status == status


def test_invalid_status():
    with pytest.raises(TypeError):
        Model(status="stored")


def test_invalid_maker():
    with pytest.raises(ValueError):
        Model(maker="")


def test_invalid_product():
    with pytest.raises(ValueError):
        Model(product="")


def test_invalid_source():
    with pytest.raises(ValueError):
        Model(source="")


def test_invalid_price():
    with pytest.raises(ValueError):
        Model(price=-1)


def test_invalid_acquired():
    with pytest.raises(TypeError):
        Model(acquired="2026-08-01")


def test_invalid_note():
    with pytest.raises(TypeError):
        Model(note=123)
