#!/usr/bin/env python3
# railroad/rs/car_type.py
#

"""
Car type classification.
"""

from enum import Enum


class CarType(Enum):
    """Classification of railroad cars."""

    # Passenger
    PASSENGER = "passenger"
    OBSERVATION = "observation"
    LUGGAGE = "luggage"
    BRAKEVAN = "brakevan"

    # Freight
    HOPPER = "hopper"
    GONDOLA = "gondola"
    WAGON = "wagon"
    TANKER = "tanker"
    FLATCAR = "flatcar"
    INTERMODAL = "intermodal"
    REEFER = "reefer"

    # Special
    POWER = "power"
    PANTRY = "pantry"
    CABOOSE = "caboose"
