"""20×4 HD44780 LCD behind a PCF8574 I2C backpack.

The backpack mapping used here is the common hobby-module wiring:
P0 RS, P1 RW, P2 E, P3 backlight, P4-P7 data. RW is held low (write).

A 5 V backpack must not be tied straight to the Jetson I2C pins. See the
level-shifter section of the design doc. This driver only talks I2C; it
does not make a 5 V module safe.

``sleep`` can be replaced in tests so the init delays do not run.
"""

from __future__ import annotations

import time

# 20×4 DDRAM starts.
_LINE = (0x00, 0x40, 0x14, 0x54)


def format_lines(snapshot: dict) -> list[str]:
    """Four LCD lines, each at most 20 characters."""

    def num(value, width, suffix):
        if value is None:
            return f"{'—':>{width}}{suffix}"
        return f"{value:{width}.1f}{suffix}"

    voltage = snapshot.get("voltage_v")
    current = snapshot.get("current_a")
    power = snapshot.get("power_w")
    soc = snapshot.get("soc_percent")
    energy = snapshot.get("energy_wh")
    temp = snapshot.get("temperature_c")
    status = snapshot.get("status") or "?"
    faults = snapshot.get("faults") or []
    # 20 columns. Full words are on the web page; the LCD uses short codes.
    codes = {"Charging": "CHG", "Discharging": "DIS", "Idle": "IDLE", "Fault": "FAULT"}
    code = codes.get(status, "????")
    mark = "ALRM" if faults and status != "Fault" else ("    " if status == "Fault" else "OK  ")
    soc_text = "SOC —" if soc is None else f"SOC {soc:5.1f}%"
    line1 = f"{num(voltage, 6, 'V')} {num(current, 6, 'A')}"
    line2 = f"{num(power, 7, 'W')} {soc_text}"
    line3 = f"Ah {num(snapshot.get('ampere_hours_out'), 7, '')} Wh {num(energy, 6, '')}"
    line4 = f"{code:<5} {mark} {num(temp, 5, 'C')}"
    return [line[:20].ljust(20) for line in (line1, line2, line3, line4)]


class PCF8574LCD:
    def __init__(self, bus, address: int = 0x27, sleeper=None):
        self.bus = bus
        self.address = address
        self.sleep = sleeper or time.sleep
        self.backlight = True
        self._init()

    def _write_raw(self, value: int) -> None:
        try:
            self.bus.write_byte(self.address, value & 0xFF)
        except OSError as exc:
            raise OSError(f"LCD I2C write failed: {exc}") from exc

    def _nibble(self, nibble: int, rs: int) -> None:
        base = ((nibble & 0x0F) << 4) | (0x08 if self.backlight else 0) | (0x01 if rs else 0)
        self._write_raw(base | 0x04)
        self.sleep(0.0001)
        self._write_raw(base)
        self.sleep(0.0001)

    def _byte(self, value: int, rs: int) -> None:
        self._nibble((value >> 4) & 0x0F, rs)
        self._nibble(value & 0x0F, rs)

    def _command(self, value: int) -> None:
        self._byte(value, 0)

    def _init(self) -> None:
        self.sleep(0.02)
        self._nibble(0x03, 0)
        self.sleep(0.005)
        self._nibble(0x03, 0)
        self.sleep(0.001)
        self._nibble(0x03, 0)
        self._nibble(0x02, 0)
        self._command(0x28)
        self._command(0x0C)
        self._command(0x01)
        self.sleep(0.002)
        self._command(0x06)

    def write_lines(self, lines: list[str]) -> None:
        for index, text in enumerate(lines[:4]):
            self._command(0x80 | _LINE[index])
            for char in text[:20].ljust(20):
                self._byte(ord(char), 1)


class NullDisplay:
    """Used when the LCD is disabled or failed to open. Records the last text."""

    def __init__(self):
        self.lines: list[str] = []

    def write_lines(self, lines: list[str]) -> None:
        self.lines = list(lines)
