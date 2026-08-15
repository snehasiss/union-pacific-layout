#!/usr/bin/env python3
# test_electronics.py
#

from railroad.domain.electronics import Electronics


SHOW_TEST_OUTPUT = True


def _log(message: str) -> None:
    if SHOW_TEST_OUTPUT:
        print(f"[ElectronicsTest] {message}")


def test_default_non_dcc_electronics():
    electronics = Electronics()

    assert electronics.dcc is False
    assert electronics.decoder is None
    assert electronics.address is None
    assert electronics.sound is False
    assert electronics.light is False

    _log("Default non-DCC electronics validated")


def test_dcc_electronics_defaults_to_address_3():
    electronics = Electronics(
        dcc=True,
        decoder="LokSound 5",
    )

    assert electronics.dcc is True
    assert electronics.decoder == "LokSound 5"
    assert electronics.address == 3
    assert electronics.sound is False
    assert electronics.light is False

    _log(
        f"DCC electronics validated: "
        f"decoder={electronics.decoder}, "
        f"address={electronics.address}"
    )


def test_dcc_electronics_with_custom_address():
    electronics = Electronics(
        dcc=True,
        decoder="LokSound 5",
        address=4014,
        sound=True,
        light=True,
    )

    assert electronics.dcc is True
    assert electronics.decoder == "LokSound 5"
    assert electronics.address == 4014
    assert electronics.sound is True
    assert electronics.light is True

    _log(
        f"DCC electronics with custom address validated: "
        f"{electronics.address}"
    )


def test_non_dcc_sound_equipment():
    """
    Example: sound-equipped reefer container without DCC.
    """

    electronics = Electronics(
        dcc=False,
        sound=True,
        light=False,
    )

    assert electronics.dcc is False
    assert electronics.decoder is None
    assert electronics.address is None
    assert electronics.sound is True
    assert electronics.light is False

    _log("Non-DCC sound-equipped model validated")


def test_non_dcc_light_equipment():
    """
    Example: illuminated EOT device without DCC.
    """

    electronics = Electronics(
        dcc=False,
        sound=False,
        light=True,
    )

    assert electronics.dcc is False
    assert electronics.decoder is None
    assert electronics.address is None
    assert electronics.sound is False
    assert electronics.light is True

    _log("Non-DCC light-equipped model validated")


def test_sound_and_light_are_independent_of_dcc():
    electronics = Electronics(
        dcc=False,
        sound=True,
        light=True,
    )

    assert electronics.dcc is False
    assert electronics.sound is True
    assert electronics.light is True

    _log("Sound/light independence from DCC validated")


def test_dcc_requires_decoder():
    try:
        Electronics(
            dcc=True,
            decoder=None,
        )
        assert False, "DCC should require a decoder."
    except ValueError:
        pass

    _log("DCC decoder requirement validated")


def test_non_dcc_cannot_have_decoder():
    try:
        Electronics(
            dcc=False,
            decoder="LokSound 5",
        )
        assert False, "Non-DCC model cannot have a decoder."
    except ValueError:
        pass

    _log("Non-DCC decoder restriction validated")


def test_non_dcc_cannot_have_address():
    try:
        Electronics(
            dcc=False,
            address=3,
        )
        assert False, "Non-DCC model cannot have a DCC address."
    except ValueError:
        pass

    _log("Non-DCC address restriction validated")


def test_dcc_address_must_be_positive():
    try:
        Electronics(
            dcc=True,
            decoder="LokSound 5",
            address=0,
        )
        assert False, "DCC address must be greater than zero."
    except ValueError:
        pass

    _log("DCC address validation passed")


def test_invalid_decoder_is_rejected():
    try:
        Electronics(
            dcc=True,
            decoder="",
        )
        assert False, "Empty decoder should be rejected."
    except ValueError:
        pass

    _log("Invalid decoder correctly rejected")


def test_invalid_boolean_values_are_rejected():
    try:
        Electronics(dcc="true")
        assert False, "dcc must be a boolean."
    except TypeError:
        pass

    try:
        Electronics(sound="true")
        assert False, "sound must be a boolean."
    except TypeError:
        pass

    try:
        Electronics(light="true")
        assert False, "light must be a boolean."
    except TypeError:
        pass

    _log("Boolean validation passed")

