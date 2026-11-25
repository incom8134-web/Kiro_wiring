"""UART measurement lines on the Jetson 40-pin UART.

Header pins 8 (TX) and 10 (RX) are ``/dev/ttyTHS1`` on the Nano developer kit,
3.3 V, behind the carrier TXB0108. This output is a log, not a second SOC
engine. A missing port is reported and ignored unless ``required`` is set.
"""

from __future__ import annotations

HEADER = "unix_s,voltage_v,current_a,power_w,soc_percent,capacity_ah,energy_wh,status,faults"


def _field(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def format_line(snapshot: dict) -> str:
    faults = "|".join(snapshot.get("faults") or [])
    columns = [
        _field(snapshot.get("updated_unix")),
        _field(snapshot.get("voltage_v")),
        _field(snapshot.get("current_a")),
        _field(snapshot.get("power_w")),
        _field(snapshot.get("soc_percent")),
        _field(snapshot.get("capacity_ah")),
        _field(snapshot.get("energy_wh")),
        _field(snapshot.get("status")),
        faults,
    ]
    return ",".join(columns)


class UartLogger:
    def __init__(self, port, required: bool = False):
        self.port = port
        self.required = required
        self.disabled_reason = ""
        self._header_sent = False

    def write_snapshot(self, snapshot: dict) -> None:
        if self.port is None:
            if self.required:
                raise OSError(self.disabled_reason or "UART is not open")
            return
        if not self._header_sent:
            self.port.write((HEADER + "\n").encode("ascii"))
            self._header_sent = True
        self.port.write((format_line(snapshot) + "\n").encode("ascii"))
        flush = getattr(self.port, "flush", None)
        if flush:
            flush()


def open_uart(device: str, baud: int, required: bool = False) -> UartLogger:
    try:
        import serial
    except ImportError as exc:
        logger = UartLogger(None, required=required)
        logger.disabled_reason = f"pyserial is not installed ({exc})"
        if required:
            raise OSError(logger.disabled_reason) from exc
        return logger
    try:
        port = serial.Serial(device, baudrate=baud, timeout=0)
    except (OSError, ValueError) as exc:
        logger = UartLogger(None, required=required)
        logger.disabled_reason = f"{device} did not open: {exc}"
        if required:
            raise OSError(logger.disabled_reason) from exc
        return logger
    return UartLogger(port, required=required)
