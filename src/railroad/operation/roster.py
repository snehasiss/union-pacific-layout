#!/usr/bin/env python3
# railroad/operation/roster.py

"""Operational search over an active collection of domain objects."""

from __future__ import annotations

from typing import Generic, Iterable, TypeVar

from railroad.domain.model import Status


T = TypeVar("T")


class Roster(Generic[T]):
    """Collection used for operational search.

    Retired objects are intentionally excluded when the roster is built.
    Search returns persistent IDs, not domain objects.
    """

    def __init__(self, objects: Iterable[T] = ()) -> None:
        self._objects = [obj for obj in objects if not self._retired(obj)]

    @property
    def objects(self) -> tuple[T, ...]:
        """Return the active objects represented by the roster."""
        return tuple(self._objects)

    def search(self, **criteria) -> list[str]:
        """Return IDs of active objects matching all supplied criteria."""
        return [
            obj.id
            for obj in self._objects
            if all(self._matches(obj, key, value) for key, value in criteria.items())
        ]

    @staticmethod
    def _retired(obj: T) -> bool:
        model = getattr(obj, "model", None)
        return model is not None and getattr(model, "status", None) == Status.RETIRED

    @staticmethod
    def _matches(obj: T, path: str, expected) -> bool:
        value = obj
        for part in path.split("."):
            value = getattr(value, part)
        return value == expected

    def __len__(self) -> int:
        return len(self._objects)

    def __iter__(self):
        return iter(self._objects)
