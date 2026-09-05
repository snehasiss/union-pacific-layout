from __future__ import annotations

import logging
import queue
import threading
from collections.abc import Callable
from typing import Any

import serial

from .discovery import resolve_port
from .framing import DccExFramer
from .parser import ProtocolEvent, parse_frame

EventCallback = Callable[[ProtocolEvent], None]
ConnectionCallback = Callable[[str, str | None, str | None], None]
LOGGER = logging.getLogger(__name__)


class SerialRequestTimeout(RuntimeError):
    pass


class SerialController:
    def __init__(
        self,
        config: dict[str, Any],
        on_event: EventCallback,
        on_connection: ConnectionCallback,
    ) -> None:
        self._config = config
        self._on_event = on_event
        self._on_connection = on_connection
        self._serial: serial.Serial | None = None
        self._port: str | None = None
        self._running = threading.Event()
        self._write_lock = threading.Lock()
        self._request_lock = threading.Lock()
        self._pending_lock = threading.Lock()
        self._pending_matcher: Callable[[ProtocolEvent], bool] | None = None
        self._pending_event = threading.Event()
        self._pending_response: ProtocolEvent | None = None
        self._commands: queue.Queue[str] = queue.Queue()
        self._thread: threading.Thread | None = None

    @property
    def connected(self) -> bool:
        return bool(self._serial and self._serial.is_open and self._running.is_set())

    def connect(self, requested_port: str | None = None) -> str:
        if self.connected:
            return self._port or ""
        port = resolve_port(requested_port or self._config["port"])
        self._on_connection("connecting", port, None)
        try:
            self._serial = serial.Serial(
                port=port,
                baudrate=self._config["baudRate"],
                timeout=self._config["readTimeoutSeconds"],
                write_timeout=self._config["writeTimeoutSeconds"],
            )
        except (serial.SerialException, OSError) as exc:
            if self._serial and self._serial.is_open:
                self._serial.close()
            self._serial = None
            self._on_connection("error", port, str(exc))
            raise RuntimeError(f"Unable to open serial port {port}: {exc}") from exc
        self._port = port
        self._running.set()
        self._thread = threading.Thread(target=self._run, name="csb1-serial", daemon=True)
        self._thread.start()
        self._on_connection("connected", port, None)
        return port

    def disconnect(self) -> None:
        self._running.clear()
        self._pending_event.set()
        if self._thread and self._thread is not threading.current_thread():
            self._thread.join(timeout=2)
        if self._serial and self._serial.is_open:
            self._serial.close()
        port = self._port
        self._serial = None
        self._thread = None
        self._on_connection("disconnected", port, None)

    def send(self, command: str, priority: bool = False) -> None:
        if not self.connected:
            raise RuntimeError("CSB1 serial connection is not active")
        if not command.startswith("<") or not command.endswith(">"):
            raise ValueError("DCC-EX commands must be enclosed by '<' and '>'")
        if self._request_lock.locked() and not priority:
            raise RuntimeError("CSB1 programming transaction is in progress")
        if priority:
            self._write(command)
        else:
            self._commands.put(command)

    def request(
        self,
        command: str,
        matcher: Callable[[ProtocolEvent], bool],
        timeout: float = 15.0,
    ) -> ProtocolEvent:
        if not self.connected:
            raise RuntimeError("CSB1 serial connection is not active")
        with self._request_lock:
            if not self._commands.empty():
                raise RuntimeError("CSB1 has pending operating commands; retry programming shortly")
            self._pending_event.clear()
            with self._pending_lock:
                self._pending_matcher = matcher
                self._pending_response = None
            try:
                self._write(command)
                if not self._pending_event.wait(timeout):
                    LOGGER.warning("Timed out waiting for CSB1 response to %s", command)
                    raise SerialRequestTimeout("CSB1 did not confirm the programming command")
                with self._pending_lock:
                    if self._pending_response is None:
                        raise RuntimeError("CSB1 disconnected during the programming command")
                    return self._pending_response
            finally:
                with self._pending_lock:
                    self._pending_matcher = None
                    self._pending_response = None

    def _write(self, command: str) -> None:
        if not self._serial:
            raise RuntimeError("CSB1 serial connection is not active")
        with self._write_lock:
            LOGGER.debug("CSB1 TX: %s", command)
            self._serial.write(command.encode("ascii"))
            self._serial.flush()

    def _run(self) -> None:
        framer = DccExFramer()
        try:
            while self._running.is_set() and self._serial:
                while True:
                    try:
                        self._write(self._commands.get_nowait())
                    except queue.Empty:
                        break
                data = self._serial.read(self._serial.in_waiting or 1)
                with self._pending_lock:
                    request_pending = self._pending_matcher is not None
                if request_pending and data:
                    LOGGER.info("CSB1 RX during programming request: %r", data)
                for frame in framer.feed(data):
                    LOGGER.debug("CSB1 RX: %s", frame)
                    event = parse_frame(frame)
                    with self._pending_lock:
                        if self._pending_matcher and self._pending_matcher(event):
                            self._pending_response = event
                            self._pending_event.set()
                    self._on_event(event)
        except (serial.SerialException, OSError) as exc:
            self._running.clear()
            self._on_connection("error", self._port, str(exc))
