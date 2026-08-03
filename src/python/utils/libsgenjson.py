#!/usr/bin/env python3

"""
libsgenjson.py

Library of class(es) to generate one JSON file per locomotive from a CSV inventory.

Author : Snehasis Sinha
Project: Union Pacific Layout
"""

import csv
import json
from pathlib import Path
from datetime import datetime, date
from typing import Any, Dict



class GenJSON:

    SCHEMA_VERSION = "1.0"

    def __init__(self,
                 csv_file: str,
                 output_directory: str) -> None:

        self.csv_file = Path(csv_file)
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

    ###########################################################################
    # Public API
    ###########################################################################

    def run(self) -> None:
        """Entry point."""

        for row in self._read_csv():

            locomotive  = self._build_locomotive(row)
            road_number = locomotive["prototype"]["roadNumber"]
            road_mark   = locomotive["prototype"]["reportingMark"]

            filename = self.output_directory / f"{road_mark}{road_number}.json"
            self._write_json(filename, locomotive)
            print(f"Created {filename.name}")

        print("\nGeneration complete.")

    ###########################################################################
    # CSV
    ###########################################################################

    def _read_csv(self):

        with open(self.csv_file,
                  newline="",
                  encoding="utf-8-sig") as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:
                yield {
                    key.lower(): self._clean(value)
                    for key, value in row.items()
                }

    ###########################################################################
    # Build JSON
    ###########################################################################

    def _build_locomotive(self,
                          row: Dict[str, Any]) -> Dict[str, Any]:

        locomotive = {
            "metadata": {
                "schemaVersion": self.SCHEMA_VERSION,
                "created": str(date.today()),
                "lastModified": str(date.today())
            },

            "prototype": {
                "builder":
                    self._title(row.get("builder")),

                "railroad":
                    self._title(row.get("railroad")),

                "reportingMark":
                    self._title(row.get("mark")).upper(),

                "roadNumber":
                    self._to_int(row.get("road number")),

                "nickname":
                    self._title(row.get("name")),

                "wheelArrangement":
                    self._title(row.get("wheels"))
            },

            "model": {

                "scale": "HO",

                "manufacturer":
                    row.get("make"),

                "product":
                    row.get("product"),

                "status":
                    row.get("status")

            },

            "electronics": {

                "dcc":
                    self._to_bool(row.get("dcc")),

                "sound":
                    self._to_bool(row.get("sound")),

                "smoke":
                    self._to_bool(row.get("smoke")),

                "decoder":
                    row.get("decoder"),

                "address":
                    self._to_int(row.get("address"))

            },

            "ownership": {

                "store":
                    self._title(row.get("store")),

                "purchasePriceUSD":
                    self._to_int(row.get("price")),

                "purchaseDate":
                    self._to_date(row.get("dated"))

            },

            "configuration": {},

            "maintenance": {
                "serviceHistory": []
            },

            "media": {
                "photo":
                    f"assets/photos/{self._title(row.get("mark"))}{self._to_int(row.get('road number'))}.png"
            },

            "notes": ""

        }

        return self._remove_empty(locomotive)

    ###########################################################################
    # JSON
    ###########################################################################

    def _write_json(self,
                    filename: Path,
                    data: Dict[str, Any]) -> None:

        with open(filename,
                  "w",
                  encoding="utf-8") as outfile:

            json.dump(
                data,
                outfile,
                indent=4,
                ensure_ascii=False
            )

    ###########################################################################
    # Utilities
    ###########################################################################

    @staticmethod
    def _clean(value):

        if value is None:
            return None

        value = value.strip()
        return value if value else None

    @staticmethod
    def _title(value):

        if value is None:
            return None

        return value.title()

    @staticmethod
    def _to_int(value):

        if value is None:
            return None

        try:
            return int(value)
        except ValueError:
            return value

    @staticmethod
    def _to_bool(value):

        if value is None:
            return None

        value = value.lower()

        if value in ("y", "yes", "true", "1"):
            return True

        if value in ("n", "no", "false", "0"):
            return False

        return None

    @staticmethod
    def _to_date(value):

        if value is None:
            return None

        try:
            return datetime.strptime(
                value,
                "%d-%b-%Y"
            ).strftime("%Y-%m-%d")

        except ValueError:
            return value

    def _remove_empty(self, obj):

        if isinstance(obj, dict):
            cleaned = {}

            for key, value in obj.items():
                value = self._remove_empty(value)

                if value is None:
                    continue

                if value == {}:
                    continue

                cleaned[key] = value
            return cleaned
        return obj


###############################################################################
# End
###############################################################################

