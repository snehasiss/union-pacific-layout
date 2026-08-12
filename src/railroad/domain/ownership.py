#!/usr/bin/env python3
# ownership.py
#

"""
Ownership information for a physical railroad model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class OwnershipStatus(Enum):
    """Ownership status of a physical railroad model."""

    OWNED = "owned"
    INTENT = "intent"
    RETIRED = "retired"


@dataclass
class Ownership:
    """
    Describe ownership and acquisition information.

    This object is generic and may be associated with locomotives,
    cars, MOW equipment, power cars, containers, and other physical
    railroad models.
    """

    status: OwnershipStatus = OwnershipStatus.OWNED
    source: str | None = None
    price: float | None = None
    acquired: date | None = None

    def __post_init__(self) -> None:
        """Validate ownership attributes."""

        if not isinstance(self.status, OwnershipStatus):
            raise TypeError(
                "status must be an OwnershipStatus."
            )

        if self.source is not None:
            if not isinstance(self.source, str) or not self.source.strip():
                raise ValueError(
                    "source must be a non-empty string when provided."
                )

        if self.price is not None:
            if not isinstance(self.price, (int, float)):
                raise TypeError(
                    "price must be numeric when provided."
                )

            if self.price < 0:
                raise ValueError(
                    "price cannot be negative."
                )

        if self.acquired is not None:
            if not isinstance(self.acquired, date):
                raise TypeError(
                    "acquired must be a date when provided."
                )
