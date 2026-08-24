#!/usr/bin/env python3
# railroad/operation/asset.py

"""Object-centric operations for persisted railroad assets."""

from __future__ import annotations

from typing import Callable

from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Status
from railroad.operation.ops import dao_for_type, load_object, resolve_type, save_object, validate_id


class Asset:
    """A generic operational wrapper around one railroad object.

    Construct an unbound gateway with ``Asset(config)``.  ``view`` and
    ``create`` return a bound Asset that delegates domain attributes to its
    loaded object and can persist or retire itself.
    """

    def __init__(
        self,
        config,
        *,
        dao_factory: Callable = dao_for_type,
        obj=None,
        dao=None,
    ) -> None:
        self._config = config
        self._dao_factory = dao_factory
        self._object = obj
        self._dao = dao

    @property
    def object(self):
        """Return the wrapped railroad domain object."""
        return self._require_object()

    def view(self, entity_id: str) -> "Asset":
        """Load and bind an object by ID, including retired objects."""
        validate_id(entity_id)
        entity_type = resolve_type(entity_id)
        dao = self._dao_factory(entity_type, self._config)
        return Asset(
            self._config,
            dao_factory=self._dao_factory,
            obj=load_object(dao, entity_id),
            dao=dao,
        )

    def update(self) -> "Asset":
        """Persist this bound asset after its domain object has been modified."""
        obj = self._require_object()
        self._validate_object(obj)
        save_object(self._dao, obj)
        return self

    def retire(self) -> "Asset":
        """Mark this bound asset retired and persist it.

        A retired object remains viewable by ID, but is excluded from an
        operational roster/search.
        """
        obj = self._require_object()
        self._validate_object(obj)
        if not hasattr(obj, "model"):
            raise TypeError("asset retirement requires an object with model.status.")
        obj.model.status = Status.RETIRED
        return self.update()

    def create(
        self,
        entity_type: EntityType,
        builder: Callable[[Identity], object],
        *,
        railroad: str,
        reporting_mark: str,
        road_number: str,
    ) -> "Asset":
        """Create, assign an ID to, and persist a new domain object.

        The caller supplies a builder for the concrete domain object; this
        operation owns identity allocation and persistence.
        """
        if not isinstance(entity_type, EntityType):
            raise TypeError("entity_type must be an EntityType.")
        dao = self._dao_factory(entity_type, self._config)
        entity_id = dao.next_id()
        identity = Identity.from_existing(
            id=entity_id,
            entity_type=entity_type,
            railroad=railroad,
            reporting_mark=reporting_mark,
            road_number=road_number,
        )
        obj = builder(identity)
        self._validate_object(obj, entity_type)
        save_object(dao, obj)
        return Asset(self._config, dao_factory=self._dao_factory, obj=obj, dao=dao)

    def _require_object(self):
        if self._object is None or self._dao is None:
            raise RuntimeError("Asset is not bound; call view() or create() first.")
        return self._object

    def _validate_object(self, obj, expected_type: EntityType | None = None) -> None:
        if not hasattr(obj, "identity") or not hasattr(obj, "id"):
            raise TypeError("asset must wrap a persisted railroad domain object.")
        entity_type = expected_type or resolve_type(obj.id)
        if obj.identity.entity_type != entity_type:
            raise ValueError(
                f"object identity must have EntityType.{entity_type.name}."
            )
        validate_id(obj.id)
        if resolve_type(obj.id) != entity_type:
            raise ValueError(f"object ID '{obj.id}' does not match its entity type.")

    def __getattr__(self, name: str):
        """Expose the wrapped domain object's attributes on a bound asset."""
        return getattr(self._require_object(), name)
