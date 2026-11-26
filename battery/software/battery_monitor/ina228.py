"""INA228 register math and I2C driver.

Numbers below are from Texas Instruments, INA228 datasheet (SLYS021):
https://www.ti.com/lit/ds/symlink/ina228.pdf

The die measures the shunt between IN+ and IN-. On the Matek I2C-INA-BM
the shunt is the module's 200 µΩ conductive path, and pack current does
flow through that path. It does not flow through the Jetson header.

Matek full scale, from https://www.mateksys.com/?portfolio=i2c-ina-bm and
SLYS021: R = 0.0002 ohm, ADCRANGE = 1 (±40.96 mV), Imax = 204.8 A,
CURRENT_LSB = 204.8 / 2^19, SHUNT_CAL = 4096. Address 0x45 is decimal 69
(A1=VS, A0=VS, jumpers open). The constructor default stays 0x40 so the
datasheet example test is unchanged; the profile passes 0x45.
"""

from __future__ import annotations

# Electrical characteristics, section 6.5.
VFS_V = {163.84: 0.16384, 40.96: 0.04096}
SHUNT_LSB_V = {163.84: 312.5e-9, 40.96: 78.125e-9}
VBUS_LSB_V = 195.3125e-6
DIETEMP_LSB_C = 7.8125e-3
MANUFACTURER_ID = 0x5449
DEVICE_ID = 0x2281

# Matek I2C-INA-BM module facts. Not a pack nameplate.
# https://www.mateksys.com/?portfolio=i2c-ina-bm
MATEK_SHUNT_OHM = 0.0002
MATEK_ADC_RANGE_MV = 40.96
MATEK_ADDRESS = 0x45
MATEK_FULL_SCALE_A = 204.8
MATEK_CONTINUOUS_A = 150.0

REG_CONFIG = 0x00
REG_ADC_CONFIG = 0x01
REG_SHUNT_CAL = 0x02
REG_VSHUNT = 0x04
REG_VBUS = 0x05
REG_DIETEMP = 0x06
REG_CURRENT = 0x07
REG_POWER = 0x08
REG_ENERGY = 0x09
REG_CHARGE = 0x0A
REG_DIAG_ALRT = 0x0B
REG_MANUFACTURER_ID = 0x3E
REG_DEVICE_ID = 0x3F

# ADC_CONFIG: continuous bus + shunt + die temp, 1052 µs, average 128.
# Update period is about 3 * 1.052 ms * 128 ≈ 404 ms (section 7.3.4).
ADC_CONFIG_DEFAULT = 0xFB6C


class InaError(OSError):
    pass


def sign_extend(value: int, bits: int) -> int:
    value &= (1 << bits) - 1
    sign = 1 << (bits - 1)
    if value & sign:
        value -= 1 << bits
    return value


def decode_shunt_voltage_v(raw24: int, adc_range_mv: float = 163.84) -> float:
    """Decode the 24-bit VSHUNT register. Bits 23-4 are the 20-bit reading."""
    lsb = SHUNT_LSB_V[adc_range_mv]
    return sign_extend(raw24 >> 4, 20) * lsb


def decode_bus_voltage_v(raw24: int) -> float:
    return sign_extend(raw24 >> 4, 20) * VBUS_LSB_V


def decode_dietemp_c(raw16: int) -> float:
    return sign_extend(raw16, 16) * DIETEMP_LSB_C


def current_lsb_a(maximum_expected_current_a: float) -> float:
    """Equation 3: CURRENT_LSB = Maximum Expected Current / 2^19."""
    if maximum_expected_current_a <= 0:
        raise ValueError("maximum expected current must be positive")
    return maximum_expected_current_a / float(2**19)


def shunt_cal_register(
    maximum_expected_current_a: float,
    r_shunt_ohm: float,
    adc_range_mv: float = 163.84,
) -> tuple[int, float]:
    """Equation 2, allowing CURRENT_LSB to grow by at most 8× so the register fits.

    Returns ``(register_value, current_lsb_used)``.
    """
    if r_shunt_ohm <= 0:
        raise ValueError("shunt resistance must be positive")
    if adc_range_mv not in VFS_V:
        raise ValueError("adc_range_mv must be 163.84 or 40.96")
    base_lsb = current_lsb_a(maximum_expected_current_a)
    lsb = base_lsb
    for _doubling in range(0, 4):
        cal = 13107.2e6 * lsb * r_shunt_ohm
        if adc_range_mv == 40.96:
            cal *= 4.0
        rounded = int(round(cal))
        if 1 <= rounded <= 32767:
            return rounded, lsb
        lsb *= 2.0
        if lsb > base_lsb * 8.0 + 1e-18:
            break
    raise ValueError(
        "SHUNT_CAL does not fit in 15 bits. Lower the shunt resistance or "
        "the maximum expected current."
    )


