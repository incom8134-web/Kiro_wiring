# Battery monitor software

[English](README.md) | [한국어](README.ko.md)

Python 3.9+ service for the Jetson Nano design in [`../README.md`](../README.md).
Stock JetPack 4.6 on a Nano is Python 3.6. Use a virtualenv built with Python 3.9 or newer.

The Matek I2C-INA-BM is read on `/dev/i2c-1` at address 0x45. It is I2C only. UART `/dev/ttyTHS1` is the serial log, not the sensor.

The shipped profile sets the module facts from [Matek](https://www.mateksys.com/?portfolio=i2c-ina-bm) and TI SLYS021: shunt 0.0002 ohm, `adc_range_mv` 40.96, full scale 204.8 A. At that full scale SHUNT_CAL is 4096 and CURRENT_LSB is 390.625 µA. Once the pack nameplate exists, `configure()` recomputes SHUNT_CAL from the nameplate current. The driver accepts only DEVICE_ID 0x2281. This path has not been run on a Matek board.

There is no web server in this package. The HAEBOT robot web app reads `/var/lib/battery-monitor/state.json` or the UART CSV on `/dev/ttyTHS1`. The field list is in [`../README.md`](../README.md). The app source is not in this repo.

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
