#!/usr/bin/env python3
# roster.py
#

"""
Car roster domain object.

A Roster is the collection of cars represented in the
railroad's digital model.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from railroad.car.car import Car


@dataclass
class Roster:
    """
    Collection of railroad cars.
    """

    cars: list[Car] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate roster contents."""

        if not isinstance(self.cars, list):
            raise TypeError("cars must be a list.")

        for car in self.cars:
            if not isinstance(car, Car):
                raise TypeError(
                    "roster can contain only Car objects."
                )

    def add(self, car: Car) -> None:
        """Add a car to the roster."""

        if not isinstance(car, Car):
            raise TypeError("car must be a Car.")

        if self.contains_id(car.id):
            raise ValueError(
                f"Car with id '{car.id}' already exists in the roster."
            )

        self.cars.append(car)

    def get(self, car_id: str) -> Car:
        """Return a car by its persistent ID."""

        for car in self.cars:
            if car.id == car_id:
                return car

        raise KeyError(
            f"Car with id '{car_id}' was not found."
        )

    def remove(self, car_id: str) -> Car:
        """Remove and return a car by its persistent ID."""

        for index, car in enumerate(self.cars):
            if car.id == car_id:
                return self.cars.pop(index)

        raise KeyError(
            f"Car with id '{car_id}' was not found."
        )

    def contains_id(self, car_id: str) -> bool:
        """Return whether a car ID exists in the roster."""

        return any(
            car.id == car_id
            for car in self.cars
        )

    def __len__(self) -> int:
        """Return the number of cars in the roster."""

        return len(self.cars)

    def __iter__(self):
        """Iterate over cars in roster order."""

        return iter(self.cars)

