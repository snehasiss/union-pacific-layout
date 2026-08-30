from backend.serial.framing import DccExFramer


def test_reassembles_fragmented_frames():
    framer = DccExFramer()
    assert framer.feed("boot log\n<p") == []
    assert framer.feed("1><iDCC-EX V-5.4.0>") == ["<p1>", "<iDCC-EX V-5.4.0>"]


def test_ignores_text_outside_frames():
    framer = DccExFramer()
    assert framer.feed("diagnostic\n<p0>more text") == ["<p0>"]

