#!/usr/bin/env python3
# mow_type.py

"""
Maintenance-of-Way equipment classification.
"""

from enum import Enum


class MOWType(Enum):
    """Classification of Maintenance-of-Way equipment."""

    # General MOW equipment
    CRANE = "crane"
    SNOWPLOW = "snowplow"
    CLEANER = "cleaner"

    # Self-propelled MOW equipment
    TAMPER = "tamper"
    MPV = "mpv"

