from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProtocolEvent:
    type: str
    data: dict[str, object]
    raw: str


def parse_frame(frame: str) -> ProtocolEvent:
    body = frame[1:-1].strip() if frame.startswith("<") and frame.endswith(">") else frame
    if body == "p1":
        return ProtocolEvent("power", {"state": "on"}, frame)
    if body == "p0":
        return ProtocolEvent("power", {"state": "off"}, frame)
    if body.startswith("iDCC-EX"):
        return ProtocolEvent("system", {"identity": body[1:]}, frame)
    if body.startswith("l "):
        parts = body.split()
        if len(parts) >= 5:
            try:
                address = int(parts[1])
                speed_byte = int(parts[3])
                function_map = int(parts[4])
            except ValueError:
                pass
            else:
                if speed_byte >= 128:
                    direction = "forward"
                    speed = 0 if speed_byte == 128 else max(0, speed_byte - 129)
                else:
                    direction = "reverse"
                    speed = 0 if speed_byte == 0 else max(0, speed_byte - 1)
                return ProtocolEvent(
                    "locomotive",
                    {
                        "address": address,
                        "speed": speed,
                        "direction": direction,
                        "functions": {
                            str(number): bool(function_map & (1 << number))
                            for number in range(16)
                        },
                    },
                    frame,
                )
    return ProtocolEvent("protocol", {"message": body}, frame)
