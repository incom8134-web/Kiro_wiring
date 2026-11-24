"""Monitor loop: read, integrate, store, display, serve.

The first tick after start does not integrate across the time the process
was not running. A tick whose dt is longer than ``max_integrate_dt_s`` is
treated the same way: the current sample is shown, and the gap is not
invented as ampere-hours.
"""

from __future__ import annotations

import argparse
import copy
import signal
import sys
import threading
import time
from pathlib import Path

from . import __version__
from .accounting import (
    apply_calibration,
    fresh_state,
    integrate,
    remaining_ah,
    remaining_runtime_h,
    soc_percent,
    status_from_current,
)
from .faults import evaluate
from .lcd import NullDisplay, format_lines
from .profile import resolve_profile, validate_profile
from .sensors import CommsError, HardwareSensor, SimulatedSensor
from .soc import RestTracker
from .storage import HistoryDB, StateStore
from .uart_out import UartLogger


class Monitor:
    def __init__(self, profile: dict, sensor, store: StateStore, history: HistoryDB | None = None,
                 display=None, uart: UartLogger | None = None, simulated: bool = False):
        self.profile = profile
        self.sensor = sensor
        self.store = store
        self.history = history
        self.display = display if display is not None else NullDisplay()
        self.uart = uart
        self.simulated = simulated
        self.rest = RestTracker()
        self.state = store.state
        self._lock = threading.Lock()
        self._snapshot = {}
        self._last_mono = None
        self._last_persist = None
        self._last_history = None
        self._comms_failures = 0
        self.publish(self._blank_snapshot(comms_ok=False, faults=[]))

    def _blank_snapshot(self, comms_ok: bool, faults: list[str]) -> dict:
        capacity = float(self.profile["capacity_ah"])
        return {
            "profile_name": self.profile.get("profile_name"),
            "chemistry": self.profile.get("chemistry"),
            "voltage_v": None,
            "current_a": None,
            "power_w": None,
            "soc_percent": soc_percent(self.state, capacity),
            "soc_unclamped_percent": soc_percent(self.state, capacity, clamp=False),
            "capacity_ah": remaining_ah(self.state, capacity),
            "nominal_capacity_ah": capacity,
            "energy_wh": float(self.state.get("watt_hours_out", 0.0)),
            "ampere_hours_out": float(self.state.get("ampere_hours_out", 0.0)),
            "status": "Fault" if not comms_ok else "Idle",
            "temperature_c": None,
            "die_temperature_c": None,
            "runtime_hours": None,
            "runtime_label": None,
            "faults": list(faults),
            "comms_ok": comms_ok,
            "stale": not comms_ok,
            "simulated": self.simulated,
            "power_loss_gap": bool(self.state.get("power_loss_gap")),
            "ocv_corrected": False,
            "updated_unix": time.time(),
        }

    def publish(self, snapshot: dict) -> None:
        with self._lock:
            self._snapshot = snapshot

    def snapshot(self) -> dict:
        with self._lock:
            return copy.deepcopy(self._snapshot)

    def tick(self, dt: float | None = None, now: float | None = None) -> dict:
        mono = time.monotonic()
        if dt is None:
            if self._last_mono is None:
                dt = 0.0
            else:
                dt = mono - self._last_mono
        self._last_mono = mono
        wall = time.time() if now is None else now
        max_dt = float(self.profile.get("max_integrate_dt_s", 5.0))
        gap = dt > max_dt
        integrate_dt = 0.0 if gap else dt
        if gap:
            self.state["power_loss_gap"] = True

        try:
            sample = self.sensor.read()
        except CommsError:
            self._comms_failures += 1
            faults = ["COMMS"]
            snap = self._blank_snapshot(comms_ok=False, faults=faults)
            snap["updated_unix"] = wall
            self._output(snap, wall)
            return snap

        self._comms_failures = 0
        voltage, current = apply_calibration(sample.voltage_v, sample.current_a, self.profile)
        power = integrate(self.state, voltage, current, integrate_dt)
        ocv_corrected = False
        if not gap:
            ocv_corrected = self.rest.update(self.state, integrate_dt, current, voltage, self.profile)
        else:
            self.rest.reset()
        capacity = float(self.profile["capacity_ah"])
        idle = float(self.profile["idle_current_a"])
        faults = evaluate(
            voltage,
            current,
            sample.pack_temp_c,
            self.profile,
            comms_ok=True,
            memstat_ok=sample.memstat_ok,
            math_overflow=sample.math_overflow,
        )
        remaining = remaining_ah(self.state, capacity)
        runtime, runtime_label = remaining_runtime_h(current, remaining, capacity, idle)
        snap = {
            "profile_name": self.profile.get("profile_name"),
            "chemistry": self.profile.get("chemistry"),
            "voltage_v": voltage,
            "current_a": current,
            "power_w": power,
            "soc_percent": soc_percent(self.state, capacity),
            "soc_unclamped_percent": soc_percent(self.state, capacity, clamp=False),
            "capacity_ah": remaining,
            "nominal_capacity_ah": capacity,
            "energy_wh": float(self.state.get("watt_hours_out", 0.0)),
            "ampere_hours_out": float(self.state.get("ampere_hours_out", 0.0)),
            "status": status_from_current(current, idle, True),
            "temperature_c": sample.pack_temp_c,
            "die_temperature_c": sample.die_temp_c,
            "runtime_hours": runtime,
            "runtime_label": runtime_label,
            "faults": faults,
            "comms_ok": True,
            "stale": False,
            "simulated": self.simulated,
            "power_loss_gap": bool(self.state.get("power_loss_gap")),
            "ocv_corrected": ocv_corrected,
            "updated_unix": wall,
        }
        self._output(snap, wall)
        return snap

    def _output(self, snap: dict, wall: float) -> None:
        self.publish(snap)
        try:
            self.display.write_lines(format_lines(snap))
        except OSError:
            pass
        if self.uart is not None:
            try:
                self.uart.write_snapshot(snap)
            except OSError:
                pass
        self._maybe_persist(wall, snap)

    def _maybe_persist(self, wall: float, snap: dict) -> None:
        persist_every = float(self.profile.get("persist_interval_s", 30.0))
        history_every = float(self.profile.get("history_interval_s", 10.0))
        if self._last_persist is None or wall - self._last_persist >= persist_every:
            self.store.save()
            self._last_persist = wall
        if self.history is not None and (
            self._last_history is None or wall - self._last_history >= history_every
        ):
            self.history.insert(snap)
            self._last_history = wall

    def shutdown(self) -> None:
        self.store.save()
        if self.history is not None:
            self.history.close()
            self.history = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Jetson Nano battery charge/discharge monitor")
    parser.add_argument("--config", default=None, help="battery profile JSON")
    parser.add_argument("--simulate", action="store_true", help="use the simulated sensor")
    parser.add_argument("--allow-example", action="store_true", help="permit an example_only profile")
    parser.add_argument("--check-profile", action="store_true", help="validate the profile and exit")
    parser.add_argument("--state", default="run/state.json")
    parser.add_argument("--history", default="run/history.sqlite")
    parser.add_argument("--duration", type=float, default=None, help="exit after N seconds")
    parser.add_argument("--no-web", action="store_true")
    parser.add_argument("--version", action="store_true")
    return parser


