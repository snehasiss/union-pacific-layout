#!/usr/bin/env python3
# tests/tools/test_loco_import.py
#

from datetime import date
from pathlib import Path

import pytest

from railroad.domain.control import ControlType
from railroad.domain.model import Model
from railroad.domain.prototype import Purpose
from railroad.rs.loco_type import LocoType
from railroad.tools.loco_import import LocoImport


IMPORT_DIRECTORY = (
    Path(__file__).resolve().parents[2]
    / "tools"
    / "imports"
)


def test_import_steam_file():
    locos = LocoImport.import_file(
        IMPORT_DIRECTORY / "steam.csv"
    )

    assert len(locos) == 27

    loco = locos[0]

    assert loco.id == "L301"
    assert loco.loco_type == LocoType.STEAM
    assert loco.railroad == "union pacific"
    assert loco.reporting_mark == "UP"
    assert loco.road_number == "4014"

    assert loco.prototype.builder == "ALCo"
    assert loco.prototype.model == "4-8-8-4"
    assert loco.prototype.nickname == "big boy"
    assert loco.prototype.purpose == Purpose.FREIGHT

    assert loco.model.manufacturer == "Athearn"
    assert loco.model.product is None
    # assert loco.model.scale == "HO"

    assert loco.control.type == ControlType.DCC
    assert loco.control.decoder == "tsunami"
    assert loco.control.address == 3
    assert loco.control.sound is True
    assert loco.control.light is True
    assert loco.control.smoke is False

    assert loco.asset.status.value == "owned"
    assert loco.asset.source == "model train stuff"
    assert loco.asset.price == 655.0
    assert loco.asset.acquired == date(2020, 11, 20)


def test_import_dc_locomotive_translates_decoder_and_address():
    locos = LocoImport.import_file(
        IMPORT_DIRECTORY / "steam.csv"
    )

    loco = next(
        loco
        for loco in locos
        if loco.reporting_mark == "UP"
        and loco.road_number == "5090"
    )

    assert loco.control.type == ControlType.DC
    assert loco.control.decoder is None
    assert loco.control.address == 0
    assert loco.control.sound is False
    assert loco.control.light is False
    assert loco.control.smoke is False

    assert loco.asset.status.value == "intent"
    assert loco.asset.source == "unknown"
    assert loco.asset.price == 0.0
    assert loco.asset.acquired is None


def test_import_diesel_file_1():
    locos = LocoImport.import_file(
        IMPORT_DIRECTORY / "diesel.csv"
    )

    assert len(locos) == 122

    loco = locos[0]

    assert loco.loco_type == LocoType.DIESEL
    assert loco.prototype.builder == "Plymouth"
    assert loco.prototype.model == "35T switcher"

    assert loco.model.manufacturer == "Broadway Limited"
    assert loco.model.product is None
    # assert loco.model.scale == "HO"

    assert loco.control.type == ControlType.DCC
    assert loco.control.decoder == "dcc"
    assert loco.control.address == 3


def test_import_turbine():
    locos = LocoImport.import_file(
        IMPORT_DIRECTORY / "diesel.csv"
    )

    turbine = next(
        loco
        for loco in locos
        if loco.loco_type == LocoType.TURBINE
    )

    assert turbine.prototype.model == "Turbine Gas Big Blow"
    assert turbine.loco_type == LocoType.TURBINE
    assert turbine.reporting_mark == "UP"
    assert turbine.road_number == "28"


def test_reporting_mark_is_normalised_to_uppercase():
    locos = LocoImport.import_file(
        IMPORT_DIRECTORY / "steam.csv"
    )

    loco = locos[0]

    assert loco.reporting_mark == "UP"


def test_optional_values_are_none():
    locos = LocoImport.import_file(
        IMPORT_DIRECTORY / "steam.csv"
    )

    loco = next(
        loco
        for loco in locos
        if loco.road_number == "3203"
    )

    assert loco.prototype.nickname == "pacific"
    assert loco.asset.price == 0.0
    assert loco.asset.acquired is None


def test_invalid_boolean_raises():
    row = {
        "dcc": "maybe",
        "light": "yes",
        "sound": "no",
        "smoke": "no",
        "decoder": "dc",
        "address": "0",
    }

    with pytest.raises(ValueError):
        LocoImport._create_control(row)


def test_import_diesel_file():
    locos = LocoImport.import_file(
        IMPORT_DIRECTORY / "diesel.csv"
    )

    assert len(locos) == 122

    assert all(
        loco.loco_type in {
            LocoType.DIESEL,
            LocoType.TURBINE,
        }
        for loco in locos
    )

    assert all(
        loco.control.address == 0
        for loco in locos
        if loco.control.type == ControlType.DC
    )

    assert all(
        loco.control.address >= 1
        for loco in locos
        if loco.control.type == ControlType.DCC
    )

