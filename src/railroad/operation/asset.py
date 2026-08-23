#!/usr/bin/env python3
# railroad/operation/asset.py

"""Generic operations on persisted railroad assets."""

from __future__ import annotations

from typing import Callable, Generic, TypeVar

from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Status
from railroad.operation.ops import load_object, resolve_type, save_object, validate_id


T = TypeVar("T")


class Asset(Generic[T]):
    """Operational facade over one persisted railroad object type.

    The wrapped object remains a domain object. This class owns only
    operational mechanics such as load, update, retire, and creation.
    """

    def __init__(self, dao, object_type: type[T], entity_type: EntityType, prefix: str) -> None:
        self._dao = dao
        self._object_type = object_type
        self._entity_type = entity_type
        self._prefix = prefix

    def view(self, entity_id: str) -> T:
        """Return the domain object stored under an ID, including retired objects."""
        validate_id(entity_id)
        if resolve_type(entity_id) != self._entity_type:
            raise ValueError(
                f"ID '{entity_id}' does not belong to {self._entity_type.value}."
            )
        return load_object(self._dao, entity_id)

    def update(self, obj: T) -> T:
        """Persist a modified domain object and return it."""
        self._validate_object(obj)
        return save_object(self._dao, obj)

    def retire(self, obj: T | str) -> T:
        """Mark an object retired and persist it.

        A retired object remains viewable by ID, but is excluded from an
        operational roster/search.
        """
        if isinstance(obj, str):
            obj = self.view(obj)
        self._validate_object(obj)
        if not hasattr(obj, "model"):
            raise TypeError("asset retirement requires an object with model.status.")
        obj.model.status = Status.RETIRED
        return self.update(obj)

    def create(
        self,
        builder: Callable[[Identity], T],
        *,
        railroad: str,
        reporting_mark: str,
        road_number: str,
    ) -> T:
        """Create, assign an ID to, and persist a new domain object.

        The caller supplies a builder for the concrete domain object; this
        operation owns identity allocation and persistence.
        """
        entity_id = self._dao.next_id()
        identity = Identity.from_existing(
            id=entity_id,
            entity_type=self._entity_type,
            railroad=railroad,
            reporting_mark=reporting_mark,
            road_number=road_number,
        )
        obj = builder(identity)
        self._validate_object(obj)
        return save_object(self._dao, obj)

    def _validate_object(self, obj: T) -> None:
        if not isinstance(obj, self._object_type):
            raise TypeError(
                f"expected {self._object_type.__name__}, got {type(obj).__name__}."
            )
        if obj.identity.entity_type != self._entity_type:
            raise ValueError(
                f"object identity must have EntityType.{self._entity_type.name}."
            )
        validate_id(obj.id)
        if not obj.id.startswith(self._prefix):
            raise ValueError(
                f"object ID '{obj.id}' does not belong to prefix '{self._prefix}'."
            )
