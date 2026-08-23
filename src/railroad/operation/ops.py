#!/usr/bin/env python3
# railroad/operation/ops.py

"""Common operational persistence mechanics."""

from __future__ import annotations

from railroad.dao import CarDAO, LocoDAO, MowDAO
from railroad.domain.identity import EntityType, IdGenerator


_PREFIX_TYPES = {
    "L": EntityType.LOCO,
    "C": EntityType.CAR,
    "M": EntityType.MOW,
    "G": EntityType.SIGNAL,
    "T": EntityType.TURNOUT,
}


def validate_id(entity_id: str) -> str:
    """Validate and return a persistent railroad object ID."""
    IdGenerator.parse(entity_id)
    return entity_id


def resolve_type(entity_id: str) -> EntityType:
    """Resolve an object type from its persistent ID namespace."""
    prefix, _ = IdGenerator.parse(entity_id)
    try:
        return _PREFIX_TYPES[prefix]
    except KeyError as exc:
        raise ValueError(f"Unknown railroad object prefix '{prefix}'.") from exc


def load_object(dao, entity_id: str):
    """Load one domain object through its DAO."""
    validate_id(entity_id)
    return dao.get(entity_id)


def save_object(dao, obj):
    """Persist one domain object through its DAO."""
    dao.save(obj)
    return obj


def dao_for_type(entity_type: EntityType, config):
    """Create the DAO for a currently supported persisted object type."""
    daos = {
        EntityType.LOCO: LocoDAO,
        EntityType.CAR: CarDAO,
        EntityType.MOW: MowDAO,
    }
    try:
        return daos[entity_type](config)
    except KeyError as exc:
        raise NotImplementedError(
            f"No DAO is registered yet for {entity_type.value}."
        ) from exc
