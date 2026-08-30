from backend.roster import available_locomotives


def test_available_locomotives_come_from_shared_railroad_operation_layer():
    locomotives = available_locomotives()
    assert all(locomotive["status"] == "active" for locomotive in locomotives)
    assert all(isinstance(locomotive["address"], int) for locomotive in locomotives)
