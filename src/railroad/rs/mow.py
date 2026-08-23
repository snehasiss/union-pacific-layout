#!/usr/bin/env python3
# railroad/rs/mow.py
#

"""
Maintenance-of-Way domain entity.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from railroad.domain.control import Control
from railroad.domain.identity import Identity, EntityType
from railroad.domain.model import Model
from railroad.domain.asset import Asset
from railroad.domain.prototype import Prototype


class MOWType(Enum):
    """Classification of Maintenance-of-Way equipment."""

    CRANE = "crane"
    SNOWPLOW = "snowplow"
    CLEANER = "cleaner"
    TAMPER = "tamper"
    MPV = "mpv"


@dataclass
class MOW:
    """Digital representation of a Maintenance-of-Way asset."""

    identity: Identity
    prototype: Prototype
    model: Model
    control: Control
    asset: Asset
    mow_type: MOWType
    self_propelled: bool

    def __post_init__(self) -> None:
        """Validate MOW invariants."""

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
        if not isinstance(self.mow_type, MOWType):
            raise TypeError("mow_type must be an MOWType.")
        if not isinstance(self.self_propelled, bool):
            raise TypeError("self_propelled must be a bool.")

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
