#!/usr/bin/env python3
# test_config.py

"""
Tests for railroad application configuration.
"""

from pathlib import Path

import pytest

from railroad.config import Config, DataConfig


CONFIG_FILE = Path("config/railroad-conf.json")


@pytest.fixture
def config() -> Config:
    """Return the application configuration."""

    return Config(CONFIG_FILE)


def test_config_can_be_loaded(config: Config) -> None:
    """Configuration can be loaded from the configuration file."""

    assert config.name == "union-pacific-layout"


def test_config_root(config: Config) -> None:
    """Configuration resolves the application root."""

    assert config.root.is_dir()
    assert config.root.name == "union-pacific-layout"


def test_config_directories(config: Config) -> None:
    """Configured application directories are resolved correctly."""

    assert config.config == config.root / "config"
    assert config.data == config.root / "data"
    assert config.resources == config.root / "resources"
    assert config.logs == config.root / "logs"


def test_resource_directories(config: Config) -> None:
    """Configured resource directories are resolved correctly."""

    assert config.drawings == config.root / "resources/drawings"
    assert config.media == config.root / "resources/media"


def test_loco_data_config(config: Config) -> None:
    """Loco data configuration is correct."""

    data = config.data_config("loco")

    assert isinstance(data, DataConfig)
    assert data.path == config.data / "loco"
    assert data.prefix == "L"


def test_car_data_config(config: Config) -> None:
    """Car data configuration is correct."""

    data = config.data_config("car")

    assert isinstance(data, DataConfig)
    assert data.path == config.data / "car"
    assert data.prefix == "C"


def test_mow_data_config(config: Config) -> None:
    """MOW data configuration is correct."""

    data = config.data_config("mow")

    assert isinstance(data, DataConfig)
    assert data.path == config.data / "mow"
    assert data.prefix == "M"


def test_signal_data_config(config: Config) -> None:
    """Signal data configuration is correct."""

    data = config.data_config("signal")

    assert isinstance(data, DataConfig)
    assert data.path == config.data / "signal"
    assert data.prefix == "G"


def test_turnout_data_config(config: Config) -> None:
    """Turnout data configuration is correct."""

    data = config.data_config("turnout")

    assert isinstance(data, DataConfig)
    assert data.path == config.data / "turnout"
    assert data.prefix == "T"


def test_unknown_data_config_is_rejected(config: Config) -> None:
    """An unknown data entity cannot be configured."""

    with pytest.raises(KeyError):
        config.data_config("unknown")

