#!/usr/bin/env python3
# railroad/tests/rs/test_loco_type.py
#

def test_loco_type_values():
    assert LocoType.STEAM.value == "steam"
    assert LocoType.DIESEL.value == "diesel"
