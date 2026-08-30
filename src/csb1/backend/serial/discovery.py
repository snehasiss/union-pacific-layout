from __future__ import annotations

from serial.tools import list_ports


def available_ports() -> list[dict[str, object]]:
    return [
        {
            "device": port.device,
            "description": port.description,
            "manufacturer": port.manufacturer,
            "vid": port.vid,
            "pid": port.pid,
            "serialNumber": port.serial_number,
        }
        for port in list_ports.comports()
    ]


def resolve_port(configured_port: str) -> str:
    if configured_port != "auto":
        return configured_port
    ports = available_ports()
    likely = [
        port for port in ports
        if any(token in str(port.get("device", "")).lower() for token in ("usbmodem", "usbserial", "ttyacm"))
    ]
    if len(likely) == 1:
        return str(likely[0]["device"])
    if not likely:
        raise RuntimeError("No likely USB serial device found")
    raise RuntimeError("Multiple USB serial devices found; select one explicitly")

