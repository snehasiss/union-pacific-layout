from backend.serial.parser import parse_frame


def test_parses_forward_locomotive_broadcast():
    event = parse_frame("<l 4014 0 171 5>")
    assert event.type == "locomotive"
    assert event.data["address"] == 4014
    assert event.data["speed"] == 42
    assert event.data["direction"] == "forward"
    assert event.data["functions"]["0"] is True
    assert event.data["functions"]["2"] is True


def test_parses_stopped_reverse_locomotive_broadcast():
    event = parse_frame("<l 3 0 0 0>")
    assert event.data["speed"] == 0
    assert event.data["direction"] == "reverse"
