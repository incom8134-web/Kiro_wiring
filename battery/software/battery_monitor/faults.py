"""Threshold and communications faults.

A fault is an alarm. It does not open a contactor. Limits come from the
profile; nothing here is a guessed pack rating.
"""

from __future__ import annotations

from .ina228 import VFS_V


def evaluate(
    voltage_v: float | None,
    current_a: float | None,
    profile: dict,
    comms_ok: bool,
    memstat_ok: bool = True,
    math_overflow: bool = False,
) -> list[str]:
    faults: list[str] = []
    if not comms_ok or voltage_v is None or current_a is None:
        faults.append("COMMS")
        return faults
    if not memstat_ok:
        faults.append("INA_MEMORY")
    if math_overflow:
        faults.append("INA_MATH_OVERFLOW")
    if voltage_v > float(profile["max_voltage_v"]):
        faults.append("OVERVOLTAGE")
    if voltage_v < float(profile["min_voltage_v"]):
        faults.append("UNDERVOLTAGE")
    if current_a > float(profile["max_discharge_current_a"]):
        faults.append("DISCHARGE_OVERCURRENT")
    if -current_a > float(profile["max_charge_current_a"]):
        faults.append("CHARGE_OVERCURRENT")
    adc = float(profile.get("adc_range_mv", 163.84))
    vfs = VFS_V[adc]
    if abs(current_a) * float(profile["shunt_resistance_ohm"]) >= 0.98 * vfs:
        faults.append("SHUNT_SATURATED")
    return faults
