#!/usr/bin/env python3
# railroad/operation/car.py

"""Railroad car operational facade."""

from __future__ import annotations

from railroad.config import Config
from railroad.dao.car import CarDAO
from railroad.domain.identity import EntityType
from railroad.operation.asset import Asset
from railroad.rs.car import Car


class CarOps(Asset[Car]):
    """Operations for persisted railroad cars."""

    def __init__(self, config: Config) -> None:
        super().__init__(CarDAO(config), Car, EntityType.CAR, "C")
