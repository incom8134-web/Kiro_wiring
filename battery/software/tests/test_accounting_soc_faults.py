import pytest

from battery_monitor.accounting import (
    apply_calibration,
    fresh_state,
    integrate,
    remaining_runtime_h,
    signed_power_w,
    soc_percent,
    status_from_current,
)
from battery_monitor.faults import evaluate
from battery_monitor.sensors import CommsError, Sample, ScriptedSensor, SimulatedSensor
from battery_monitor.service import Monitor
from battery_monitor.soc import RestTracker, ocv_to_soc
from battery_monitor.storage import HistoryDB, StateStore


def _profile(**overrides):
    profile = {
        "profile_name": "unit",
        "chemistry": "unit",
        "nominal_voltage_v": 48.0,
        "max_voltage_v": 54.0,
        "min_voltage_v": 40.0,
        "capacity_ah": 100.0,
        "max_charge_current_a": 20.0,
        "max_discharge_current_a": 50.0,
        "idle_current_a": 0.5,
        "shunt_resistance_ohm": 0.001,
        "shunt_rated_current_a": 100.0,
        "initial_soc_percent": 50.0,
        "ocv_voltage_v": [40.0, 48.0, 54.0],
        "ocv_soc_percent": [0.0, 50.0, 100.0],
        "rest_current_a": 0.5,
        "rest_duration_s": 10.0,
        "current_gain": 1.0,
        "current_offset_a": 0.0,
        "voltage_gain": 1.0,
        "voltage_offset_v": 0.0,
        "invert_current": False,
        "max_integrate_dt_s": 10000.0,
        "persist_interval_s": 1.0e9,
        "history_interval_s": 1.0e9,
        "sample_period_s": 0.5,
    }
    profile.update(overrides)
    return profile


def _monitor(tmp_path, profile, samples, history=False):
    store = StateStore(tmp_path / "state.json", profile.get("initial_soc_percent"))
    store.load()
    db = HistoryDB(tmp_path / "history.sqlite") if history else None
    sensor = ScriptedSensor(samples)
    monitor = Monitor(profile, sensor, store, history=db, simulated=True)
    return monitor


def test_signed_power_and_one_hour_discharge():
    assert signed_power_w(48.0, 10.0) == pytest.approx(480.0)
    assert signed_power_w(48.0, -10.0) == pytest.approx(-480.0)
    profile = _profile()
    state = fresh_state(50.0)
    integrate(state, 48.0, 10.0, 3600.0)
    assert state["ampere_hours_out"] == pytest.approx(10.0)
    assert state["watt_hours_out"] == pytest.approx(480.0)
    assert soc_percent(state, 100.0) == pytest.approx(40.0)
    status = status_from_current(10.0, profile["idle_current_a"], True)
    assert status == "Discharging"
    assert status_from_current(-5.0, 0.5, True) == "Charging"
    assert status_from_current(0.1, 0.5, True) == "Idle"
    assert status_from_current(10.0, 0.5, False) == "Fault"


def test_charge_increases_soc_and_runtime_directions(tmp_path):
    profile = _profile()
    monitor = _monitor(
        tmp_path,
        profile,
        [Sample(48.0, -10.0, pack_temp_c=26.0)],
    )
    snap = monitor.tick(dt=3600.0)
    assert snap["current_a"] == pytest.approx(-10.0)
    assert snap["power_w"] == pytest.approx(-480.0)
    assert snap["ampere_hours_out"] == pytest.approx(-10.0)
    assert snap["energy_wh"] == pytest.approx(-480.0)
    assert snap["soc_percent"] == pytest.approx(60.0)
    assert snap["status"] == "Charging"
    assert snap["capacity_ah"] == pytest.approx(60.0)
    assert snap["runtime_label"] == "time_to_full"
    assert snap["runtime_hours"] == pytest.approx(4.0)
    monitor.shutdown()


def test_calibration_offset_and_invert():
    voltage, current = apply_calibration(
        10.0,
        1.0,
        {"voltage_gain": 2.0, "voltage_offset_v": 0.5, "current_gain": 1.0, "current_offset_a": -0.1},
    )
    assert voltage == pytest.approx(20.5)
    assert current == pytest.approx(0.9)
    _, inverted = apply_calibration(
        10.0,
        1.0,
        {
            "voltage_gain": 1.0,
            "voltage_offset_v": 0.0,
            "current_gain": 1.0,
            "current_offset_a": 0.0,
            "invert_current": True,
        },
    )
    assert inverted == pytest.approx(-1.0)


def test_ocv_correction_once_per_rest_and_no_extrapolation():
    assert ocv_to_soc(48.0, [40.0, 48.0, 54.0], [0.0, 50.0, 100.0]) == pytest.approx(50.0)
    assert ocv_to_soc(51.0, [40.0, 48.0, 54.0], [0.0, 50.0, 100.0]) == pytest.approx(75.0)
    assert ocv_to_soc(30.0, [40.0, 54.0], [0.0, 100.0]) is None

    profile = _profile(initial_soc_percent=10.0)
    state = fresh_state(10.0)
    tracker = RestTracker()
    assert tracker.update(state, 10.0, 0.0, 51.0, profile) is True
    assert state["soc_anchor_percent"] == pytest.approx(75.0)
    assert tracker.update(state, 10.0, 0.0, 51.0, profile) is False
    assert tracker.update(state, 1.0, 5.0, 51.0, profile) is False
    assert tracker.elapsed_s == 0.0


