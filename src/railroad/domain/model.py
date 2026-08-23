#!/usr/bin/env python3
# railroad/domain/model.py
#

"""Physical scaled model representing a railroad prototype."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import ClassVar


class ModelStatus(Enum):
    """Lifecycle of a physical railroad model.

    SPOTTED and INTENT describe acquisition activity before a model is
    obtained. SHIPPED means the model is in transit. STORED means the
    model has arrived and is in the collection, whether in its original
    box or stored elsewhere. ACTIVE and REPAIR describe post-acquisition
    operation. RETIRED removes the model from the active roster.
    """

    INTENT = "intent"
    SPOTTED = "spotted"
    SHIPPED = "shipped"
    STORED = "stored"
    ACTIVE = "active"
    REPAIR = "repair"
    RETIRED = "retired"


@dataclass
class Model:
    """Describe the physical scaled model of a railroad prototype."""

    maker: str | None = None
    SCALE: ClassVar[str] = "HO"
    product: str | None = None
    status: ModelStatus = ModelStatus.STORED
    source: str | None = None
    price: float | None = None
    acquired: date | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        """Validate model attributes."""
        if self.maker is not None:
            if not isinstance(self.maker, str) or not self.maker.strip():
                raise ValueError("maker must be a non-empty string when provided.")

        if self.product is not None:
            if not isinstance(self.product, str) or not self.product.strip():
                raise ValueError("product must be a non-empty string when provided.")

        if not isinstance(self.status, ModelStatus):
            raise TypeError("status must be a ModelStatus.")

        if self.source is not None:
            if not isinstance(self.source, str) or not self.source.strip():
                raise ValueError("source must be a non-empty string when provided.")

        if self.price is not None:
            if not isinstance(self.price, (int, float)):
                raise TypeError("price must be numeric when provided.")
            if self.price < 0:
                raise ValueError("price cannot be negative.")

        if self.acquired is not None and not isinstance(self.acquired, date):
            raise TypeError("acquired must be a date when provided.")

        if self.note is not None and not isinstance(self.note, str):
            raise TypeError("note must be a string when provided.")
