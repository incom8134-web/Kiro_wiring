# Battery monitor software

[English](README.md) | [한국어](README.ko.md)

Python 3.9+ service for the Jetson Nano design in [`../README.md`](../README.md).
Stock JetPack 4.6 on a Nano is Python 3.6. Use a virtualenv built with Python 3.9 or newer.

The INA228 is read on `/dev/i2c-1`. It is I2C only. UART `/dev/ttyTHS1` is the serial log, not the sensor.

There is no web server in this package. The web app that already runs on the Jetson reads `/var/lib/battery-monitor/state.json`. The field list is in [`../README.md`](../README.md).

```bash
cd battery/software
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pytest
python -m battery_monitor --simulate --duration 2
python -m battery_monitor --check-profile --config config/battery_profile.json
```

`--simulate` runs with no sensor and no real battery profile.

Hardware start, after `config/battery_profile.json` is filled in from the pack datasheet:

```bash
python -m battery_monitor --config config/battery_profile.json \
  --state /var/lib/battery-monitor/state.json \
  --history /var/lib/battery-monitor/history.sqlite
```

The process must be in the `i2c` and `dialout` groups. A systemd unit is in `systemd/battery-monitor.service`. `SIGTERM` writes the state file before exit.

| Module | Role |
|---|---|
| `battery_monitor/ina228.py` | INA228 register math and smbus2 driver |
| `battery_monitor/sensors.py` | Header I2C, scripted sensor, simulated waveform |
| `battery_monitor/accounting.py` | Signed power, Ah, Wh |
| `battery_monitor/soc.py` | Coulomb SOC and rest OCV correction |
| `battery_monitor/faults.py` | Voltage, current, saturation, comms |
| `battery_monitor/storage.py` | Atomic JSON state, SQLite history |
| `battery_monitor/uart_out.py` | CSV lines on `/dev/ttyTHS1` |
| `battery_monitor/service.py` | Loop, signals, CLI |

`config/battery_profile.json` ships with null nameplate fields. `config/examples/example_DO_NOT_USE.json` is a shape example and is refused on hardware.
