#!/usr/bin/env python3
# asset.py
#

"""
Asset information for a physical railroad model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class AssetStatus(Enum):
    """Lifecycle status of a physical railroad model asset."""

    OWNED = "owned"
    INTENT = "intent"
    RETIRED = "retired"


@dataclass
class Asset:
    """
    Describe acquisition and lifecycle information for a railroad asset.
    """

    status: AssetStatus = AssetStatus.OWNED
    source: str | None = None
    price: float | None = None
    acquired: date | None = None

    def __post_init__(self) -> None:
        """Validate asset invariants."""

        if not isinstance(self.status, AssetStatus):
            raise TypeError(
                "status must be an AssetStatus."
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
