import json

from battery_monitor.faults import evaluate
from battery_monitor.profile import (
    calibration_current_a,
    load_profile,
    synthetic_profile,
    validate_profile,
)
from battery_monitor.service import main, uart_is_enabled
from battery_monitor.uart_out import HEADER, UartLogger, format_line


ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "battery_profile.json"
EXAMPLE = ROOT / "config" / "examples" / "example_DO_NOT_USE.json"


def test_shipped_profile_starts_with_unverified_current():
    profile = load_profile(CONFIG)
    errors, warnings = validate_profile(profile)
    assert errors == []
    text = "\n".join(warnings)
    assert "unverified" in text
    assert "shunt_resistance_ohm" not in text
    assert profile["shunt_resistance_ohm"] == 0.0002
    assert profile["shunt_rated_current_a"] == 204.8
    assert profile["ina228_address"] == "0x45"
    assert profile["adc_range_mv"] == 40.96
    assert profile["chemistry"] == "li-ion"
    assert profile["nominal_voltage_v"] == 12.0
    assert profile["max_voltage_v"] == 12.6
    assert profile["min_voltage_v"] == 9.0
    assert profile["capacity_ah"] == 45
    assert profile["cell_configuration"] == "3S"
    assert profile["max_charge_current_a"] is None
    assert profile["max_discharge_current_a"] is None
    amps, from_pack = calibration_current_a(profile)
    assert amps == 204.8
    assert from_pack is False
    faults = evaluate(12.0, 80.0, profile, True)
    assert "DISCHARGE_OVERCURRENT" not in faults
    assert "CHARGE_OVERCURRENT" not in evaluate(12.0, -40.0, profile, True)
    assert "OVERVOLTAGE" in evaluate(13.0, 0.0, profile, True)
    assert "UNDERVOLTAGE" in evaluate(8.5, 0.0, profile, True)
    assert profile["i2c_bus"] == "/dev/i2c-7"
    assert profile["uart_device"] == "/dev/ttyTHS0"
    assert profile["uart_enabled"] is False
    assert uart_is_enabled(profile) is False
    assert uart_is_enabled({}) is False
    assert uart_is_enabled({"uart_enabled": True}) is True
    assert synthetic_profile()["i2c_bus"] == "/dev/i2c-7"
    assert synthetic_profile()["uart_device"] == "/dev/ttyTHS0"
    assert synthetic_profile()["uart_enabled"] is False


def test_shipped_profile_simulate_uses_the_pack(tmp_path):
    state = tmp_path / "state.json"
    code = main(
        [
            "--config",
            str(CONFIG),
            "--simulate",
            "--duration",
            "0.6",
            "--state",
            str(state),
            "--history",
            str(tmp_path / "history.sqlite"),
        ]
    )
    assert code == 0
    saved = json.loads(state.read_text(encoding="utf-8"))
    assert saved["chemistry"] == "li-ion"
    assert saved["nominal_capacity_ah"] == 45.0
    assert saved["simulated"] is True


def test_over_voltage_pack_is_rejected_and_example_is_not_hardware():
    profile = synthetic_profile()
    profile["example_only"] = False
    profile["max_voltage_v"] = 90.0
    errors, _warnings = validate_profile(profile)
    assert any("85" in line for line in errors)

    example = load_profile(EXAMPLE)
    errors, warnings = validate_profile(example, allow_example=False)
    assert any("example_only" in line for line in errors)
    _errors, warnings = validate_profile(example, allow_example=True)
    assert any("OCV" in line for line in warnings)

    too_big = synthetic_profile()
    too_big["example_only"] = False
    too_big["shunt_resistance_ohm"] = 1.0
    errors, _warnings = validate_profile(too_big)
    assert any("full scale" in line for line in errors)


def test_check_profile_command_accepts_the_shipped_pack():
    assert main(["--check-profile", "--config", str(CONFIG)]) == 0
    assert main(["--check-profile", "--config", str(EXAMPLE), "--allow-example"]) == 0


def test_simulate_command_writes_state(tmp_path):
    state = tmp_path / "state.json"
    history = tmp_path / "history.sqlite"
    code = main(
        [
            "--simulate",
            "--duration",
            "0.8",
            "--state",
            str(state),
            "--history",
            str(history),
        ]
    )
    assert code == 0
    saved = json.loads(state.read_text(encoding="utf-8"))
    assert "ampere_hours_out" in saved
    assert "voltage_v" in saved
    assert "temperature_c" not in saved
    assert history.is_file()


def test_uart_formatter():
    snap = {
        "voltage_v": 48.0,
        "current_a": -4.0,
        "power_w": -192.0,
        "soc_percent": 50.0,
        "capacity_ah": 50.0,
        "energy_wh": -48.0,
        "status": "Charging",
        "faults": [],
        "updated_unix": 1000.0,
        "nominal_capacity_ah": 100.0,
    }

    class Port:
        def __init__(self):
            self.buf = b""

        def write(self, data):
            self.buf += data

        def flush(self):
            pass

    port = Port()
    logger = UartLogger(port)
    logger.write_snapshot(snap)
    text = port.buf.decode("ascii")
    assert text.splitlines()[0] == HEADER
    assert "temperature" not in HEADER
    assert format_line(snap) in text
    assert "Charging" in text
    assert "-4.000000" in text
    assert "50.000000" in text
