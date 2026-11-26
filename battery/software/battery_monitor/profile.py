"""Battery profile loading.

Nameplate values are never invented. A null required field is an error on
hardware. ``--simulate`` may substitute a clearly marked synthetic profile
so the tests can run with no pack connected.
"""

from __future__ import annotations

import json
from pathlib import Path

# Operating maximum of the INA228 VBUS / common-mode pins (SLYS021).
INA228_MAX_BUS_V = 85.0
INA228_FULL_SCALE_V = {163.84: 0.16384, 40.96: 0.04096}

# These are the pack facts the user must supply. The software will not guess.
NAMEPLATE_FIELDS = (
    "chemistry",
    "nominal_voltage_v",
    "max_voltage_v",
    "min_voltage_v",
    "capacity_ah",
    "max_charge_current_a",
    "max_discharge_current_a",
)

# Required before a real sensor is used, but not all of them are printed on the pack.
CONFIG_FIELDS = NAMEPLATE_FIELDS + (
    "idle_current_a",
    "shunt_resistance_ohm",
)

NAMEPLATE_HELP = {
    "chemistry": "cell chemistry, from the cell or pack datasheet (the OCV table depends on it)",
    "nominal_voltage_v": "nominal pack voltage, volts",
    "max_voltage_v": "highest voltage the sense node can reach, volts (full pack or charger, whichever is higher)",
    "min_voltage_v": "empty cutoff voltage, volts",
    "capacity_ah": "pack capacity used for SOC, ampere-hours",
    "max_charge_current_a": "maximum charge current, amperes",
    "max_discharge_current_a": "maximum discharge current, amperes",
}


