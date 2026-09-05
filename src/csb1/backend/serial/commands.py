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


def read_cv(cv: int, callback: int, callback_sub: int = 0) -> str:
    if not 1 <= cv <= 1024:
        raise ValueError("CV number must be between 1 and 1024")
    if not 0 <= callback <= 32767 or not 0 <= callback_sub <= 32767:
        raise ValueError("CV callback numbers must be between 0 and 32767")
    return f"<R {cv} {callback} {callback_sub}>"


def write_cv(cv: int, value: int) -> str:
    if not 1 <= cv <= 1024:
        raise ValueError("CV number must be between 1 and 1024")
    if not 0 <= value <= 255:
        raise ValueError("CV value must be between 0 and 255")
    return f"<W {cv} {value}>"


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
