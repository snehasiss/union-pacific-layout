#!/usr/bin/env python3
# Identity : identity of the record
#

"""
Generic identity for railroad entities.

An Identity uniquely identifies a physical railroad entity within
the digital model.

Examples:

    L001 -> locomotive
    C001 -> car
    M001 -> MOW equipment

The identity also retains the prototype's railroad identity:

    railroad
    reporting_mark
    road_number
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class IdGenerator:
    """
    Generate sequential IDs within an entity namespace.

    The namespace is represented by a single-character prefix.

    Examples:
        L -> L001, L002, L003, ...
        C -> C001, C002, C003, ...
        M -> M001, M002, M003, ...
    """

    MIN_DIGITS = 3
    MAX_NUMBER = 999

    _next_numbers: dict[str, int] = {}

    @classmethod
    def next_id(cls, prefix: str) -> str:
        """Return the next available ID for the specified namespace."""
        prefix = cls._validate_prefix(prefix)

        next_number = cls._next_numbers.get(prefix, 1)

        if next_number > cls.MAX_NUMBER:
            raise ValueError(
                f"Maximum ID {prefix}{cls.MAX_NUMBER} "
                f"has been reached."
            )

        entity_id = f"{prefix}{next_number:0{cls.MIN_DIGITS}d}"

        cls._next_numbers[prefix] = next_number + 1

        return entity_id

    @classmethod
    def reset(cls) -> None:
        """Reset generated ID state.

        Intended primarily for test isolation.
        """
        cls._next_numbers.clear()

    @classmethod
    def observe(cls, entity_id: str) -> None:
        """
        Register an existing entity ID.

        This is used when an entity is reconstructed from persistence,
        ensuring that subsequently generated IDs do not collide with
        the existing entity.
        """
        prefix, number = cls.parse(entity_id)

        next_number = cls._next_numbers.get(prefix, 1)

        if number >= next_number:
            cls._next_numbers[prefix] = number + 1

    @classmethod
    def parse(cls, entity_id: str) -> tuple[str, int]:
        """Validate an entity ID and return its prefix and number."""
        if not isinstance(entity_id, str):
            raise TypeError("entity_id must be a string.")

        match = re.fullmatch(
            rf"([A-Z])(\d{{{cls.MIN_DIGITS},{len(str(cls.MAX_NUMBER))}}})",
            entity_id,
        )

        if match is None:
            raise ValueError(
                f"Invalid entity ID '{entity_id}'. "
                f"Expected format X001 through X{cls.MAX_NUMBER}."
            )

        prefix = match.group(1)
        number = int(match.group(2))

        if number < 1 or number > cls.MAX_NUMBER:
            raise ValueError(f"Invalid entity ID '{entity_id}'.")

        return prefix, number

    @staticmethod
    def _validate_prefix(prefix: str) -> str:
        """Validate an entity namespace prefix."""
        if not isinstance(prefix, str):
            raise TypeError("prefix must be a string.")

        if not re.fullmatch(r"[A-Z]", prefix):
            raise ValueError(
                "prefix must be a single uppercase alphabetic character."
            )

        return prefix


class EntityType(Enum):
    LOCO = "loco"
    CAR = "car"
    MOW = "mow"
    SIGNAL = "signal"
    TURNOUT = "turnout"


@dataclass(frozen=True)
class Identity:
    """
    Generic identity of a railroad entity.

    Attributes:
        id:
            Persistent digital identity, e.g. L001.

        entity_type:
            Primary domain classification, e.g. steam, diesel,
            hopper, reefer, passenger.

        railroad:
            Railroad represented by the entity.

        reporting_mark:
            Railroad reporting mark, e.g. UP.

        road_number:
            Number carried by the real-world entity.
    """

    id: str
    entity_type: EntityType
    railroad: str
    reporting_mark: str
    road_number: str 

    @classmethod
    def create(
        cls,
        prefix: str,
        entity_type: EntityType,
        railroad: str,
        reporting_mark: str,
        road_number: str,
    ) -> "Identity":
        """
        Create a new identity and allocate a new persistent ID.
        """
        entity_id = IdGenerator.next_id(prefix)

        return cls(
            id=entity_id,
            entity_type=entity_type,
            railroad=railroad,
            reporting_mark=reporting_mark,
            road_number=road_number,
        )

    @classmethod
    def from_existing(
        cls,
        id: str,
        entity_type: EntityType,
        railroad: str,
        reporting_mark: str,
        road_number: str,
    ) -> "Identity":
        """
        Reconstruct an identity from persisted data.

        The existing ID is registered with the generator so future
        IDs remain sequential and collision-free.
        """
        IdGenerator.observe(id)

        return cls(
            id=id,
            entity_type=entity_type,
            railroad=railroad,
            reporting_mark=reporting_mark,
            road_number=road_number,
        )

    def __post_init__(self) -> None:
        """Validate identity invariants."""
        IdGenerator.parse(self.id)

        if not isinstance(self.entity_type, EntityType):
            raise ValueError("entity_type must be an EntityType.")

        if not isinstance(self.railroad, str) or not self.railroad.strip():
            raise ValueError("railroad must be a non-empty string.")

        if (
            not isinstance(self.reporting_mark, str)
            or not self.reporting_mark.strip()
        ):
            raise ValueError(
                "reporting_mark must be a non-empty string."
            )

        if not isinstance(self.road_number, str):
            raise TypeError("road_number must be a string.")

        if not self.road_number.strip():
            raise ValueError(
                "road_number must be a non-empty string."
            )

