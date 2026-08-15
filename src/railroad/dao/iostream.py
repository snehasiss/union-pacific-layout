#!/usr/bin/env python3
# iostream.py

"""
Low-level filesystem I/O for the DAO layer.
"""

from pathlib import Path
from typing import Union


class IOStream:
    """Perform basic text I/O operations on the filesystem."""

    def read(self, path: Union[str, Path]) -> str:
        """Read and return text from a file."""

        file_path = Path(path)
        return file_path.read_text(encoding="utf-8")

    def write(self, path: Union[str, Path], data: str) -> None:
        """Write text to a file."""

        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(data, encoding="utf-8")

    def exists(self, path: Union[str, Path]) -> bool:
        """Return True when the specified file exists."""

        return Path(path).is_file()

    def delete(self, path: Union[str, Path]) -> None:
        """Delete a file."""

        file_path = Path(path)
        file_path.unlink()

