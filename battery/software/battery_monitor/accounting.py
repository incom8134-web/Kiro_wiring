"""Signed power, coulomb counting, and energy.

Sign convention, fixed by the wiring in the design doc:
positive current is discharge (out of the battery), negative current is charge.
Power uses the same sign: positive power is leaving the battery.

The INA228 POWER register is unsigned (datasheet equation 5), so signed power
is computed here from bus voltage and signed current. Ampere-hours and
watt-hours are integrated here as well. The chip's ENERGY and CHARGE
registers reset when its supply drops and are not the stored record.
"""

from __future__ import annotations


def apply_calibration(voltage_v: float, current_a: float, profile: dict) -> tuple[float, float]:
    voltage = float(profile.get("voltage_gain", 1.0)) * voltage_v + float(
        profile.get("voltage_offset_v", 0.0)
    )
    current = float(profile.get("current_gain", 1.0)) * current_a + float(
        profile.get("current_offset_a", 0.0)
    )
    if profile.get("invert_current"):
        current = -current
    return voltage, current


def signed_power_w(voltage_v: float, current_a: float) -> float:
    return voltage_v * current_a


def integrate(state: dict, voltage_v: float, current_a: float, dt_s: float) -> float:
    """Add one step. Returns signed power in watts.

    ``dt_s`` of 0 establishes a reading and adds nothing. Negative dt is rejected.
    """
    if dt_s < 0:
        raise ValueError("dt must be >= 0")
    power = signed_power_w(voltage_v, current_a)
    if dt_s > 0:
        state["ampere_hours_out"] = float(state.get("ampere_hours_out", 0.0)) + current_a * dt_s / 3600.0
        state["watt_hours_out"] = float(state.get("watt_hours_out", 0.0)) + power * dt_s / 3600.0
    return power


def status_from_current(current_a: float, idle_current_a: float, comms_ok: bool) -> str:
    if not comms_ok:
        return "Fault"
    if current_a > idle_current_a:
        return "Discharging"
    if current_a < -idle_current_a:
        return "Charging"
    return "Idle"


def remaining_ah(state: dict, capacity_ah: float) -> float | None:
    anchor = state.get("soc_anchor_percent", None)
    if anchor is None or capacity_ah <= 0:
        return None
    return capacity_ah * float(anchor) / 100.0 - (
        float(state.get("ampere_hours_out", 0.0)) - float(state.get("ah_at_anchor", 0.0))
    )


def soc_percent(state: dict, capacity_ah: float, clamp: bool = True) -> float | None:
    remaining = remaining_ah(state, capacity_ah)
    if remaining is None:
        return None
    soc = remaining / capacity_ah * 100.0
    if clamp:
        return min(100.0, max(0.0, soc))
    return soc


def remaining_runtime_h(
    current_a: float,
    remaining: float | None,
    capacity_ah: float,
    idle_current_a: float,
) -> tuple[float | None, str | None]:
    if remaining is None:
        return None, None
    if current_a > idle_current_a:
        usable = max(remaining, 0.0)
        return usable / current_a, "remaining"
    if current_a < -idle_current_a:
        deficit = capacity_ah - remaining
        if deficit <= 0:
            return 0.0, "time_to_full"
        return deficit / abs(current_a), "time_to_full"
    return None, None


def fresh_state(initial_soc_percent: float | None) -> dict:
    state = {
        "ampere_hours_out": 0.0,
        "watt_hours_out": 0.0,
        "soc_anchor_percent": None,
        "ah_at_anchor": 0.0,
        "power_loss_gap": False,
    }
    if initial_soc_percent is not None:
        state["soc_anchor_percent"] = float(initial_soc_percent)
    return state