def check_profile(path: str, allow_example: bool) -> int:
    from .profile import load_profile

    profile = load_profile(path)
    errors, warnings = validate_profile(profile, allow_example=allow_example)
    if warnings:
        print("Warnings:")
        for line in warnings:
            print(f"  - {line}")
    if errors:
        print("Profile is not usable on hardware. Still required:")
        for line in errors:
            print(f"  - {line}")
        return 2
    print(f"Profile '{profile.get('profile_name')}' passed the checks.")
    return 0


def _start_web(monitor: Monitor, host: str, port: int) -> None:
    import uvicorn

    from .dashboard import create_app

    app = create_app(monitor.snapshot)
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="battery-dashboard", daemon=True)
    thread.start()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.version:
        print(__version__)
        return 0
    if args.check_profile:
        if not args.config:
            print("pass --config with --check-profile", file=sys.stderr)
            return 2
        return check_profile(args.config, args.allow_example)

    try:
        profile, notes = resolve_profile(args.config, args.simulate, args.allow_example)
    except (OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    for note in notes:
        print(f"note: {note}", file=sys.stderr)

    store = StateStore(args.state, profile.get("initial_soc_percent"))
    store.load()
    if not store.loaded_from_disk and profile.get("initial_soc_percent") is None:
        print(
            "note: no saved state and initial_soc_percent is null. "
            "SOC stays unknown until you set it or an OCV rest correction runs. "
            "Ampere-hours still accumulate from zero.",
            file=sys.stderr,
        )
    history = HistoryDB(args.history)
    if args.simulate:
        sensor = SimulatedSensor(profile)
    else:
        sensor = HardwareSensor(profile)
        try:
            sensor.open()
        except (OSError, ValueError) as exc:
            print(f"sensor open failed: {exc}", file=sys.stderr)
            return 2

    display = NullDisplay()
    if profile.get("lcd_enabled", True) and not args.simulate:
        display = _open_lcd(profile)
    uart = None
    if profile.get("uart_enabled", True):
        from .uart_out import open_uart

        uart = open_uart(
            str(profile.get("uart_device", "/dev/ttyTHS1")),
            int(profile.get("uart_baud", 115200)),
            required=False,
        )
        if uart.disabled_reason:
            print(f"note: UART disabled: {uart.disabled_reason}", file=sys.stderr)

    monitor = Monitor(
        profile,
        sensor,
        store,
        history=history,
        display=display,
        uart=uart,
        simulated=args.simulate or bool(profile.get("example_only")),
    )
    if not args.no_web:
        host = str(profile.get("web_host", "0.0.0.0"))
        port = int(profile.get("web_port", 8080))
        try:
            _start_web(monitor, host, port)
            print(f"dashboard http://{host}:{port}", file=sys.stderr)
        except OSError as exc:
            print(f"dashboard did not start: {exc}", file=sys.stderr)

    stop = {"flag": False}

    def _handle_signal(_signum, _frame):
        stop["flag"] = True

    previous_term = signal.signal(signal.SIGTERM, _handle_signal)
    previous_int = signal.signal(signal.SIGINT, _handle_signal)
    period = float(profile.get("sample_period_s", 0.5))
    deadline = None if args.duration is None else time.monotonic() + args.duration
    try:
        while not stop["flag"]:
            monitor.tick()
            if deadline is not None and time.monotonic() >= deadline:
                break
            time.sleep(period)
    finally:
        signal.signal(signal.SIGTERM, previous_term)
        signal.signal(signal.SIGINT, previous_int)
        monitor.shutdown()
        closer = getattr(sensor, "close", None)
        if closer:
            closer()
    return 0


def _open_lcd(profile: dict):
    from .lcd import PCF8574LCD
    from .sensors import parse_address, parse_i2c_bus

    try:
        import smbus2

        bus = smbus2.SMBus(parse_i2c_bus(profile.get("i2c_bus", "/dev/i2c-1")))
        return PCF8574LCD(bus, address=parse_address(profile.get("lcd_address", "0x27")))
    except (OSError, ImportError) as exc:
        print(f"note: LCD disabled: {exc}", file=sys.stderr)
        return NullDisplay()


def fresh_demo_state() -> dict:
    """Kept for tests that want a known starting point without the store."""
    return fresh_state(50.0)
