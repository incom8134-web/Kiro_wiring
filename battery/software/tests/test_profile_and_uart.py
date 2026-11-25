import json

from battery_monitor.profile import NAMEPLATE_FIELDS, load_profile, synthetic_profile, validate_profile
from battery_monitor.service import main
from battery_monitor.uart_out import HEADER, UartLogger, format_line


ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "battery_profile.json"
EXAMPLE = ROOT / "config" / "examples" / "example_DO_NOT_USE.json"


def test_unconfigured_profile_lists_the_nameplate_fields():
    profile = load_profile(CONFIG)
    errors, _warnings = validate_profile(profile)
    text = "\n".join(errors)
    for field in NAMEPLATE_FIELDS:
        assert field in text
    assert "shunt_resistance_ohm" in text
    assert "shunt_rated_current_a" in text


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


def test_check_profile_command_exits_nonzero():
    assert main(["--check-profile", "--config", str(CONFIG)]) == 2
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
