#!/usr/bin/env python3
# railroad/operation/loco.py

"""Locomotive operational facade."""

from __future__ import annotations

from railroad.config import Config
from railroad.dao.loco import LocoDAO
from railroad.domain.identity import EntityType
from railroad.operation.asset import Asset
from railroad.rs.loco import Loco


class LocoOps(Asset[Loco]):
    """Operations for persisted locomotives."""

    def __init__(self, config: Config) -> None:
        super().__init__(LocoDAO(config), Loco, EntityType.LOCO, "L")
