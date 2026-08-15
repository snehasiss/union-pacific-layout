#!/usr/bin/env python3
# test_config.py

"""
Tests for the railroad Config class.
"""

import json
from pathlib import Path

import pytest

from railroad.config import Config


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    """Create a representative railroad configuration."""

    root = tmp_path / "union-pacific-layout"
    config_dir = root / "config"
    config_dir.mkdir(parents=True)

    path = config_dir / "railroad-conf.json"

    configuration = {
        "application": {
            "name": "union-pacific-layout"
        },
        "paths": {
            "config": "config",
            "data": "data",
            "resources": "resources",
            "logs": "logs"
        },
        "data": {
            "locomotive": "data/locomotive",
            "car": "data/car",
            "mow": "data/mow"
        },
        "resources": {
            "drawings": "resources/drawings",
            "media": "resources/media"
        }
    }

    path.write_text(
        json.dumps(configuration, indent=4),
        encoding="utf-8",
    )

    return path


def test_config_can_be_loaded(config_path: Path) -> None:
    """Configuration can be loaded from JSON."""

    config = Config(config_path)

    assert isinstance(config, Config)


def test_application_name(config_path: Path) -> None:
    """Application name is available from configuration."""

    config = Config(config_path)

    assert config.name == "union-pacific-layout"


def test_root_directory(config_path: Path) -> None:
    """Application root is resolved from the configuration location."""

    config = Config(config_path)

    assert config.root == config_path.parent.parent.resolve()


def test_config_directory(config_path: Path) -> None:
    """Configuration directory is resolved correctly."""

    config = Config(config_path)

    assert config.config == config.root / "config"


def test_data_directory(config_path: Path) -> None:
    """Data directory is resolved correctly."""

    config = Config(config_path)

    assert config.data == config.root / "data"


def test_resources_directory(config_path: Path) -> None:
    """Resources directory is resolved correctly."""

    config = Config(config_path)

    assert config.resources == config.root / "resources"


def test_logs_directory(config_path: Path) -> None:
    """Logs directory is resolved correctly."""

    config = Config(config_path)

    assert config.logs == config.root / "logs"


def test_locomotive_directory(config_path: Path) -> None:
    """Locomotive data directory is resolved correctly."""

    config = Config(config_path)

    assert config.locomotive == config.root / "data" / "locomotive"


def test_car_directory(config_path: Path) -> None:
    """Car data directory is resolved correctly."""

    config = Config(config_path)

    assert config.car == config.root / "data" / "car"


def test_mow_directory(config_path: Path) -> None:
    """MOW data directory is resolved correctly."""

    config = Config(config_path)

    assert config.mow == config.root / "data" / "mow"


def test_drawings_directory(config_path: Path) -> None:
    """Drawings resource directory is resolved correctly."""

    config = Config(config_path)

    assert config.drawings == config.root / "resources" / "drawings"


def test_media_directory(config_path: Path) -> None:
    """Media resource directory is resolved correctly."""

    config = Config(config_path)

    assert config.media == config.root / "resources" / "media"


def test_paths_are_absolute(config_path: Path) -> None:
    """All resolved configuration paths are absolute."""

    config = Config(config_path)

    paths = [
        config.root,
        config.config,
        config.data,
        config.resources,
        config.logs,
        config.locomotive,
        config.car,
        config.mow,
        config.drawings,
        config.media,
    ]

    assert all(path.is_absolute() for path in paths)


def test_missing_configuration_file_is_rejected(tmp_path: Path) -> None:
    """A missing configuration file raises FileNotFoundError."""

    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        Config(path)


def test_invalid_json_is_rejected(tmp_path: Path) -> None:
    """Invalid JSON raises JSONDecodeError."""

    path = tmp_path / "invalid.json"
    path.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    with pytest.raises(json.JSONDecodeError):
        Config(path)

