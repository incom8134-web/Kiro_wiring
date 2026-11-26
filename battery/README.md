# Jetson Nano battery monitor

[English](README.md) | [한국어](README.ko.md)

This monitor reads one battery pack through a Matek I2C-INA-BM module on the Jetson Nano I2C header. The module's conductive path is the shunt. The service counts coulombs, estimates state of charge, writes a JSON file, and prints the same readings on the UART. The HAEBOT robot web app reads that file, or the UART line. This folder does not contain a web server.

The pack chemistry, voltages, capacity, and currents are not known. Those fields are null in [`software/config/battery_profile.json`](software/config/battery_profile.json). The program will not open the real sensor until they are filled in from the pack datasheet. The power-lead row in [`bom/BOM.csv`](bom/BOM.csv) stays BLOCKED until then. The module shunt, address, and ADC range are filled from the Matek page and are not a guess at the pack. Nothing in the example file is a suggested pack.

This is not a battery management system. It does not balance cells and it does not open a contactor.

## What is connected

| Part | Role |
|---|---|
| Matek I2C-INA-BM | In the battery positive lead. Pack current enters BAT+ and leaves ESC+. The conductive path is 200 µΩ typical. |
| JST-GH-4P | Logic and I2C: 5V, SCL, SDA, G. Address 0x45 (decimal 69) with the jumpers open. |
| Jetson Nano | Reads `/dev/i2c-1` and writes the state file and `/dev/ttyTHS1`. Pin 2 feeds the module's 4–9 V pin. |

The bus range is 0 V to 85 V (Matek page and TI SLYS021). If the pack can exceed 85 V, do not connect it. The profile loader rejects that case. Matek rates the path at 150 A continuous and 204.8 A burst. At 200 µΩ that burst is 40.96 mV, so the profile uses the ±40.96 mV ADC range. Full-scale calibration is CURRENT_LSB = 204.8 / 2^19 = 390.625 µA and SHUNT_CAL = 4096 (SLYS021). After the pack nameplate is filled in, the driver recomputes SHUNT_CAL from that current, still with 200 µΩ and the ±40.96 mV range. Continuous current above 150 A produces a warning. This code has not been run on a Matek board.

The official page lists INA228 and INA238. The driver accepts only DEVICE_ID 0x2281 and refuses any other ID. Which chip is fitted is unverified until that register is read.

Positive current is discharge, from BAT+ toward ESC+. Negative current is charge. Power uses the same sign.

![Matek module to the Jetson I2C header, and the UART output](wiring/battery_monitor_wiring.png)

The module is I2C only. It has no UART pins.

The cable from the module to the Jetson is the JST-GH-4P lead supplied with the module: 5V to J41 pin 2, SCL to pin 5, SDA to pin 3, G to pin 6. Pins 3 and 5 are `/dev/i2c-1` (NVIDIA Jetson Nano Developer Kit User Guide, DA_09402). The module's 5V pin is a 4–9 V input and draws about 1 mA, so pin 2 (5 V) can feed it. Pin 1 is 3.3 V and must not be tied to that pin. Do not use pin 4. Do not put pack voltage on a header pin.

The I2C pull-up rail on the module is unverified. Matek's red LED is labeled a 3.3 V indicator, which only says the board has a regulator; it does not say the pull-ups go to 3.3 V. With only the 5V pin and GND connected, measure idle SDA and SCL. About 3.3 V: connect them to pins 3 and 5. Above about 3.6 V: do not connect. This folder does not add a level shifter.

UART pins 8 (TX) and 10 (RX) are `/dev/ttyTHS1`. That port is the serial data output. It is not the connection to the module.

The power leads are the pack conductors on BAT+ and ESC+. Their gauge is not chosen, because the pack current is unknown. Do not size them from the module's 150 A rating.

## How the HAEBOT web app reads the data

The display is the HAEBOT robot web app. Its source is not in this repo. This service does not serve a page, and the app should not open the module itself. There is no HTTP or WebSocket server in this folder. The app gets the same row two ways: the JSON file below, and the UART CSV.

The app reads one file:

`/var/lib/battery-monitor/state.json`

