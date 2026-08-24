#!/usr/bin/env python3
# railroad/operation/roster.py

"""Operational search over an active collection of domain objects."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Generic, Iterable, TypeVar

from railroad.domain.identity import EntityType
from railroad.domain.model import Status
from railroad.operation.ops import dao_for_type


T = TypeVar("T")


class Roster(Generic[T]):
    """Collection used for operational search.

    Retired objects are intentionally excluded when the roster is built.
    Search returns persistent IDs, not domain objects.
    """

    def __init__(self, objects: Iterable[T] = ()) -> None:
        self._objects = [obj for obj in objects if not self._retired(obj)]

    @classmethod
    def from_config(
        cls,
        config,
        entity_types: Iterable[EntityType] = (
            EntityType.LOCO,
            EntityType.CAR,
            EntityType.MOW,
        ),
        *,
        dao_factory=dao_for_type,
    ) -> "Roster":
        """Load currently supported persisted objects into an active roster.

        The returned collection omits retired objects just like a roster built
        directly from an iterable.  Callers may limit the collection to a
        subset of entity types when needed.
        """
        objects = []
        for entity_type in entity_types:
            if not isinstance(entity_type, EntityType):
                raise TypeError("entity_types must contain only EntityType values.")
            objects.extend(dao_factory(entity_type, config).list())
        return cls(objects)

    @property
    def objects(self) -> tuple[T, ...]:
        """Return the active objects represented by the roster."""
        return tuple(self._objects)

    def search(
        self,
        criteria: Mapping[str, object] | None = None,
        **keyword_criteria: object,
    ) -> list[str]:
        """Return active object IDs matching every supplied criterion.

        Criteria are attribute paths such as ``reporting_mark`` or
        ``model.status``.  A mapping is the primary public API; keyword
        criteria remain supported as a convenient shorthand.
        """
        if criteria is None:
            criteria = {}
        elif not isinstance(criteria, Mapping):
            raise TypeError("criteria must be a mapping when provided.")

        overlapping_keys = criteria.keys() & keyword_criteria.keys()
        if overlapping_keys:
            names = ", ".join(sorted(overlapping_keys))
            raise ValueError(f"criteria specified more than once: {names}.")

        all_criteria = {**criteria, **keyword_criteria}
        return [
            obj.id
            for obj in self._objects
            if all(self._matches(obj, key, value) for key, value in all_criteria.items())
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
