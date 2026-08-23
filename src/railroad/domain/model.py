#!/usr/bin/env python3
# railroad/domain/model.py
#

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from enum import Enum


class ModelStatus(Enum):
    """Lifecycle status of a physical railroad model asset."""

    UNKNOWN = "unknown"
    ACTIVE = "active"
    OFFLINE = "offline"
    STORED = "stored"
    RETIRED = "retired"


@dataclass
class Model:
    """
    Physical model representing a railroad prototype.
    """

    maker: str | None = None
    SCALE: ClassVar[str] = "HO"
    product: str | None = None
    status: ModelStatus | None = ModelStatus.UNKNOWN

    def __post_init__(self) -> None:
        """Validate model attributes."""
        if self.maker is not None:
            if (
                not isinstance(self.maker, str)
                or not self.maker.strip()
            ):
                raise ValueError(
                    "maker must be a non-empty string when provided."
                )

        if self.product is not None:
            if (
                not isinstance(self.product, str)
                or not self.product.strip()
            ):
                raise ValueError(
                    "product must be a non-empty string when provided."
                )