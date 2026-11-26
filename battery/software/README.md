# Battery monitor software

[English](README.md) | [한국어](README.ko.md)

Python 3.9+ service for the Jetson Orin Nano Developer Kit design in [`../README.md`](../README.md).
JetPack 6 on that kit is Ubuntu 22.04 and includes Python 3.10. JetPack 5 is Ubuntu 20.04 and includes Python 3.8, which is older than this package, so use a virtualenv built with Python 3.9 or newer.

The Matek I2C-INA-BM is read on `/dev/i2c-7` (J12 pins 3 and 5, I2C1) at address 0x45. It is I2C only. `sudo i2cdetect -y -r 7` should show 0x45. UART `/dev/ttyTHS0` (pins 8 and 10) is optional and unused. The shipped profile sets `uart_enabled` to false. The code remains for a later opt-in.

The shipped profile sets the module facts from [Matek](https://www.mateksys.com/?portfolio=i2c-ina-bm) and TI SLYS021: shunt 0.0002 ohm, `adc_range_mv` 40.96, full scale 204.8 A. At that full scale SHUNT_CAL is 4096 and CURRENT_LSB is 390.625 µA. Once the pack nameplate exists, `configure()` recomputes SHUNT_CAL from the nameplate current. The driver accepts only DEVICE_ID 0x2281. This path has not been run on a Matek board.

The pack row is YOLTON e-bike pack (Coupang 9101801616). Chemistry, voltage, capacity, and current stay null until a label or datasheet is read. Hardware mode refuses that file.

There is no web server in this package. The HAEBOT robot web app reads `/var/lib/battery-monitor/state.json`. The path is Matek INA, I2C, Jetson, state file, web app. The field list is in [`../README.md`](../README.md). The app source is not in this repo.

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

The process must be in the `i2c` group. `dialout` is only needed if `uart_enabled` is later set true. A systemd unit is in `systemd/battery-monitor.service`. `SIGTERM` writes the state file before exit.

| Module | Role |
|---|---|
| `battery_monitor/ina228.py` | INA228 register math and smbus2 driver |
| `battery_monitor/sensors.py` | Header I2C, scripted sensor, simulated waveform |
| `battery_monitor/accounting.py` | Signed power, Ah, Wh |
| `battery_monitor/soc.py` | Coulomb SOC and rest OCV correction |
| `battery_monitor/faults.py` | Voltage, current, saturation, comms |
| `battery_monitor/storage.py` | Atomic JSON state, SQLite history |
| `battery_monitor/uart_out.py` | Optional CSV lines on `/dev/ttyTHS0`. Off by default |
| `battery_monitor/service.py` | Loop, signals, CLI |

`config/battery_profile.json` ships with null nameplate fields. `config/examples/example_DO_NOT_USE.json` is a shape example and is refused on hardware.
