#!/usr/bin/env python3
# test_model.py
#

from datetime import date
from dataclasses import fields

import pytest

from railroad.domain.model import Model, Scale, Status


def test_model_default_scale_is_ho():
    model = Model()
    assert model.scale == Scale.HO
    assert "scale" in {field.name for field in fields(Model)}


def test_default_model_is_stored():
    model = Model()
    assert model.status == Status.STORED
    assert model.source is None
    assert model.price is None
    assert model.acquired is None
    assert model.note is None


def test_model_can_be_created_with_complete_data():
    acquired = date(2026, 8, 1)
    model = Model(
        maker="Broadway Limited Imports",
        product="4801",
        scale=Scale.OO,
        status=Status.STORED,
        source="Broadway Limited Imports",
        price=599.99,
        acquired=acquired,
        note="Prototype-correct model",
    )

    assert model.maker == "Broadway Limited Imports"
    assert model.product == "4801"
    assert model.scale == Scale.OO
    assert model.status == Status.STORED
    assert model.source == "Broadway Limited Imports"
    assert model.price == 599.99
    assert model.acquired == acquired
    assert model.note == "Prototype-correct model"


@pytest.mark.parametrize("status", list(Status))
def test_valid_model_statuses(status):
    assert Model(status=status).status == status


def test_invalid_status():
    with pytest.raises(TypeError):
        Model(status="stored")


@pytest.mark.parametrize("scale", list(Scale))
def test_valid_model_scales(scale):
    assert Model(scale=scale).scale == scale


def test_scale_can_be_changed_from_ho_to_oo():
    model = Model()
    model.scale = Scale.OO
    assert model.scale == Scale.OO


def test_invalid_scale():
    with pytest.raises(TypeError):
        Model(scale="HO")


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
