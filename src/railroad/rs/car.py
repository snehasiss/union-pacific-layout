#!/usr/bin/env python3
# railroad/rs/car.py
#

"""Car domain entity."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from railroad.domain.control import Control
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.prototype import Prototype


class CarType(Enum):
    """Classification of railroad cars."""

    PASSENGER = "passenger"
    OBSERVATION = "observation"
    LUGGAGE = "luggage"
    BRAKEVAN = "brakevan"
    HOPPER = "hopper"
    GONDOLA = "gondola"
    WAGON = "wagon"
    TANKER = "tanker"
    FLATCAR = "flatcar"
    INTERMODAL = "intermodal"
    REEFER = "reefer"
    POWER = "power"
    PANTRY = "pantry"
    CABOOSE = "caboose"


@dataclass
class Car:
    """Digital representation of a physical railroad car."""

    identity: Identity
    prototype: Prototype
    model: Model
    control: Control
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
        if not isinstance(self.car_type, CarType):
            raise TypeError("car_type must be a CarType.")

    @property
    def id(self) -> str:
        return self.identity.id

    @property
    def entity_type(self) -> EntityType:
        return self.identity.entity_type

    @property
    def railroad(self) -> str:
        return self.identity.railroad

    @property
    def reporting_mark(self) -> str:
        return self.identity.reporting_mark

    @property
    def road_number(self) -> str:
        return self.identity.road_number

    @property
    def prototype_model(self) -> str:
        return self.prototype.model

    @property
    def nickname(self) -> str | None:
        return self.prototype.nickname
