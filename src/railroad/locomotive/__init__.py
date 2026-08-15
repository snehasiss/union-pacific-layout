#!/usr/bin/env python3
# __init__.py
#

"""
Locomotive domain package.
"""

from railroad.locomotive.locomotive import Locomotive
from railroad.locomotive.roster import Roster

__all__ = [
    "Locomotive",
    "Roster",
]