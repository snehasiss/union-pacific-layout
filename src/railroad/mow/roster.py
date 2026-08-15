#!/usr/bin/env python3
# roster.py

"""
Maintenance-of-Way roster domain object.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from railroad.mow.mow import MOW


@dataclass
class Roster:
    """
    Collection of Maintenance-of-Way assets.
    """

    mow: list[MOW] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate roster contents."""

        if not isinstance(self.mow, list):
            raise TypeError("mow must be a list.")

        for item in self.mow:
            if not isinstance(item, MOW):
                raise TypeError(
                    "roster can contain only MOW objects."
                )

    def add(self, mow: MOW) -> None:
        """Add an MOW asset to the roster."""

        if not isinstance(mow, MOW):
            raise TypeError("mow must be an MOW.")

        if self.contains_id(mow.id):
            raise ValueError(
                f"MOW with id '{mow.id}' already exists in the roster."
            )

        self.mow.append(mow)

    def get(self, mow_id: str) -> MOW:
        """Return an MOW asset by its persistent ID."""

        for item in self.mow:
            if item.id == mow_id:
                return item

        raise KeyError(
            f"MOW with id '{mow_id}' was not found."
        )

    def remove(self, mow_id: str) -> MOW:
        """Remove and return an MOW asset by its persistent ID."""

        for index, item in enumerate(self.mow):
            if item.id == mow_id:
                return self.mow.pop(index)

        raise KeyError(
            f"MOW with id '{mow_id}' was not found."
        )

    def contains_id(self, mow_id: str) -> bool:
        """Return whether an MOW ID exists in the roster."""

        return any(
            item.id == mow_id
            for item in self.mow
        )

    def __len__(self) -> int:
        """Return the number of MOW assets."""

        return len(self.mow)

    def __iter__(self):
        """Iterate over MOW assets in roster order."""

        return iter(self.mow)

