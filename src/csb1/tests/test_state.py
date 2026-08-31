from backend.state import StateStore


def test_function_updates_merge_across_function_banks():
    state = StateStore("mac")

    state.update_locomotive(3, functions={"16": True, "31": True})
    locomotive = state.update_locomotive(
        3,
        functions={str(number): number == 0 for number in range(16)},
    )

    assert locomotive["functions"]["0"] is True
    assert locomotive["functions"]["1"] is False
    assert locomotive["functions"]["16"] is True
    assert locomotive["functions"]["31"] is True


def test_function_updates_still_replace_values_within_first_bank():
    state = StateStore("mac")

    state.update_locomotive(3, functions={"0": True, "2": True})
    locomotive = state.update_locomotive(3, functions={"0": False, "2": False})

    assert locomotive["functions"]["0"] is False
    assert locomotive["functions"]["2"] is False
