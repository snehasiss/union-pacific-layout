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

from railroad.locomotive.locomotive import Locomotive


@dataclass
class Roster:
    """
    Collection of locomotives.
    """

    locomotives: list[Locomotive] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate roster contents."""

        if not isinstance(self.locomotives, list):
            raise TypeError("locomotives must be a list.")

        for locomotive in self.locomotives:
            if not isinstance(locomotive, Locomotive):
                raise TypeError(
                    "roster can contain only Locomotive objects."
                )

    def add(self, locomotive: Locomotive) -> None:
        """Add a locomotive to the roster."""

        if not isinstance(locomotive, Locomotive):
            raise TypeError("locomotive must be a Locomotive.")

        if self.contains_id(locomotive.id):
            raise ValueError(
                f"Locomotive with id '{locomotive.id}' "
                "already exists in the roster."
            )

        self.locomotives.append(locomotive)

    def get(self, locomotive_id: str) -> Locomotive:
        """Return a locomotive by its persistent ID."""

        for locomotive in self.locomotives:
            if locomotive.id == locomotive_id:
                return locomotive

        raise KeyError(
            f"Locomotive with id '{locomotive_id}' was not found."
        )

    def remove(self, locomotive_id: str) -> Locomotive:
        """Remove and return a locomotive by its persistent ID."""

        for index, locomotive in enumerate(self.locomotives):
            if locomotive.id == locomotive_id:
                return self.locomotives.pop(index)

        raise KeyError(
            f"Locomotive with id '{locomotive_id}' was not found."
        )

    def contains_id(self, locomotive_id: str) -> bool:
        """Return whether a locomotive ID exists in the roster."""

        return any(
            locomotive.id == locomotive_id
            for locomotive in self.locomotives
        )

    def __len__(self) -> int:
        """Return the number of locomotives in the roster."""

        return len(self.locomotives)

    def __iter__(self):
        """Iterate over locomotives in roster order."""

        return iter(self.locomotives)

