"""TMP117 pack-temperature sensor.

Texas Instruments TMP117 datasheet (SNOSD82):
https://www.ti.com/lit/ds/symlink/tmp117.pdf

The temperature result register is 0x00, 16-bit two's complement,
7.8125 m°C per LSB (1/128 °C). Device ID register 0x0F resets to 0x0117.
ADD0 tied to GND selects I2C address 0x48.
"""

from __future__ import annotations

REG_TEMP = 0x00
REG_DEVICE_ID = 0x0F
DEVICE_ID = 0x0117


class TmpError(OSError):
    pass


def decode_temperature_c(raw16: int) -> float:
    if raw16 & 0x8000:
        raw16 -= 0x10000
    return raw16 / 128.0


class TMP117:
    def __init__(self, bus, address: int = 0x48):
        self.bus = bus
        self.address = address

    def _read16(self, reg: int) -> int:
        try:
            data = self.bus.read_i2c_block_data(self.address, reg, 2)
        except OSError as exc:
            raise TmpError(f"TMP117 read reg 0x{reg:02X} failed: {exc}") from exc
        if len(data) != 2:
            raise TmpError(f"TMP117 reg 0x{reg:02X} returned {len(data)} bytes")
        return ((data[0] & 0xFF) << 8) | (data[1] & 0xFF)

    def verify_identity(self) -> None:
        device = self._read16(REG_DEVICE_ID)
        if device != DEVICE_ID:
            raise TmpError(f"unexpected TMP117 id 0x{device:04X}")

    def read_c(self) -> float:
        return decode_temperature_c(self._read16(REG_TEMP))
