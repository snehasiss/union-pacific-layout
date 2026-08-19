#!/usr/bin/env python3
# test_iostream.py

"""
Tests for IOStream.
"""

from pathlib import Path

import pytest

from railroad.dao.iostream import IOStream


@pytest.fixture
def stream() -> IOStream:
    """Create an IOStream for testing."""

    return IOStream()


def test_iostream_can_be_created() -> None:
    """IOStream can be instantiated."""

    stream = IOStream()

    assert isinstance(stream, IOStream)


def test_write_creates_file(
    stream: IOStream,
    tmp_path: Path,
) -> None:
    """Writing creates the requested file."""

    path = tmp_path / "test.txt"

    stream.write(path, "hello")

    assert path.is_file()


def test_write_creates_parent_directories(
    stream: IOStream,
    tmp_path: Path,
) -> None:
    """Writing creates missing parent directories."""

    path = tmp_path / "nested" / "directory" / "test.txt"

    stream.write(path, "hello")

    assert path.is_file()


def test_read_returns_file_contents(
    stream: IOStream,
    tmp_path: Path,
) -> None:
    """Reading returns the complete file contents."""

    path = tmp_path / "test.txt"
    path.write_text("hello world", encoding="utf-8")

    result = stream.read(path)

    assert result == "hello world"


def test_write_and_read_round_trip(
    stream: IOStream,
    tmp_path: Path,
) -> None:
    """Written text can be read back unchanged."""

    path = tmp_path / "test.txt"
    content = "Union Pacific Railroad\nL001\nUP 844"

    stream.write(path, content)

    assert stream.read(path) == content


def test_exists_returns_true_for_existing_file(
    stream: IOStream,
    tmp_path: Path,
) -> None:
    """exists returns True for an existing file."""

    path = tmp_path / "test.txt"
    path.write_text("hello", encoding="utf-8")

    assert stream.exists(path) is True


def test_exists_returns_false_for_missing_file(
    stream: IOStream,
    tmp_path: Path,
) -> None:
    """exists returns False for a missing file."""

    path = tmp_path / "missing.txt"

    assert stream.exists(path) is False


def test_exists_for_directory(
    stream: IOStream,
    tmp_path: Path,
) -> None:
    """exists() returns True for an existing directory."""

    directory = tmp_path / "loco"
    directory.mkdir()

    assert stream.exists(directory) is True


def test_read_missing_file_raises_error(
    stream: IOStream,
    tmp_path: Path,
) -> None:
    """Reading a missing file raises FileNotFoundError."""

    path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        stream.read(path)


