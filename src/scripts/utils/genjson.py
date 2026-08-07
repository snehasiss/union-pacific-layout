#!/usr/bin/env python3

"""
csv_to_json.py

Generate one JSON file per locomotive from a CSV inventory.

Author : Snehasis Sinha
Project: Union Pacific Layout

Input:
    config/loco/steam/steam.csv

Output:
    config/loco/steam/json/UP844.json
    config/loco/steam/json/UP4014.json
    ...
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from datetime import datetime, date
from typing import Any, Dict

from libs.libsgenjson import GenJSON


###############################################################################
# Main
###############################################################################

def main():

    generator = GenJSON (
        csv_file="steam.csv",
        output_directory="json"
    )
    generator.run()


if __name__ == "__main__":
    main()

