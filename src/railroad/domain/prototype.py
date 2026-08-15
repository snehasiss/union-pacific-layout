#!/usr/bin/env python3
# Prototype : represents the prototype (of the locomotive)

"""
Generic prototype representation for railroad entities.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Purpose(Enum):
    """Primary purpose of a railroad prototype."""

    PASSENGER = "passenger"
    FREIGHT = "freight"
    SWITCHER = "switcher"
    MACHINE = "machine"


@dataclass(frozen=True)
class Prototype:
    """
    Describe the real-world railroad prototype.

    Attributes:
        builder:
            Manufacturer/builder of the prototype.

        model:
            Primary prototype classification.

            Examples:
                Steam:  "4-8-8-4"
                Diesel: "SD90MAC"

        nickname:
            Commonly used prototype name, e.g. "Big Boy".

        purpose:
            Primary purpose of the prototype.
    """

    builder: str
    model: str
    nickname: str | None
    purpose: Purpose

    def __post_init__(self) -> None:
        """Validate prototype invariants."""

        if not isinstance(self.builder, str) or not self.builder.strip():
            raise ValueError("builder must be a non-empty string.")

        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("model must be a non-empty string.")

        if self.nickname is not None:
            if (
                not isinstance(self.nickname, str)
                or not self.nickname.strip()
            ):
                raise ValueError(
                    "nickname must be a non-empty string when provided."
                )

        if not isinstance(self.purpose, Purpose):
            raise TypeError("purpose must be a Purpose.")

