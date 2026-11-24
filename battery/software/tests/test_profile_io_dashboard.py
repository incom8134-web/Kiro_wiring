import json

import pytest

from battery_monitor.lcd import NullDisplay, PCF8574LCD, format_lines
from battery_monitor.profile import NAMEPLATE_FIELDS, load_profile, synthetic_profile, validate_profile
from battery_monitor.sensors import Sample
from battery_monitor.service import Monitor, main
from battery_monitor.storage import StateStore
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
            "--no-web",
            "--state",
            str(state),
            "--history",
            str(history),
        ]
    )
    assert code == 0
    saved = json.loads(state.read_text(encoding="utf-8"))
    assert "ampere_hours_out" in saved
    assert history.is_file()


def test_lcd_and_uart_formatters():
    snap = {
        "voltage_v": 48.0,
        "current_a": -4.0,
        "power_w": -192.0,
        "soc_percent": 50.0,
        "ampere_hours_out": -1.0,
        "energy_wh": -48.0,
        "status": "Charging",
        "temperature_c": 26.0,
        "faults": [],
        "updated_unix": 1000.0,
        "nominal_capacity_ah": 100.0,
    }
    lines = format_lines(snap)
    assert len(lines) == 4
    assert all(len(line) == 20 for line in lines)
    assert "V" in lines[0] and "A" in lines[0]
    assert "CHG" in lines[3]
    assert "OK" in lines[3]
    blank = format_lines({"status": "Fault", "faults": ["COMMS"]})
    assert "FAULT" in blank[3]

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
    assert format_line(snap) in text
    assert "Charging" in text
    assert "-4.000000" in text


def test_lcd_driver_writes_the_backpack():
    class Bus:
        def __init__(self):
            self.writes = []

        def write_byte(self, address, value):
            self.writes.append((address, value))

    bus = Bus()
    lcd = PCF8574LCD(bus, address=0x27, sleeper=lambda _seconds: None)
    lcd.write_lines(["hello", "", "", ""])
    assert bus.writes
    assert all(address == 0x27 for address, _value in bus.writes)
    assert any((value & 0x01) for _address, value in bus.writes)  # RS set for text
    NullDisplay().write_lines(["x"])


def test_dashboard_snapshot_and_page(tmp_path):
    fastapi = pytest.importorskip("fastapi")
    assert fastapi
    from fastapi.testclient import TestClient

    from battery_monitor.dashboard import create_app

    profile = synthetic_profile()
    profile["persist_interval_s"] = 1.0e9
    profile["history_interval_s"] = 1.0e9
    store = StateStore(tmp_path / "state.json", 50.0)
    store.load()
    monitor = Monitor(
        profile,
        __import__("battery_monitor.sensors", fromlist=["ScriptedSensor"]).ScriptedSensor(
            [Sample(48.2, 10.0, pack_temp_c=27.5)]
        ),
        store,
        simulated=True,
    )
    monitor.tick(dt=1.0)
    app = create_app(monitor.snapshot)
    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    for label in (
        "Voltage V",
        "Current A",
        "Power W",
        "SOC %",
        "Capacity Ah",
        "Energy Wh",
        "Status",
        "Temperature C",
    ):
        assert label in page.text
    body = client.get("/api/snapshot").json()
    assert body["simulated"] is True
    assert body["status"] == "Discharging"
    assert body["current_a"] == pytest.approx(10.0)
    assert body["power_w"] == pytest.approx(48.2 * 10.0)
    assert body["temperature_c"] == pytest.approx(27.5)
    monitor.shutdown()
