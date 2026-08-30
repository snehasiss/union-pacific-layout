from backend.config import load_config


def test_mac_profile_uses_port_5001():
    config = load_config("mac")
    assert config["profile"] == "mac"
    assert config["server"]["port"] == 5001
    assert config["serial"]["connectOnStartup"] is False


def test_sbc_profiles_use_stable_device_name():
    assert load_config("cubietruck")["serial"]["port"] == "/dev/csb1"
    assert load_config("axon")["serial"]["port"] == "/dev/csb1"

