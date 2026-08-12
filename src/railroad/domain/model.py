#!/usr/bin/env python3
# model.py
# 

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Model:
    """
    Physical HO-scale model representing a railroad prototype.
    """

    manufacturer: str | None = None
    product: str | None = None

    SCALE: ClassVar[str] = "HO"

    def __post_init__(self) -> None:
        """Validate model attributes."""

        if self.manufacturer is not None:
            if (
                not isinstance(self.manufacturer, str)
                or not self.manufacturer.strip()
            ):
                raise ValueError(
                    "manufacturer must be a non-empty string when provided."
                )

        if self.product is not None:
            if (
                not isinstance(self.product, str)
                or not self.product.strip()
            ):
                raise ValueError(
                    "product must be a non-empty string when provided."
                )

