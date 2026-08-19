#!/usr/bin/env python3
# loco.py
#

"""
Loco domain entity.

A Loco represents a physical locomotive in the railroad's
digital model.
"""

from __future__ import annotations

from dataclasses import dataclass

from railroad.domain.electronics import Electronics
from railroad.domain.identity import Identity
from railroad.domain.model import Model
from railroad.domain.ownership import Ownership
from railroad.domain.prototype import Prototype
from railroad.rs.loco_type import LocoType


@dataclass
class Loco:
    """
    Digital representation of a physical locomotive.

    A locomotive is composed of shared domain objects describing
    its identity, prototype, physical model, electronics, and
    ownership.
    """

    identity: Identity
    loco_type: LocoType
    prototype: Prototype
    model: Model
    electronics: Electronics
    ownership: Ownership

        
    def __post_init__(self) -> None:
        """Validate locomotive invariants."""

        if not isinstance(self.identity, Identity):
            raise TypeError("identity must be an Identity.")

        if not isinstance(self.loco_type, LocoType):
            raise TypeError("loco_type must be a LocoType")

        if not isinstance(self.prototype, Prototype):
            raise TypeError("prototype must be a Prototype.")

        if not isinstance(self.model, Model):
            raise TypeError("model must be a Model.")

        if not isinstance(self.electronics, Electronics):
            raise TypeError("electronics must be an Electronics.")

        if not isinstance(self.ownership, Ownership):
            raise TypeError("ownership must be an Ownership.")

    @property
    def id(self) -> str:
        """Return the persistent digital identity."""
        return self.identity.id

    @property
    def entity_type(self) -> EntityType:
        """Return the locomotive entity type."""
        return self.identity.entity_type

    @property
    def railroad(self) -> str:
        """Return the represented railroad."""
        return self.identity.railroad

    @property
    def reporting_mark(self) -> str:
        """Return the railroad reporting mark."""
        return self.identity.reporting_mark

    @property
    def road_number(self) -> int:
        """Return the locomotive road number."""
        return self.identity.road_number

    @property
    def prototype_model(self) -> str:
        """Return the prototype model or wheel arrangement."""
        return self.prototype.model

    @property
    def nickname(self) -> str | None:
        """Return the prototype nickname."""
        return self.prototype.nickname

