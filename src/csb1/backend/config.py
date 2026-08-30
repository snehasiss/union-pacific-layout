from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_DIR / "config"


class ConfigurationError(RuntimeError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"Unable to read configuration {path}: {exc}") from exc


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def load_config(profile: str | None = None) -> dict[str, Any]:
    selected = profile or os.environ.get("CSB1_PROFILE", "mac")
    profile_path = CONFIG_DIR / f"{selected}.json"
    if not profile_path.is_file():
        raise ConfigurationError(f"Unknown CSB1 profile: {selected}")

    config = _merge(_read_json(CONFIG_DIR / "common.json"), _read_json(profile_path))
    config["profile"] = selected

    if port := os.environ.get("CSB1_SERIAL_PORT"):
        config["serial"]["port"] = port
    if server_port := os.environ.get("CSB1_SERVER_PORT"):
        config["server"]["port"] = int(server_port)
    if server_host := os.environ.get("CSB1_SERVER_HOST"):
        config["server"]["host"] = server_host

    validator = Draft202012Validator(_read_json(CONFIG_DIR / "schema.json"))
    errors = sorted(validator.iter_errors(config), key=lambda error: list(error.path))
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ConfigurationError(f"Invalid configuration: {details}")
    return config
