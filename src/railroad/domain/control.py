#!/usr/bin/env python3
# control.py
#

"""
Control information for a railroad model.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ControlType(Enum):
    """Control system used by a railroad model."""

    DC = "dc"
    DCC = "dcc"


@dataclass
class Control:
    """
    Describe the control capabilities of a railroad model.

    Attributes:
        type: DC or DCC control.
        light: Whether the model has lighting.
        sound: Whether the model has sound.
        smoke: Whether the model has a smoke generator.
        decoder: Installed DCC decoder, if applicable.
        address: DCC address, defaulting to 3 for DCC models.
    """

    type: ControlType = ControlType.DC
    light: bool = False
    sound: bool = False
    smoke: bool = False
    decoder: str | None = None
    address: int | None = None

    def __post_init__(self) -> None:
        """Validate control invariants."""

        if not isinstance(self.type, ControlType):
            raise TypeError("type must be a ControlType.")

        if not isinstance(self.light, bool):
            raise TypeError("light must be a boolean.")

        if not isinstance(self.sound, bool):
            raise TypeError("sound must be a boolean.")

        if not isinstance(self.smoke, bool):
            raise TypeError("smoke must be a boolean.")

        if self.decoder is not None:
            if not isinstance(self.decoder, str) or not self.decoder.strip():
                raise ValueError(
                    "decoder must be a non-empty string when provided."
                )

        if self.type == ControlType.DCC:
            if self.decoder is None:
                raise ValueError(
                    "decoder is required when control type is DCC."
                )

            if self.address is None:
                self.address = 3

            if not isinstance(self.address, int):
                raise TypeError(
                    "address must be an integer when control type is DCC."
                )

            if self.address < 1:
                raise ValueError(
                    "address must be greater than zero."
                )

        else:
            if self.decoder is not None:
                raise ValueError(
                    "decoder must be None when control type is DC."
                )

            if self.address is not None:
                raise ValueError(
                    "address must be None when control type is DC."
                )