def test_monitor_applies_ocv_and_then_counts(tmp_path):
    profile = _profile(initial_soc_percent=10.0, rest_duration_s=10.0)
    monitor = _monitor(
        tmp_path,
        profile,
        [Sample(51.0, 0.0, pack_temp_c=25.0), Sample(51.0, 10.0, pack_temp_c=25.0)],
    )
    first = monitor.tick(dt=10.0)
    assert first["ocv_corrected"] is True
    assert first["soc_percent"] == pytest.approx(75.0)
    second = monitor.tick(dt=3600.0)
    assert second["soc_percent"] == pytest.approx(65.0)
    assert second["status"] == "Discharging"
    monitor.shutdown()


def test_faults_and_comms_do_not_integrate(tmp_path):
    profile = _profile(temp_min_c=0.0, temp_max_c=45.0)
    faults = evaluate(60.0, 170.0, 50.0, profile, True)
    assert "OVERVOLTAGE" in faults
    assert "DISCHARGE_OVERCURRENT" in faults
    assert "SHUNT_SATURATED" in faults
    assert "PACK_OVERTEMP" in faults
    assert "CHARGE_OVERCURRENT" in evaluate(50.0, -30.0, 25.0, profile, True)
    assert "UNDERVOLTAGE" in evaluate(30.0, 0.0, 25.0, profile, True)
    assert evaluate(50.0, 1.0, 25.0, profile, False) == ["COMMS"]

    monitor = _monitor(
        tmp_path,
        profile,
        [Sample(48.0, 10.0, pack_temp_c=25.0), CommsError("i2c")],
    )
    good = monitor.tick(dt=1.0)
    assert good["ampere_hours_out"] == pytest.approx(10.0 / 3600.0)
    bad = monitor.tick(dt=100.0)
    assert bad["status"] == "Fault"
    assert bad["faults"] == ["COMMS"]
    assert bad["stale"] is True
    assert bad["ampere_hours_out"] == pytest.approx(good["ampere_hours_out"])
    monitor.shutdown()


def test_long_gap_is_not_counted_as_ampere_hours(tmp_path):
    profile = _profile(max_integrate_dt_s=5.0)
    monitor = _monitor(tmp_path, profile, [Sample(48.0, 10.0, pack_temp_c=25.0)])
    snap = monitor.tick(dt=1000.0)
    assert snap["ampere_hours_out"] == pytest.approx(0.0)
    assert snap["power_loss_gap"] is True
    assert snap["power_w"] == pytest.approx(480.0)
    monitor.shutdown()


def test_state_survives_restart_without_counting_downtime(tmp_path):
    profile = _profile()
    store = StateStore(tmp_path / "state.json", 50.0)
    store.load()
    monitor = Monitor(
        profile,
        ScriptedSensor([Sample(48.0, 10.0, pack_temp_c=25.0)]),
        store,
        simulated=True,
    )
    monitor.tick(dt=3600.0)
    monitor.shutdown()

    restored = StateStore(tmp_path / "state.json", 50.0)
    restored.load()
    assert restored.loaded_from_disk is True
    assert restored.state["power_loss_gap"] is True
    assert restored.state["ampere_hours_out"] == pytest.approx(10.0)
    again = Monitor(
        profile,
        ScriptedSensor([Sample(48.0, 10.0, pack_temp_c=25.0)]),
        restored,
        simulated=True,
    )
    snap = again.tick(dt=0.0)
    assert snap["ampere_hours_out"] == pytest.approx(10.0)
    assert snap["soc_percent"] == pytest.approx(40.0)
    assert snap["power_loss_gap"] is True
    again.shutdown()


def test_history_and_atomic_json(tmp_path):
    from battery_monitor.storage import atomic_write_json, load_json

    path = tmp_path / "state.json"
    atomic_write_json(path, {"ampere_hours_out": 1.25})
    assert not path.with_name(path.name + ".tmp").exists()
    assert load_json(path)["ampere_hours_out"] == 1.25
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(Exception):
        load_json(path)

    profile = _profile(history_interval_s=0.0, persist_interval_s=1.0e9)
    monitor = _monitor(
        tmp_path / "history-case",
        profile,
        [Sample(48.0, 1.0, pack_temp_c=25.0)],
        history=True,
    )
    monitor.tick(dt=1.0)
    assert monitor.history.count() == 1
    monitor.shutdown()
    reopened = HistoryDB(tmp_path / "history-case" / "history.sqlite")
    assert reopened.count() == 1
    reopened.close()


def test_simulated_waveform_has_both_signs():
    sensor = SimulatedSensor(_profile())
    currents = [sensor.read().current_a for _ in range(25)]
    assert any(value > 0 for value in currents)
    assert any(value < 0 for value in currents)
    assert any(value == 0 for value in currents)


def test_runtime_idle_is_none():
    hours, label = remaining_runtime_h(0.0, 40.0, 100.0, 0.5)
    assert hours is None and label is None
