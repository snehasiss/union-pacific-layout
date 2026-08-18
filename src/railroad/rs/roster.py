#!/usr/bin/env python3
# roster.py
#

"""
Locomotive roster domain object.

A Roster is the collection of locomotives represented in the
railroad's digital model.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from railroad.rs.loco import Loco


@dataclass
class Roster:
    """
    Collection of locomotives.
    """

    locos: list[loco] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate roster contents."""

        if not isinstance(self.locos, list):
            raise TypeError("locomotives must be a list.")

        for loco in self.locos:
            if not isinstance(loco, Loco):
                raise TypeError(
                    "roster can contain only Loco objects."
                )

    def add(self, loco: Loco) -> None:
        """Add a locomotive to the roster."""

        if not isinstance(loco, Loco):
            raise TypeError("locomotive must be a Loco.")

        if self.contains_id(loco.id):
            raise ValueError(
                f"Locomotive with id '{loco.id}' "
                "already exists in the roster."
            )

        self.locos.append(loco)

    def get(self, loco_id: str) -> Loco:
        """Return a locomotive by its persistent ID."""

        for loco in self.locos:
            if loco.id == loco_id:
                return loco

        raise KeyError(
            f"Locomotive with id '{loco_id}' was not found."
        )

    def remove(self, loco_id: str) -> Loco:
        """Remove and return a locomotive by its persistent ID."""

        for index, loco in enumerate(self.locos):
            if loco.id == loco_id:
                return self.locos.pop(index)

        raise KeyError(
            f"Locomotive with id '{loco_id}' was not found."
        )

    def contains_id(self, loco_id: str) -> bool:
        """Return whether a locomotive ID exists in the roster."""

        return any(
            loco.id == loco_id
            for loco in self.locos
        )

    def __len__(self) -> int:
        """Return the number of locomotives in the roster."""

        return len(self.locos)

    def __iter__(self):
        """Iterate over locomotives in roster order."""

        return iter(self.locos)

