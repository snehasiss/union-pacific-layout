import pytest

from backend.serial.commands import emergency_stop, function, power, throttle


def test_power_commands():
    assert power("on") == "<1>"
    assert power("off", "MAIN") == "<0 MAIN>"


def test_invalid_power_state():
    with pytest.raises(ValueError):
        power("maybe")


def test_emergency_stop_command():
    assert emergency_stop() == "<!>"


def test_throttle_command():
    assert throttle(3, 42, "forward") == "<t 3 42 1>"
    assert throttle(4014, 0, "reverse") == "<t 4014 0 0>"


def test_function_commands_f0_to_f31():
    assert function(3, 0, True) == "<F 3 0 1>"
    assert function(3, 8, False) == "<F 3 8 0>"
    assert function(3, 15, True) == "<F 3 15 1>"
    assert function(3, 16, True) == "<F 3 16 1>"
    assert function(3, 31, False) == "<F 3 31 0>"


@pytest.mark.parametrize("address,speed,direction", [(0, 0, "forward"), (3, 127, "forward"), (3, 0, "sideways")])
def test_invalid_throttle(address, speed, direction):
    with pytest.raises(ValueError):
        throttle(address, speed, direction)
