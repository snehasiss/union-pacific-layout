from __future__ import annotations


def power(state: str, track: str | None = None) -> str:
    if state not in {"on", "off"}:
        raise ValueError("Power state must be 'on' or 'off'")
    code = "1" if state == "on" else "0"
    return f"<{code}{f' {track}' if track else ''}>"


def emergency_stop() -> str:
    return "<!>"


def status() -> str:
    return "<s>"


def throttle(address: int, speed: int, direction: str) -> str:
    if not 1 <= address <= 10293:
        raise ValueError("DCC address must be between 1 and 10293")
    if not 0 <= speed <= 126:
        raise ValueError("Speed must be between 0 and 126")
    if direction not in {"forward", "reverse"}:
        raise ValueError("Direction must be 'forward' or 'reverse'")
    return f"<t {address} {speed} {1 if direction == 'forward' else 0}>"


def function(address: int, number: int, active: bool) -> str:
    if not 1 <= address <= 10293:
        raise ValueError("DCC address must be between 1 and 10293")
    if not 0 <= number <= 68:
        raise ValueError("Function number must be between 0 and 68")
    return f"<F {address} {number} {1 if active else 0}>"
