#!/usr/bin/env python3
"""
Generate one JSON file per locomotive from a CSV inventory.

Author : Snehasis Sinha
Project: Union Pacific Layout

Input:
    steam.csv

Output:
    config/locomotives/UP844.json
    config/locomotives/UP4014.json
    ...

"""

import csv
import json
from pathlib import Path
from datetime import date


###############################################################################
# Configuration
###############################################################################

CSV_FILE = "steam.csv"

OUTPUT_DIR = Path("json")

ROAD_NUMBER_FIELD = "road number"

SCHEMA_VERSION = "1.0"

FIELD_MAP = {
    "road number": ("prototype", "roadNumber"),
    "Name": ("prototype", "class"),
    "Wheels": ("prototype", "wheelArrangement"),
    "Builder": ("prototype", "builder"),
    "Brand": ("model", "manufacturer"),
    "product line": ("model", "productLine"),
    "decoder": ("electronics", "decoder"),
    "DCC": ("electronics", "dcc"),
    "Sound": ("electronics", "sound"),
    "Smoke": ("electronics", "smoke"),
}

###############################################################################
# Utility functions
###############################################################################


def clean(value):
    """Remove whitespace and return None for empty strings."""
    if value is None:
        return None

    value = value.strip()

    if value == "":
        return None

    return value


def to_bool(value):
    """Convert common Yes/No fields."""

    if value is None:
        return None

    value = value.strip().lower()

    if value in ("yes", "y", "true", "1"):
        return True

    if value in ("no", "n", "false", "0"):
        return False

    return value


def to_int(value):
    """Convert integer if possible."""

    if value is None:
        return None

    try:
        return int(value)
    except ValueError:
        return value


#########################################
# set the json attributes from column
#########################################
#for csv_field, (section, key) in FIELD_MAP.items():
#    if row.get(csv_field):
#        locomotive[section][key] = row[csv_field]


###############################################################################
# Create output directory
###############################################################################

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

###############################################################################
# Read CSV
###############################################################################

with open(CSV_FILE, newline="", encoding="utf-8-sig") as csvfile:

    reader = csv.DictReader(csvfile)

    for row in reader:

        # ------------------------------------------------------------------
        # Clean row
        # ------------------------------------------------------------------

        row = {k: clean(v) for k, v in row.items()}

        road_number = to_int(row.get(ROAD_NUMBER_FIELD))

        if road_number is None:
            print("Skipping row without road number.")
            continue

        filename = OUTPUT_DIR / f"UP{road_number}.json"

        # ------------------------------------------------------------------
        # Build rich JSON
        # ------------------------------------------------------------------

        locomotive = {

            "metadata": {
                "schemaVersion": SCHEMA_VERSION,
                "generatedOn": str(date.today())
            },

            "prototype": {
                "railroad": "Union Pacific",
                "roadNumber": road_number,
                "class": row.get("Name"),
                "wheelArrangement": row.get("wheels"),
                "builder": row.get("Builder"),
                "built": row.get("Built"),
                "retired": row.get("Retired")
            },

            "model": {
                "scale": "HO",
                "manufacturer": row.get("Brand"),
                "productLine": row.get("product line"),
                "catalogNumber": row.get("Catalog Number")
            },

            "electronics": {
                "decoder": row.get("decoder"),
                "dcc": to_bool(row.get("DCC")),
                "sound": to_bool(row.get("Sound")),
                "smoke": to_bool(row.get("Smoke")),
                "keepAlive": to_bool(row.get("Keep Alive"))
            },

            "ownership": {
                "purchaseDate": row.get("Purchase Date"),
                "purchasePrice": row.get("Price"),
                "seller": row.get("Store"),
                "condition": row.get("Condition")
            },

            "configuration": {
		"address": road_number

            },

            "maintenance": {
                "serviceHistory": []
            },

            "media": {
                "photo":
                    f"resources/photos/UP{road_number}.png"
            },

            "notes": row.get("Notes")
        }

        # ------------------------------------------------------------------
        # Remove empty fields recursively
        # ------------------------------------------------------------------

        def remove_empty(obj):

            if isinstance(obj, dict):

                cleaned = {}

                for k, v in obj.items():

                    v = remove_empty(v)

                    if v is None:
                        continue

                    if v == {}:
                        continue

                    cleaned[k] = v

                return cleaned

            return obj

        locomotive = remove_empty(locomotive)

        # ------------------------------------------------------------------
        # Write JSON
        # ------------------------------------------------------------------

        with open(filename, "w", encoding="utf-8") as f:

            json.dump(
                locomotive,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(f"Created {filename}")

print("\nDone.")
