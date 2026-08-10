#!/usr/bin/env python3

# locobuild.py builds locomotive, prepares roster, orchastrates io


from pathlib import Path

from libs.roster import Roster
from libs.locomotive import Locomotive
from libs.iostream import IOStream


def main():

    project_root = Path(__file__).resolve().parents[3]
    config_dir   = project_root / "config" / "loco" / "steam"

    input_file = config_dir / "steam.csv"
    output_dir = config_dir / "json"

    io = IOStream (case=IOStream.CASE_TITLE)
    rows = io.read_csv(input_file)

    roster = Roster ()

    for row in rows:
        roster.add (Locomotive.from_record(row))

    for loco in roster:
        filename = (
            f"{loco.reporting_mark}"
            f"{loco.road_number}.json"
            )
        io.write_json (
            output_dir / filename,
            loco.to_dict()
            )


# --- main ---
if __name__ == "__main__":
    main()

## end

