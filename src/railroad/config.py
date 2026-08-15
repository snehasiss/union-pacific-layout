#!/usr/bin/env python3
# config.py

"""
Application configuration for the railroad system.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union


class Config:
    """Load and provide access to railroad application configuration."""

    def __init__(self, path: Union[str, Path]) -> None:
        self._path = Path(path).resolve()
        self._root = self._path.parent.parent

        with self._path.open("r", encoding="utf-8") as file:
            self._data: dict[str, Any] = json.load(file)

    @property
    def name(self) -> str:
        """Return the application name."""

        return self._data["application"]["name"]

    @property
    def root(self) -> Path:
        """Return the application root directory."""

        return self._root

    @property
    def config(self) -> Path:
        """Return the configuration directory."""

        return self._resolve(self._data["paths"]["config"])

    @property
    def data(self) -> Path:
        """Return the data directory."""

        return self._resolve(self._data["paths"]["data"])

    @property
    def resources(self) -> Path:
        """Return the resources directory."""

        return self._resolve(self._data["paths"]["resources"])

    @property
    def logs(self) -> Path:
        """Return the logs directory."""

        return self._resolve(self._data["paths"]["logs"])

    @property
    def locomotive(self) -> Path:
        """Return the locomotive data directory."""

        return self._resolve(self._data["data"]["locomotive"])

    @property
    def car(self) -> Path:
        """Return the car data directory."""

        return self._resolve(self._data["data"]["car"])

    @property
    def mow(self) -> Path:
        """Return the MOW data directory."""

        return self._resolve(self._data["data"]["mow"])

    @property
    def drawings(self) -> Path:
        """Return the drawings resource directory."""

        return self._resolve(self._data["resources"]["drawings"])

    @property
    def media(self) -> Path:
        """Return the media resource directory."""

        return self._resolve(self._data["resources"]["media"])

    def _resolve(self, value: str) -> Path:
        """Resolve a configuration path relative to the application root."""

        return (self._root / value).resolve()
