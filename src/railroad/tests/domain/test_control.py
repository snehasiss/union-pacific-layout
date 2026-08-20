#!/usr/bin/env python3
# test_control.py
#

from datetime import date

import pytest

from railroad.domain.control import Control, ControlType


def test_default_control_is_dc():
    control = Control()

    assert control.type == ControlType.DC
    assert control.light is False
    assert control.sound is False
    assert control.smoke is False
    assert control.decoder is None
    assert control.address is None


def test_dc_control():
    control = Control(
        type=ControlType.DC,
        light=True,
        sound=False,
        smoke=False,
    )

    assert control.type == ControlType.DC
    assert control.light is True
    assert control.sound is False
    assert control.smoke is False
    assert control.decoder is None
    assert control.address is None


def test_dcc_control():
    control = Control(
        type=ControlType.DCC,
        light=True,
        sound=True,
        smoke=False,
        decoder="LokSound",
        address=4014,
    )

    assert control.type == ControlType.DCC
    assert control.light is True
    assert control.sound is True
    assert control.smoke is False
    assert control.decoder == "LokSound"
    assert control.address == 4014


def test_dcc_address_defaults_to_three():
    control = Control(
        type=ControlType.DCC,
        decoder="LokSound",
    )

    assert control.address == 3


def test_dcc_requires_decoder():
    with pytest.raises(ValueError):
        Control(type=ControlType.DCC)


def test_dc_rejects_decoder():
    with pytest.raises(ValueError):
        Control(
            type=ControlType.DC,
            decoder="LokSound",
        )


def test_dc_rejects_address():
    with pytest.raises(ValueError):
        Control(
            type=ControlType.DC,
            address=3,
        )


def test_invalid_control_type():
    with pytest.raises(TypeError):
        Control(type="dcc")


@pytest.mark.parametrize("field", ["light", "sound", "smoke"])
def test_boolean_fields_require_boolean(field):
    with pytest.raises(TypeError):
        Control(**{field: "yes"})


def test_decoder_must_be_non_empty():
    with pytest.raises(ValueError):
        Control(
            type=ControlType.DCC,
            decoder="",
        )


def test_address_must_be_integer():
    with pytest.raises(TypeError):
        Control(
            type=ControlType.DCC,
            decoder="LokSound",
            address="3",
        )


def test_address_must_be_positive():
    with pytest.raises(ValueError):
        Control(
            type=ControlType.DCC,
            decoder="LokSound",
            address=0,
        )


def test_smoke_is_independent_of_dcc():
    control = Control(
        type=ControlType.DC,
        smoke=True,
    )

    assert control.smoke is True


def test_control_type_values():
    assert ControlType.DC.value == "dc"
    assert ControlType.DCC.value == "dcc"
