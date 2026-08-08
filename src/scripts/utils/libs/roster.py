#!/usr/bin/env python3

#
# roster.py
#

from libs.locomotive import Locomotive
from datetime import date
from pathlib import Path
import csv
import json

class Roster:
    def __init__(self):
        self._locomotives: dict[int, Locomotive] = {}

    def add(self, locomotive: Locomotive):
        self._locomotives[locomotive.prototype.road_number] = locomotive

    def find(self, road_number: int):
        return self._locomotives.get(road_number)

    def __len__(self):
        return len(self._locomotives)

    def __iter__(self):
        return iter(self._locomotives.values())

    @staticmethod
    def _clean(value):
        if value is None:
            return None

        value = value.strip()
        return value if value else None


    def save(self, output_dir):
        output_path = Path (output_dir)
        output_path.mkdir (parents=True, exist_ok=True)

        for loco in self:
            filename = f"{loco.reporting_mark}{loco.road_number}.json"
            filepath = output_path / filename

            with open (filepath, "w", encoding="utf-8") as fp:
                json.dump (
                    loco.to_dict(),
                    fp,
                    indent=4
                    ) 

    def load(self, filename):
        with open(filename) as fp:
            data = json.load(fp)
        loco = Locomotive.from_dict(data)
        self.add(loco)
    #

    @staticmethod
    def _normalize_row(row):
        normalized = {
            key.strip().lower().replace(" ", "_"): Roster._clean(value)
            for key, value in row.items()
        }

        #print (normalized)
        return normalized

    @classmethod
    def from_csv(cls, filename):
        roster = cls()

        with open(filename, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                normalized = cls._normalize_row(row)
                #print ("a", normalized, "b\n")
                roster.add(Locomotive.from_csv_row(normalized))

        #print (roster)
        return roster