def decode_current_a(raw24: int, current_lsb: float) -> float:
    """Equation 4. ``raw24`` is the 24-bit CURRENT register."""
    return sign_extend(raw24 >> 4, 20) * current_lsb


def decode_power_w(raw24: int, current_lsb: float) -> float:
    """Equation 5. The POWER register is unsigned and has no current sign."""
    return 3.2 * current_lsb * (raw24 & 0xFFFFFF)


def decode_energy_j(raw40: int, current_lsb: float) -> float:
    """Equation 6. Unsigned joules. Resets when VS power is lost."""
    return 16.0 * 3.2 * current_lsb * (raw40 & ((1 << 40) - 1))


def decode_charge_c(raw40: int, current_lsb: float) -> float:
    """Equation 7. Signed coulombs. Resets when VS power is lost."""
    return sign_extend(raw40, 40) * current_lsb


def max_shunt_ohm(maximum_current_a: float, adc_range_mv: float = 163.84) -> float:
    """Equation 8: Rshunt < V_SENSE_MAX / I_MAX. This returns the limit, not a choice."""
    if maximum_current_a <= 0:
        raise ValueError("maximum current must be positive")
    return VFS_V[adc_range_mv] / maximum_current_a


def shunt_dissipation_w(current_a: float, r_shunt_ohm: float) -> float:
    return current_a * current_a * r_shunt_ohm


class INA228:
    """smbus2-compatible driver. ``bus`` needs the standard block read/write calls."""

    def __init__(self, bus, address: int = 0x40, adc_range_mv: float = 163.84):
        self.bus = bus
        self.address = address
        self.adc_range_mv = adc_range_mv
        self.current_lsb = 0.0

    def _read(self, reg: int, n: int) -> int:
        try:
            data = self.bus.read_i2c_block_data(self.address, reg, n)
        except OSError as exc:
            raise InaError(f"INA228 read reg 0x{reg:02X} failed: {exc}") from exc
        if len(data) != n:
            raise InaError(f"INA228 reg 0x{reg:02X} returned {len(data)} bytes, expected {n}")
        value = 0
        for byte in data:
            value = (value << 8) | (byte & 0xFF)
        return value

    def _write16(self, reg: int, value: int) -> None:
        payload = [(value >> 8) & 0xFF, value & 0xFF]
        try:
            self.bus.write_i2c_block_data(self.address, reg, payload)
        except OSError as exc:
            raise InaError(f"INA228 write reg 0x{reg:02X} failed: {exc}") from exc

    def verify_identity(self) -> None:
        manufacturer = self._read(REG_MANUFACTURER_ID, 2)
        device = self._read(REG_DEVICE_ID, 2)
        if manufacturer != MANUFACTURER_ID or device != DEVICE_ID:
            raise InaError(
                f"unexpected identity manufacturer=0x{manufacturer:04X} "
                f"device=0x{device:04X} (expected 0x5449 / 0x2281)"
            )

    def configure(self, maximum_expected_current_a: float, r_shunt_ohm: float) -> int:
        self.verify_identity()
        cal, self.current_lsb = shunt_cal_register(
            maximum_expected_current_a, r_shunt_ohm, self.adc_range_mv
        )
        config = 0
        if self.adc_range_mv == 40.96:
            config |= 1 << 4
        self._write16(REG_CONFIG, config)
        self._write16(REG_ADC_CONFIG, ADC_CONFIG_DEFAULT)
        self._write16(REG_SHUNT_CAL, cal)
        return cal

    def read(self) -> dict:
        if self.current_lsb <= 0:
            raise InaError("INA228 is not configured")
        shunt_raw = self._read(REG_VSHUNT, 3)
        bus_raw = self._read(REG_VBUS, 3)
        temp_raw = self._read(REG_DIETEMP, 2)
        current_raw = self._read(REG_CURRENT, 3)
        power_raw = self._read(REG_POWER, 3)
        diag = self._read(REG_DIAG_ALRT, 2)
        return {
            "shunt_voltage_v": decode_shunt_voltage_v(shunt_raw, self.adc_range_mv),
            "bus_voltage_v": decode_bus_voltage_v(bus_raw),
            "die_temperature_c": decode_dietemp_c(temp_raw),
            "current_a": decode_current_a(current_raw, self.current_lsb),
            "power_unsigned_w": decode_power_w(power_raw, self.current_lsb),
            "diag": diag,
            "memstat_ok": bool(diag & 0x1),
            "math_overflow": bool(diag & (1 << 9)),
        }
