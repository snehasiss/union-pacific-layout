#!/usr/bin/env python3
# electronics.py
#

"""
Electronic equipment fitted to a railroad model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Electronics:
    """
    Describe electronic equipment fitted to a railroad model.

    Electronics is generic and may apply to locomotives, cars,
    reefer containers, EOT devices, cabooses, power cars, MOW
    vehicles, and other railroad entities.

    Attributes:
        dcc:
            Whether the model is DCC equipped.

        decoder:
            Installed DCC decoder identification, if applicable.

        address:
            DCC address. Defaults to 3 for DCC-equipped models.

        sound:
            Whether the model has an electronic sound capability.

        light:
            Whether the model has electronically controlled lighting.
    """

    dcc: bool = False
    decoder: str | None = None
    address: int | None = None
    sound: bool = False
    light: bool = False

    def __post_init__(self) -> None:
        """Validate electronics invariants."""

        if not isinstance(self.dcc, bool):
            raise TypeError("dcc must be a boolean.")

        if not isinstance(self.sound, bool):
            raise TypeError("sound must be a boolean.")

        if not isinstance(self.light, bool):
            raise TypeError("light must be a boolean.")

        if self.decoder is not None:
            if not isinstance(self.decoder, str) or not self.decoder.strip():
                raise ValueError(
                    "decoder must be a non-empty string when provided."
                )

        if self.dcc:
            if self.decoder is None:
                raise ValueError(
                    "decoder is required when dcc is True."
                )

            if self.address is None:
                self.address = 3

            if not isinstance(self.address, int):
                raise TypeError(
                    "address must be an integer when dcc is True."
                )

            if self.address < 1:
                raise ValueError(
                    "address must be greater than zero."
                )

        else:
            if self.decoder is not None:
                raise ValueError(
                    "decoder must be None when dcc is False."
                )

            if self.address is not None:
                raise ValueError(
                    "address must be None when dcc is False."
                )

