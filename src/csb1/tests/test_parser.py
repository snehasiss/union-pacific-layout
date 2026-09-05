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


def test_parses_functions_through_f15():
    event = parse_frame(f"<l 3 0 128 {1 << 15}>")
    assert event.data["functions"]["15"] is True


def test_parses_correlated_cv_read_response():
    event = parse_frame("<r 7|0|29 38>")
    assert event.type == "cv"
    assert event.data == {"cv": 29, "value": 38, "callback": 7, "callbackSub": 0}


def test_parses_compact_correlated_cv_read_response():
    event = parse_frame("<r7|0|29 38>")
    assert event.type == "cv"
    assert event.data == {"cv": 29, "value": 38, "callback": 7, "callbackSub": 0}


def test_parses_cv_write_response():
    event = parse_frame("<r 29 38>")
    assert event.type == "cv"
    assert event.data == {"cv": 29, "value": 38}
