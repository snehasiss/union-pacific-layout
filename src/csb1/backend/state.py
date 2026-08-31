from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateStore:
    def __init__(self, profile: str) -> None:
        self._lock = RLock()
        self._state: dict[str, Any] = {
            "profile": profile,
            "connection": {
                "status": "disconnected",
                "port": None,
                "error": None,
                "changedAt": utc_now(),
            },
            "trackPower": "off",
            "emergencyStop": False,
            "commandStation": None,
            "locomotives": {},
        }

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return deepcopy(self._state)

    def update(self, **changes: Any) -> dict[str, Any]:
        with self._lock:
            self._state.update(changes)
            return deepcopy(self._state)

    def set_connection(self, status: str, port: str | None, error: str | None = None) -> dict[str, Any]:
        return self.update(
            connection={
                "status": status,
                "port": port,
                "error": error,
                "changedAt": utc_now(),
            }
        )

    def update_locomotive(self, address: int, **changes: Any) -> dict[str, Any]:
        with self._lock:
            key = str(address)
            current = deepcopy(self._state["locomotives"].get(key, {}))
            if "functions" in changes:
                functions = dict(current.get("functions", {}))
                functions.update(changes["functions"])
                changes["functions"] = functions
            current.update({"address": address, **changes})
            self._state["locomotives"][key] = current
            return deepcopy(current)
