#!/usr/bin/env python3
# loco_type.py: defines locomotive types like diesel or steam

from enum import Enum


class LocoType(Enum):
    STEAM = "steam"
    DIESEL = "diesel"
