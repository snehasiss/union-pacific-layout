from __future__ import annotations


class DccExFramer:
    """Extract complete `<...>` DCC-EX frames from arbitrary serial chunks."""

    def __init__(self, maximum_frame_length: int = 4096) -> None:
        self._buffer = ""
        self._maximum_frame_length = maximum_frame_length

    def feed(self, data: bytes | str) -> list[str]:
        text = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else data
        self._buffer += text
        frames: list[str] = []

        while True:
            start = self._buffer.find("<")
            if start < 0:
                self._buffer = self._buffer[-self._maximum_frame_length :]
                break
            if start:
                self._buffer = self._buffer[start:]
            end = self._buffer.find(">", 1)
            if end < 0:
                if len(self._buffer) > self._maximum_frame_length:
                    self._buffer = ""
                break
            frames.append(self._buffer[: end + 1])
            self._buffer = self._buffer[end + 1 :]
        return frames

