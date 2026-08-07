#!/usr/bin/env python3

"""
locomotive : definition
filename   : locomotive.py

"""

from dataclasses import dataclass, asdict
from dataclassfactory import DataclassFactory

from datetime import date
from typing import Optional

@dataclass
class Prototype:
    # prototype
    builder: str
    railroad: str
    reporting_mark: str
    road_number: int
    nickname: str
    wheels: str

@dataclass
class Model:
    # model
    scale: str
    make: str
    product: str

@dataclass
class Electronics:
    # electronics
    dcc: bool
    sound: bool
    smoke: bool
    decoder: str
    address: int

@dataclass
class Ownership:
    # ownership
    status: str
    store: Optional[str] = None
    price: Optional[float] = None
    dated: Optional[date] = None

@dataclass
class Media:
    # media
    photo: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class Locomotive:
    prototype: Prototype
    model: Model
    electronics: Electronics
    ownership: Ownership
    media: Media

    @property
    def road_number(self) -> int:
        return self.prototype.road_number
    
    @property
    def reporting_mark(self):
        return self.prototype.reporting_mark
        
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_csv_row(cls, row):

        prototype = DataclassFactory.build(
            Prototype,
            row
        )

        model = DataclassFactory.build(
            Model,
            row
        )

        electronics = DataclassFactory.build(
            Electronics,
            row
        )

        ownership = DataclassFactory.build(
            Ownership,
            row
        )

        media = DataclassFactory.build(
            Media,
            row
        )

        return cls(
            prototype=prototype,
            model=model,
            electronics=electronics,
            ownership=ownership,
            media=media
        )
