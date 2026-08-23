#!/usr/bin/env python3
# railroad/operation/mow.py

"""Maintenance-of-Way operational facade."""

from __future__ import annotations

from railroad.config import Config
from railroad.dao.mow import MowDAO
from railroad.domain.identity import EntityType
from railroad.operation.asset import Asset
from railroad.rs.mow import MOW


class MowOps(Asset[MOW]):
    """Operations for persisted MOW equipment."""

    def __init__(self, config: Config) -> None:
        super().__init__(MowDAO(config), MOW, EntityType.MOW, "M")