That is the path in [`software/systemd/battery-monitor.service`](software/systemd/battery-monitor.service). A hand run from `software/` writes `run/state.json` unless you pass `--state`. The file is replaced atomically (write a temp file, fsync, rename). The shipped profile rewrites it every sample (`persist_interval_s` 0.5). `SIGTERM` writes it once more before exit.

| Field | Meaning |
|---|---|
| `updated_unix` | Seconds since the epoch, from the sample that produced this file. |
| `voltage_v` | Pack voltage at VBUS. Null when the last read failed. |
| `current_a` | Signed amperes. Positive is discharge. |
| `power_w` | `voltage_v * current_a`. Positive power leaves the battery. |
| `soc_percent` | State of charge, clamped to 0–100. Null until an anchor exists. |
| `soc_unclamped_percent` | Same count without the clamp. |
| `capacity_ah` | Remaining ampere-hours. |
| `nominal_capacity_ah` | Capacity from the profile. |
| `energy_wh` | Accumulated watt-hours out. Charge makes this fall. |
| `ampere_hours_out` | Accumulated ampere-hours out. This is the resume counter. |
| `watt_hours_out` | Same quantity as `energy_wh`. Kept so a restart can continue the integral. |
| `soc_anchor_percent`, `ah_at_anchor` | Coulomb-count anchor. The app can ignore these. |
| `status` | `Charging`, `Discharging`, `Idle`, or `Fault`. |
| `runtime_hours`, `runtime_label` | Remaining time while discharging, or time to full while charging. `runtime_label` is `remaining` or `time_to_full`. |
| `faults` | List of alarm names. Empty when the sample is inside the profile limits. |
| `comms_ok` | False when the INA228 read failed. |
| `stale` | True when `comms_ok` is false. |
| `simulated` | True when the process is on the simulated sensor. |
| `power_loss_gap` | True after a restart or a long gap. The downtime was not integrated. |
| `ocv_corrected` | True on the sample that applied a rest open-circuit correction. |
| `profile_name`, `chemistry` | Copied from the profile. |

If `comms_ok` is false, `voltage_v` and `current_a` are null. Use `updated_unix` to see how old the file is.

A SQLite history file is written beside it (`/var/lib/battery-monitor/history.sqlite`). That file is a log. The live reading is the JSON file.

The service samples every `sample_period_s` (0.5 s in the shipped profile) and rewrites the file every `persist_interval_s` (also 0.5 s). Alarms in `faults` use the pack limits in the profile. Those limits are still null, so hardware mode will not run, and no pack alarm threshold is invented here. The module ceilings the loader does enforce, once a nameplate exists, are 85 V and the shunt full scale. A nameplate above 150 A warns against the Matek continuous rating.

The same row is printed on `/dev/ttyTHS1` at 115200 baud, 3.3 V, one CSV line per sample:

```text
unix_s,voltage_v,current_a,power_w,soc_percent,capacity_ah,energy_wh,status,faults
```

`capacity_ah` on that line is the remaining ampere-hours. `faults` are joined with `|`.

## Case

The printed case holds the Matek module. The shunt is on that board, so there is no separate shunt plate. Body **33.8 × 26.8 × 11.8 mm**. With the two mounting tabs, the base is **49.8 × 26.8 × 10.0 mm**. Cavity **29.4 × 22.4 × 8.2 mm**. The board size used here is Matek's 27 × 20 × 6 mm. Wall 2.2 mm, floor 1.8 mm, lid 1.8 mm. Fit clearance is 1.2 mm per side. The lid print is **33.8 × 26.8 × 4.2 mm** with the outer face on the bed.

Openings, all open at the top: a power-lead slot in each short wall (6 mm, a printable default, not a chosen gauge), and two JST-GH slots in one long wall (11 mm). The JST side follows the product photo, not a dimensioned drawing. A retailer φ3 mm PCB hole is not on mateksys.com and is not used. Tabs take M3 clearance holes (3.4 mm). Floor and lid vents sit over the on-board shunt. The bottom pad Matek calls dead is held off the floor by 1.2 mm pads at the corners.

The Jetson is not in the box.

![Matek module case, base and lifted lid](enclosure/preview.png)

Regenerate with `python3 enclosure.py` from `battery/enclosure`. Details are in [`enclosure/README.md`](enclosure/README.md).

## Software

Run and test notes: [`software/README.md`](software/README.md). Parts: [`bom/BOM.csv`](bom/BOM.csv).
