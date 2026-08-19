#!/usr/bin/env python3
# iostream.py

"""
Filesystem I/O operations for the railroad persistence layer.

IOStream has no knowledge of railroad domain objects, JSON, IDs, or DAOs.
It provides only basic text-file and directory operations.
"""

from pathlib import Path


class IOStream:
    """Provide basic filesystem I/O operations."""

    def read(self, path: Path) -> str:
        """Read and return the contents of a text file."""

        return path.read_text(encoding="utf-8")

    def write(self, path: Path, content: str) -> None:
        """Write text content to a file.

        Parent directories are created when they do not already exist.
        """

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def exists(self, path: Path) -> bool:
        """Return True if the specified path exists."""

        return path.exists()

    def list(
        self,
        path: Path,
        pattern: str = "*.json",
    ) -> list[Path]:
        """Return matching files in a directory in sorted order."""

        return sorted(
            item
            for item in path.glob(pattern)
            if item.is_file()
        )
