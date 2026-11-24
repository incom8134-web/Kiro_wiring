"""Sensor access: the INA228 + TMP117, or a simulated source.

Hardware reads go through smbus2 on a configurable ``/dev/i2c-N``. That node
is the Jetson header bus (usually ``/dev/i2c-1``, pins 3 and 5) or the bus
number an ``i2c-tiny-usb`` adapter receives when its kernel driver binds.
The two are alternatives. Do not put a 5 V USB adapter on the header bus.
"""

from __future__ import annotations

from dataclasses import dataclass


class CommsError(OSError):
    pass


@dataclass
class Sample:
    voltage_v: float
    current_a: float
    pack_temp_c: float | None = None
    die_temp_c: float | None = None
    memstat_ok: bool = True
    math_overflow: bool = False


def parse_i2c_bus(spec: str | int) -> int:
    if isinstance(spec, int):
        return spec
    text = str(spec).strip()
    prefix = "/dev/i2c-"
    if text.startswith(prefix):
        return int(text[len(prefix) :])
    return int(text, 0)


def parse_address(spec: str | int) -> int:
    if isinstance(spec, int):
        return spec
    return int(str(spec).strip(), 0)


class ScriptedSensor:
    """Returns a prepared list of samples. Used by the unit tests."""

    def __init__(self, samples: list[Sample | Exception]):
        self._samples = list(samples)

    def read(self) -> Sample:
        if not self._samples:
            raise CommsError("scripted sensor has no more samples")
        item = self._samples.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class SimulatedSensor:
    """Deterministic waveform. No hardware and no nameplate data required.

    Index 0-9 discharge, 10-14 idle, 15-24 charge, then the pattern repeats.
    Voltage sags slightly with discharge so the sign of power is obvious.
    """

    def __init__(self, profile: dict):
        self.profile = profile
        self.index = 0

    def read(self) -> Sample:
        phase = self.index % 25
        nominal = float(self.profile["nominal_voltage_v"])
        if phase < 10:
            current = 10.0
        elif phase < 15:
            current = 0.0
        else:
            current = -4.0
        voltage = nominal - 0.02 * current
        temperature = 25.0 + 0.05 * (self.index % 25)
        sample = Sample(
            voltage_v=voltage,
            current_a=current,
            pack_temp_c=temperature,
            die_temp_c=temperature + 2.0,
        )
        self.index += 1
        return sample


class HardwareSensor:
    def __init__(self, profile: dict):
        self.profile = profile
        self.bus = None
        self.ina = None
        self.tmp = None

    def open(self) -> None:
        try:
            import smbus2
        except ImportError as exc:
            raise CommsError("smbus2 is not installed") from exc
        from .ina228 import INA228
        from .tmp117 import TMP117

        bus_number = parse_i2c_bus(self.profile.get("i2c_bus", "/dev/i2c-1"))
        try:
            self.bus = smbus2.SMBus(bus_number)
        except OSError as exc:
            raise CommsError(f"cannot open I2C bus {bus_number}: {exc}") from exc
        self.ina = INA228(
            self.bus,
            address=parse_address(self.profile.get("ina228_address", "0x40")),
            adc_range_mv=float(self.profile.get("adc_range_mv", 163.84)),
        )
        i_max = max(
            float(self.profile["max_charge_current_a"]),
            float(self.profile["max_discharge_current_a"]),
        )
        self.ina.configure(i_max, float(self.profile["shunt_resistance_ohm"]))
        self.tmp = TMP117(self.bus, address=parse_address(self.profile.get("tmp117_address", "0x48")))
        self.tmp.verify_identity()

    def close(self) -> None:
        if self.bus is not None:
            self.bus.close()
            self.bus = None

    def read(self) -> Sample:
        if self.ina is None or self.tmp is None:
            raise CommsError("sensor is not open")
        try:
            measured = self.ina.read()
            pack_temp = self.tmp.read_c()
        except OSError as exc:
            raise CommsError(str(exc)) from exc
        return Sample(
            voltage_v=measured["bus_voltage_v"],
            current_a=measured["current_a"],
            pack_temp_c=pack_temp,
            die_temp_c=measured["die_temperature_c"],
            memstat_ok=measured["memstat_ok"],
            math_overflow=measured["math_overflow"],
        )
