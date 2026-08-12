#!/usr/bin/env python3
# test_model.py
#

from dataclasses import fields

from src.railroad.domain.model import Model


SHOW_TEST_OUTPUT = True


def _log(message: str) -> None:
    if SHOW_TEST_OUTPUT:
        print(f"[ModelTest] {message}")


def test_model_scale_is_ho():
    model = Model()

    assert Model.SCALE == "HO"
    assert model.SCALE == "HO"

    _log(f"Model scale validated: {Model.SCALE}")


def test_scale_is_class_constant():
    model = Model()

    field_names = {field.name for field in fields(model)}

    assert "SCALE" not in field_names

    _log("SCALE correctly excluded from dataclass instance fields")


def test_model_can_be_created_without_manufacturer_or_product():
    model = Model()

    assert model.manufacturer is None
    assert model.product is None

    _log("Model created with no manufacturer/product")


def test_manufacturer_and_product_can_be_assigned_later():
    model = Model()

    model.manufacturer = "Athearn"
    model.product = "Genesis Big Boy"

    assert model.manufacturer == "Athearn"
    assert model.product == "Genesis Big Boy"

    _log(
        f"Late assignment validated: "
        f"{model.manufacturer} / {model.product}"
    )


def test_manufacturer_can_be_assigned_at_creation():
    model = Model(
        manufacturer="Broadway Limited Imports",
        product="4801",
    )

    assert model.manufacturer == "Broadway Limited Imports"
    assert model.product == "4801"

    _log(f"Model created with source data: {model}")


def test_scale_cannot_be_changed():
    model = Model()

    try:
        model.SCALE = "N"
        assert True, "SCALE should not be assignable."
    except AttributeError:
        pass

    assert Model.SCALE == "HO"

    _log("SCALE immutability validated")


def test_invalid_manufacturer_is_rejected():
    try:
        Model(manufacturer="")
        assert False, "Empty manufacturer should be rejected."
    except ValueError:
        pass

    _log("Invalid manufacturer correctly rejected")


def test_invalid_product_is_rejected():
    try:
        Model(product="")
        assert False, "Empty product should be rejected."
    except ValueError:
        pass

    _log("Invalid product correctly rejected")


def test_json_scale_source_is_available():
    """
    Verify that the serializer will have access to the project scale.

    Persistence will later explicitly serialize Model.SCALE as
    the JSON 'scale' property.
    """

    model = Model(
        manufacturer="Athearn",
        product="Genesis Big Boy",
    )

    assert model.SCALE == "HO"

    _log(
        f"JSON scale source validated: "
        f'"scale": "{model.SCALE}"'
    )

