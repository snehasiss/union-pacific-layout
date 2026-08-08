#!/usr/bin/env python3

# iostream.py : handles all io operations

import csv
import json
from pathlib import Path


class IOStream:

    CASE_PRESERVE = "preserve"
    CASE_LOWER = "lower"
    CASE_UPPER = "upper"
    CASE_TITLE = "title"
 
    VALID_CASES = {
        CASE_PRESERVE,
        CASE_LOWER,
        CASE_UPPER,
        CASE_TITLE,
    }

    def __init__(self, case=CASE_PRESERVE):
        if case not in self.VALID_CASES:
            raise ValueError(
                f"Invalid case option: {case}. "
                f"Valid options: {self.VALID_CASES}"
            )

        self.case = case

    # ---------------------------------------------------------------
    # CSV
    # ---------------------------------------------------------------

    def read_csv(self, filename):
        rows = []

        with open(
            filename,
            newline="",
            encoding="utf-8-sig"
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            for row in reader:
                rows.append(
                    self._normalize_dict(row)
                )

        return rows

    # ---------------------------------------------------------------
    # JSON
    # ---------------------------------------------------------------

    def write_json(self, filename, data):

        path = Path(filename)

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=4)


    def read_json(self, filename):
        with open(filename, "r", encoding="utf-8") as fp:
            return json.load(fp)

    # ---------------------------------------------------------------
    # Dictionary normalization
    # ---------------------------------------------------------------

    def _normalize_dict(self, data):
        return {
            key.strip().lower().replace(" ", "_"):
                self._normalize_value(value)

            for key, value in data.items()
        }

    def _normalize_value(self, value):
        if value is None:
            return None

        if not isinstance(value, str):
            return value

        value = value.strip()

        if self.case == self.CASE_LOWER:
            return value.lower()

        if self.case == self.CASE_UPPER:
            return value.upper()

        if self.case == self.CASE_TITLE:
            return value.title()

        return value
