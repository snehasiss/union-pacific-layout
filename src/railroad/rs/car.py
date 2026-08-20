#!/usr/bin/env python3
# railroad/rs/car.py
#

"""
Car domain entity.

A Car represents a physical railroad car in the railroad's
digital model.
"""

from __future__ import annotations

from dataclasses import dataclass

from railroad.rs.car_type import CarType
from railroad.domain.control import Control
from railroad.domain.identity import Identity, EntityType
from railroad.domain.model import Model
from railroad.domain.asset import Asset
from railroad.domain.prototype import Prototype


@dataclass
class Car:
    """
    Digital representation of a physical railroad car.

    A car is composed of shared domain objects describing its
    identity, prototype, physical model, control, asset,
    and car type.
    """

    identity: Identity
    prototype: Prototype
    model: Model
    control: Control
    asset: Asset
    car_type: CarType

    def __post_init__(self) -> None:
        """Validate car invariants."""

        if not isinstance(self.identity, Identity):
            raise TypeError("identity must be an Identity.")

        if not isinstance(self.prototype, Prototype):
            raise TypeError("prototype must be a Prototype.")

        if not isinstance(self.model, Model):
            raise TypeError("model must be a Model.")

        if not isinstance(self.control, Control):
            raise TypeError("control must be an Control.")

        if not isinstance(self.asset, Asset):
            raise TypeError("asset must be an Asset.")

        if not isinstance(self.car_type, CarType):
            raise TypeError("car_type must be a CarType.")

    @property
    def id(self) -> str:
        """Return the persistent digital identity."""
        return self.identity.id

    @property
    def entity_type(self) -> EntityType:
        """Return the car entity type."""
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
    def road_number(self) -> str:
        """Return the car road number."""
        return self.identity.road_number

    @property
    def prototype_model(self) -> str:
        """Return the prototype model."""
        return self.prototype.model

    @property
    def nickname(self) -> str | None:
        """Return the prototype nickname."""
        return self.prototype.nickname