def load_profile(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def synthetic_profile() -> dict:
    """A fake pack used only for --simulate. Not a hardware recommendation."""
    return {
        "example_only": True,
        "profile_name": "SIMULATED — not a real battery",
        "chemistry": "SIMULATED",
        "nominal_voltage_v": 48.0,
        "max_voltage_v": 54.0,
        "min_voltage_v": 40.0,
        "capacity_ah": 100.0,
        "max_charge_current_a": 20.0,
        "max_discharge_current_a": 50.0,
        "idle_current_a": 0.5,
        "shunt_resistance_ohm": 0.0002,
        "shunt_rated_current_a": 204.8,
        "initial_soc_percent": 50.0,
        "ocv_voltage_v": [40.0, 48.0, 54.0],
        "ocv_soc_percent": [0.0, 50.0, 100.0],
        "rest_current_a": 0.5,
        "rest_duration_s": 300.0,
        "i2c_bus": "/dev/i2c-7",
        "ina228_address": "0x45",
        "uart_device": "/dev/ttyTHS0",
        "uart_baud": 115200,
        "uart_enabled": False,
        "adc_range_mv": 40.96,
        "current_gain": 1.0,
        "current_offset_a": 0.0,
        "voltage_gain": 1.0,
        "voltage_offset_v": 0.0,
        "invert_current": False,
        "sample_period_s": 0.5,
        "persist_interval_s": 30.0,
        "history_interval_s": 10.0,
        "max_integrate_dt_s": 5.0,
        "comms_timeout_s": 2.0,
        "_warning": "Synthetic numbers for the simulator. Do not copy them onto a real pack.",
    }


def _missing(profile: dict) -> list[str]:
    missing = []
    for key in CONFIG_FIELDS:
        value = profile.get(key, None)
        if value is None or value == "":
            missing.append(key)
    rated_i = profile.get("shunt_rated_current_a")
    rated_p = profile.get("shunt_rated_power_w")
    if rated_i is None and rated_p is None:
        missing.append("shunt_rated_current_a or shunt_rated_power_w")
    return missing


def validate_profile(profile: dict, allow_example: bool = False) -> tuple[list[str], list[str]]:
    """Return ``(errors, warnings)``. Errors must block hardware use."""
    errors: list[str] = []
    warnings: list[str] = []
    if profile.get("example_only") and not allow_example:
        errors.append(
            "profile is marked example_only. It is not the user's battery. "
            "Copy config/battery_profile.json and fill it from the pack datasheet."
        )
    missing = _missing(profile)
    for key in missing:
        if key in NAMEPLATE_HELP:
            errors.append(f"missing {key}: {NAMEPLATE_HELP[key]}")
        else:
            errors.append(f"missing {key}")
    if missing:
        return errors, warnings

    name = str(profile.get("profile_name") or "").strip()
    if not name:
        warnings.append("profile_name is empty")

    try:
        vmin = float(profile["min_voltage_v"])
        vnom = float(profile["nominal_voltage_v"])
        vmax = float(profile["max_voltage_v"])
        capacity = float(profile["capacity_ah"])
        i_chg = float(profile["max_charge_current_a"])
        i_dis = float(profile["max_discharge_current_a"])
        i_idle = float(profile["idle_current_a"])
        r_shunt = float(profile["shunt_resistance_ohm"])
    except (TypeError, ValueError) as exc:
        errors.append(f"a required number is not numeric: {exc}")
        return errors, warnings

    if not (vmin < vnom <= vmax):
        errors.append("need min_voltage_v < nominal_voltage_v <= max_voltage_v")
    if vmax > INA228_MAX_BUS_V:
        errors.append(
            f"max_voltage_v {vmax} V is above the INA228 85 V bus limit "
            "(datasheet SLYS021). Do not connect this pack to this monitor."
        )
    if vmin <= 0 or capacity <= 0 or i_chg <= 0 or i_dis <= 0 or i_idle <= 0 or r_shunt <= 0:
        errors.append("voltages, capacity, currents, and shunt resistance must be positive")
    if i_idle >= min(i_chg, i_dis):
        errors.append("idle_current_a must be below both charge and discharge limits")

    adc = float(profile.get("adc_range_mv", 163.84))
    if adc not in INA228_FULL_SCALE_V:
        errors.append("adc_range_mv must be 163.84 or 40.96")
        return errors, warnings
    vfs = INA228_FULL_SCALE_V[adc]
    i_peak = max(i_chg, i_dis)
    v_sense = i_peak * r_shunt
    if v_sense > vfs:
        errors.append(
            f"shunt drop {v_sense * 1000:.2f} mV at {i_peak} A exceeds the "
            f"INA228 ±{vfs * 1000:.2f} mV full scale. Lower shunt_resistance_ohm "
            f"(limit is {vfs / i_peak:.6g} ohm)."
        )
    elif v_sense > 0.9 * vfs:
        warnings.append(
            f"shunt drop is {v_sense / vfs * 100:.0f}% of full scale at the "
            "nameplate current. A surge will clip. Prefer more headroom."
        )
    if abs(r_shunt - 0.0002) < 1e-9 and i_peak > 150.0:
        warnings.append(
            "nameplate current is above the Matek I2C-INA-BM 150 A continuous "
            "rating (https://www.mateksys.com/?portfolio=i2c-ina-bm). The ADC "
            "full scale at 200 µΩ and ±40.96 mV is 204.8 A."
        )

    rated_i = profile.get("shunt_rated_current_a")
    rated_p = profile.get("shunt_rated_power_w")
    dissipation = i_peak * i_peak * r_shunt
    if rated_i is not None and i_peak > float(rated_i):
        errors.append(
            f"peak current {i_peak} A is above shunt_rated_current_a {rated_i} A"
        )
    if rated_p is not None and dissipation > float(rated_p):
        errors.append(
            f"shunt dissipation {dissipation:.3f} W at peak current is above "
            f"shunt_rated_power_w {rated_p} W. Confirm the shunt datasheet derating; "
            "continuous use should stay inside the rating, with margin."
        )
    if rated_i is None and rated_p is None:
        errors.append("set shunt_rated_current_a or shunt_rated_power_w from the shunt datasheet")

    soc = profile.get("initial_soc_percent", None)
    if soc is not None and not (0.0 <= float(soc) <= 100.0):
        errors.append("initial_soc_percent must be between 0 and 100, or null")

    ocv_v = list(profile.get("ocv_voltage_v") or [])
    ocv_s = list(profile.get("ocv_soc_percent") or [])
    if len(ocv_v) != len(ocv_s):
        errors.append("ocv_voltage_v and ocv_soc_percent must be the same length")
    elif len(ocv_v) == 1:
        errors.append("an OCV table needs at least two points")
    elif len(ocv_v) >= 2:
        try:
            volts = [float(v) for v in ocv_v]
            socs = [float(s) for s in ocv_s]
        except (TypeError, ValueError):
            errors.append("OCV table values must be numbers")
        else:
            if any(volts[i] >= volts[i + 1] for i in range(len(volts) - 1)):
                errors.append("ocv_voltage_v must be strictly increasing")
            if any(s < 0.0 or s > 100.0 for s in socs):
                errors.append("ocv_soc_percent values must be between 0 and 100")
    else:
        warnings.append(
            "OCV table is empty. SOC will follow coulomb counting only, with no "
            "rest correction, until you add a curve for this chemistry."
        )

    for key, default in (
        ("current_gain", 1.0),
        ("voltage_gain", 1.0),
        ("sample_period_s", 0.5),
        ("persist_interval_s", 30.0),
        ("history_interval_s", 10.0),
        ("max_integrate_dt_s", 5.0),
    ):
        try:
            if float(profile.get(key, default)) <= 0:
                errors.append(f"{key} must be positive")
        except (TypeError, ValueError):
            errors.append(f"{key} must be a number")
    return errors, warnings


def resolve_profile(path: str | Path | None, simulate: bool, allow_example: bool) -> tuple[dict, list[str]]:
    """Load a profile. In simulate mode an incomplete file falls back to synthetic data."""
    notes: list[str] = []
    if path is None:
        if not simulate:
            raise ValueError("a profile path is required")
        notes.append("no profile path; using the synthetic simulator profile")
        return synthetic_profile(), notes
    profile = load_profile(path)
    errors, warnings = validate_profile(profile, allow_example=allow_example or simulate)
    if errors and simulate:
        notes.append(
            "profile is incomplete or an example, so --simulate is using the "
            "built-in synthetic pack instead of these values"
        )
        notes.extend(errors)
        return synthetic_profile(), notes
    if errors:
        raise ValueError("profile rejected:\n- " + "\n- ".join(errors))
    notes.extend(warnings)
    return profile, notes
