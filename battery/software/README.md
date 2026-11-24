# Battery monitor software

[English](README.md) | [한국어](README.ko.md)

Python 3.9+ service for the Jetson Nano design in [`../README.md`](../README.md).
Stock JetPack 4.6 on a Nano is Python 3.6. Use a virtualenv built with Python 3.9 or newer.

```bash
cd battery/software
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pytest
python -m battery_monitor --simulate --duration 2 --no-web
python -m battery_monitor --check-profile --config config/battery_profile.json
```

`--simulate` runs with no sensor and no real battery profile. The dashboard, if you omit `--no-web`, is at `http://<host>:8080`. It is a local page. Nothing is sent to a cloud service.

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
| `battery_monitor/tmp117.py` | Pack temperature |
| `battery_monitor/sensors.py` | Hardware bus, scripted sensor, simulated waveform |
| `battery_monitor/accounting.py` | Signed power, Ah, Wh |
| `battery_monitor/soc.py` | Coulomb SOC and rest OCV correction |
| `battery_monitor/faults.py` | Voltage, current, temperature, saturation, comms |
| `battery_monitor/storage.py` | Atomic JSON state, SQLite history |
| `battery_monitor/lcd.py` | 20×4 PCF8574 LCD |
| `battery_monitor/uart_out.py` | CSV lines on `/dev/ttyTHS1` |
| `battery_monitor/dashboard.py` | FastAPI page and server-sent events |
| `battery_monitor/service.py` | Loop, signals, CLI |

`config/battery_profile.json` ships with null nameplate fields. `config/examples/example_DO_NOT_USE.json` is a shape example and is refused on hardware.
