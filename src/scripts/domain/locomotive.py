#!/usr/bin/env python3

"""
locomotive : definition
filename   : locomotive.py

"""

from dataclasses import dataclass, asdict
from libs.dataclassfactory import DataclassFactory
from datetime import date

from datetime import date
from typing import Optional

@dataclass
class Prototype:
    # prototype
    builder: str
    railroad: str
    reporting_mark: str
    road_number: int

@dataclass
class Model:
    # model
    make: str
    product: str
    scale: str = "HO"

@dataclass
class Control:
    # control system
    dcc: bool
    sound: bool
    smoke: bool
    decoder: str
    address: int

@dataclass
class Ownership:
    # ownership
    acquired: bool = True
    store: Optional[str] = None
    price: Optional[float] = None
    dated: Optional[date] = None

@dataclass
class Media:
    # media
    photo: Optional[str] = None
    notes: Optional[str] = None

@dataclass 
class Engine:
	pass

@dataclass
class Steam (Engine):
	loco_class: str
	wheels: str
	cylinders: int

@dataclass 
class Diesel (Engine):
	loco_model: str
	service_type: str
	horsepower: int

@dataclass
class mow (Engine):
	equipment_type: str
	self_propelled: bool = True

@dataclass
class Locomotive:
	type: str
    prototype: Prototype
    model: Model
    control: Control
    ownership: Ownership
    media: Media
	engine: Engine

    @property
    def road_number(self) -> int:
        return self.prototype.road_number
    
    @property
    def reporting_mark(self):
        return self.prototype.reporting_mark
        
	def __post_init__(self):
		match self.type:
			case "steam":
				engine = Steam ()

			case "diesel":
				engine = Diesel ()

			case _:
				engine = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def to_dict(self):
        data= asdict(self)

        if isinstance(data["ownership"]["dated"], date):
            data["ownership"]["dated"] = \
            data["ownership"]["dated"].isoformat()

        return data

    @classmethod
    def from_record(cls, row):

        prototype = DataclassFactory.build (Prototype, row)
        model = DataclassFactory.build (Model, row)
        electronics = DataclassFactory.build (Electronics, row)
        ownership = DataclassFactory.build (Ownership, row)
        media = DataclassFactory.build (Media, row)

        return cls(
            prototype=prototype,
            model=model,
            electronics=electronics,
            ownership=ownership,
            media=media
        )
