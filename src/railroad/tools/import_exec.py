#!/usr/bin/env python3
# railroad/tools/import_exec.py
#

"""
Execute railroad asset imports.

The executable layer discovers import source files and delegates
domain construction to the appropriate import class and persistence
to the appropriate DAO.
"""

from __future__ import annotations

from pathlib import Path

from railroad.config import Config
from railroad.dao.loco import LocoDAO
from railroad.tools.loco_import import LocoImport


ROOT = Path(__file__).resolve().parents[3]
IMPORT_DIRECTORY = ROOT / "src" / "railroad" / "tools" / "imports"
CONFIG_FILE = ROOT / "config" / "railroad-conf.json"


def import_locos(
    config: Config,
    import_directory: Path,
) -> int:
    """Import all locomotive CSV files and persist them as JSON."""

    dao = LocoDAO(config)

    files = sorted(import_directory.glob("*.csv"))

    count = 0

    for path in files:
        locos = LocoImport.import_file(path)

        for loco in locos:
            dao.save(loco)
            count += 1

    return count


def main() -> None:
    """Run all configured railroad asset imports."""

    config = Config(CONFIG_FILE)

    count = import_locos(
        config=config,
        import_directory=IMPORT_DIRECTORY,
    )

    print(f"Imported {count} locomotives.")


if __name__ == "__main__":
    main()
