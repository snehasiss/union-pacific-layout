#!/usr/bin/env python3
# railroad/tools/loco_import.py
#

"""
Import locomotive data from CSV into Loco domain objects.

The importer translates the external CSV representation into the
railroad domain model. Persistence is deliberately handled by LocoDAO.
"""

from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path

from railroad.dao.loco import LocoDAO
from railroad.domain.asset import Asset, AssetStatus
from railroad.domain.control import Control, ControlType
from railroad.domain.identity import EntityType, Identity
from railroad.domain.model import Model
from railroad.domain.prototype import Prototype, Purpose
from railroad.rs.loco import Loco
from railroad.rs.loco_type import LocoType


class LocoImport:
    """Import locomotives from the railroad CSV import files."""

    IMPORT_DIRECTORY = Path(__file__).resolve().parent / "imports"

    STEAM_FILE = IMPORT_DIRECTORY / "steam.csv"
    DIESEL_FILE = IMPORT_DIRECTORY / "diesel.csv"

    @classmethod
    def import_file(cls, path: str | Path) -> list[Loco]:
        """Read a locomotive CSV file and return domain objects."""
        path = Path(path)

        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError("CSV file has no header.")

            rows = cls._normalise_rows(reader)

        return [cls._from_row(row) for row in rows]

    @classmethod
    def import_all(cls) -> list[Loco]:
        """Import both steam and diesel locomotive CSV files."""
        return cls.import_file(cls.STEAM_FILE) + cls.import_file(
            cls.DIESEL_FILE
        )

    @classmethod
    def import_and_save(
        cls,
        dao: LocoDAO,
        path: str | Path,
    ) -> list[Loco]:
        """Import locomotives from CSV and persist them using LocoDAO."""
        locos = cls.import_file(path)

        for loco in locos:
            dao.save(loco)

        return locos

    @staticmethod
    def _normalise_rows(
        reader: csv.DictReader,
    ) -> list[dict[str, str]]:
        """Normalise CSV headers and row values."""
        rows = []

        for source_row in reader:
            row = {}

            for key, value in source_row.items():
                if key is None:
                    continue

                normalised_key = key.strip().lower()
                row[normalised_key] = (
                    value.strip() if value is not None else ""
                )

            rows.append(row)

        return rows

    @classmethod
    def _from_row(cls, row: dict[str, str]) -> Loco:
        """Create a Loco domain object from one CSV row."""
        loco_type = LocoType(row["locotype"].lower())

        identity = Identity.create(
            prefix="L",
            entity_type=EntityType.LOCO,
            railroad=row["railroad"],
            reporting_mark=row["reporting_mark"].upper(),
            road_number=row["road_number"],
        )

        prototype = Prototype(
            builder=row["builder"],
            model=row["loco_model"],
            nickname=cls._optional_string(row["nickname"]),
            purpose=Purpose(row["purpose"].lower()),
        )

        model = Model(
            manufacturer=cls._optional_string(row["make"]),
            product=None,
        )

        control = cls._create_control(row)
        asset = cls._create_asset(row)

        return Loco(
            identity=identity,
            loco_type=loco_type,
            prototype=prototype,
            model=model,
            control=control,
            asset=asset,
        )

    @staticmethod
    def _create_control(row: dict[str, str]) -> Control:
        """Translate CSV control information into Control."""
        is_dcc = LocoImport._boolean(row["dcc"])

        control_type = (
            ControlType.DCC if is_dcc else ControlType.DC
        )

        if control_type == ControlType.DCC:
            decoder = LocoImport._optional_string(row["decoder"])
            address = LocoImport._optional_int(row["address"])

            return Control(
                type=control_type,
                light=LocoImport._boolean(row["light"]),
                sound=LocoImport._boolean(row["sound"]),
                smoke=LocoImport._boolean(row["smoke"]),
                decoder=decoder,
                address=address,
            )

        return Control(
            type=ControlType.DC,
            light=LocoImport._boolean(row["light"]),
            sound=LocoImport._boolean(row["sound"]),
            smoke=LocoImport._boolean(row["smoke"]),
            decoder=None,
            address=0,
        )

    @staticmethod
    def _create_asset(row: dict[str, str]) -> Asset:
        """Translate CSV acquisition information into Asset."""
        price = LocoImport._optional_float(row["price"])
        acquired = LocoImport._optional_date(row["dated"])

        return Asset(
            status=AssetStatus(row["status"].lower()),
            source=LocoImport._optional_string(row["store"]),
            price=price,
            acquired=acquired,
        )

    @staticmethod
    def _boolean(value: str) -> bool:
        """Convert a CSV yes/no value to bool."""
        value = value.strip().lower()

        if value == "yes":
            return True

        if value == "no":
            return False

        raise ValueError(
            f"Invalid boolean value '{value}'. Expected yes or no."
        )

    @staticmethod
    def _optional_string(value: str) -> str | None:
        """Return a stripped string or None for an empty value."""
        value = value.strip()
        return value if value else None

    @staticmethod
    def _optional_int(value: str) -> int | None:
        """Convert an optional CSV integer."""
        value = value.strip()

        if not value:
            return None

        return int(value)

    @staticmethod
    def _optional_float(value: str) -> float | None:
        """Convert an optional CSV number."""
        value = value.strip()

        if not value:
            return None

        return float(value)

    @staticmethod
    def _optional_date(value: str) -> date | None:
        """Convert an optional CSV date.

        Supports the two formats currently present in the CSV files:
        DD-Mon-YYYY and YYYY-MM-DD.
        """
        value = value.strip()

        if not value:
            return None

        for format_string in ("%d-%b-%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, format_string).date()
            except ValueError:
                continue

        raise ValueError(f"Invalid acquisition date '{value}'.")

