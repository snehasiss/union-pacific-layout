#!/usr/bin/env python3

# test of Locomotive and Roster
# filename: test.py


from libs.roster import Roster
from pathlib import Path

def main():

    project_root = Path(__file__).resolve().parents[3]
    config_dir   = project_root / "config" / "loco" / "steam"

    input_file = config_dir / "steam.csv"
    output_dir = config_dir / "json"

    roster = Roster.from_csv(input_file)

    locomotive = roster.find(4014)

    print("running")
    print(locomotive)
    print("completed")

    roster.save(output_dir)

# --- main ---
if __name__ == "__main__":
    main()

## end

