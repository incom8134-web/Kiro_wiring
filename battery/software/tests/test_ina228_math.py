"""Lock the driver to the worked example in INA228 datasheet section 8.2."""

import pytest

from battery_monitor.ina228 import (
    INA228,
    InaError,
    decode_bus_voltage_v,
    decode_charge_c,
    decode_current_a,
    decode_dietemp_c,
    decode_energy_j,
    decode_power_w,
    decode_shunt_voltage_v,
    max_shunt_ohm,
    shunt_cal_register,
)
def test_datasheet_shunt_cal_and_lsb():
    # Section 8.2.2.3: 10 A and 16.2 mΩ -> CURRENT_LSB 19.0735 µA, SHUNT_CAL 4050.
    register, lsb = shunt_cal_register(10.0, 0.0162, 163.84)
    assert register == 4050
    assert lsb == pytest.approx(10.0 / 2**19)


def test_datasheet_returned_values():
    lsb = 10.0 / 2**19
    assert decode_shunt_voltage_v(311040 << 4) == pytest.approx(0.0972)
    assert decode_shunt_voltage_v(0xB4100 << 4) == pytest.approx(-0.0972)
    assert decode_current_a(314572 << 4, lsb) == pytest.approx(6.0, abs=1e-4)
    assert decode_bus_voltage_v(245760 << 4) == pytest.approx(48.0)
    assert decode_power_w(4718604, lsb) == pytest.approx(288.0, rel=1e-5)
    assert decode_energy_j(1061683200, lsb) == pytest.approx(1_036_800.0, rel=1e-5)
    assert decode_charge_c(1132462080, lsb) == pytest.approx(21600.0, rel=1e-5)
    assert decode_dietemp_c(3200) == pytest.approx(25.0)


def test_shunt_limit():
    # Equation 8 at 10 A on the ±163.84 mV range.
    assert max_shunt_ohm(10.0) == pytest.approx(0.016384)


def test_adc_range_1_multiplies_cal_by_four():
    base, _ = shunt_cal_register(10.0, 0.001, 163.84)
    high, _ = shunt_cal_register(10.0, 0.001, 40.96)
    assert high == base * 4


def test_driver_programs_cal_and_decodes_a_negative_current():
    class Bus:
        def __init__(self):
            self.writes = []

        def read_i2c_block_data(self, addr, reg, n):
            assert addr == 0x40
            if reg == 0x3E:
                return [0x54, 0x49]
            if reg == 0x3F:
                return [0x22, 0x81]
            if reg == 0x04:  # negative shunt, 20-bit value in the top bits
                raw = (0xB4100 << 4) & 0xFFFFFF
                return [(raw >> 16) & 0xFF, (raw >> 8) & 0xFF, raw & 0xFF]
            if reg == 0x05:
                raw = 245760 << 4
                return [(raw >> 16) & 0xFF, (raw >> 8) & 0xFF, raw & 0xFF]
            if reg == 0x06:
                return [0x0C, 0x80]
            if reg == 0x07:
                raw = ((1 << 20) - 314572) << 4
                return [(raw >> 16) & 0xFF, (raw >> 8) & 0xFF, raw & 0xFF]
            if reg == 0x08:
                return [0x00, 0x00, 0x00]
            if reg == 0x0B:
                return [0x00, 0x01]  # MEMSTAT set, no faults
            raise AssertionError(reg)

        def write_i2c_block_data(self, addr, reg, data):
            self.writes.append((reg, data))

    bus = Bus()
    ina = INA228(bus)
    cal = ina.configure(10.0, 0.0162)
    assert cal == 4050
    assert (0x02, [0x0F, 0xD2]) in [(reg, data) for reg, data in bus.writes]
    reading = ina.read()
    assert reading["shunt_voltage_v"] == pytest.approx(-0.0972)
    assert reading["bus_voltage_v"] == pytest.approx(48.0)
    assert reading["current_a"] == pytest.approx(-6.0, abs=1e-4)
    assert reading["die_temperature_c"] == pytest.approx(25.0)
    assert reading["memstat_ok"] is True


def test_identity_mismatch():
    class Bus:
        def read_i2c_block_data(self, addr, reg, n):
            return [0x00, 0x00]

    with pytest.raises(InaError):
        INA228(Bus()).verify_identity()


