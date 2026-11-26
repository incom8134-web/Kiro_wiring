# Jetson Orin Nano battery monitor

[English](README.md) | [한국어](README.ko.md)

This monitor reads one battery pack through a Matek I2C-INA-BM module on the Jetson Orin Nano Developer Kit 40-pin header, J12. The module's conductive path is the shunt. The Jetson counts coulombs, estimates state of charge, and writes a JSON file. The live path is Matek INA, I2C, Jetson, `state.json`, HAEBOT web app. UART on pins 8 and 10 is optional and is not used. This folder does not contain a web server.

The pack is a YOLTON e-bike pack (Coupang 9101801616): a black rectangular pack with red and black leads, DC barrel connectors, and a small BMS box. The user confirmed 12 V and 45 Ah. Volton's 12 V 45 Ah listing says lithium-ion with LG cells ([voltonbattery.com 12 V 45 Ah](https://www.voltonbattery.com/12v/?idx=407), [Coupang 9101801616](https://www.coupang.com/vp/products/9101801616?vendorItemId=93727752087)). [`software/config/battery_profile.json`](software/config/battery_profile.json) uses chemistry `li-ion`, nominal 12.0 V, and capacity 45 Ah.

The cell configuration is an assumed 3S string. `max_voltage_v` 12.6 and `min_voltage_v` 9.0 are assumed for 3S Li-ion; verify with a meter at full charge. 12.6 V is 3 × 4.2 V and 9.0 V is 3 × 3.0 V. Those two voltages are not printed on the Volton page.

Charge and discharge current are still unverified. The profile leaves `max_charge_current_a` and `max_discharge_current_a` null. The loader has no flag that would let a placeholder number stay marked unverified, so no current number is invented. The service still starts. Overcurrent alarms stay off, and SHUNT_CAL stays at the Matek full scale. The power-lead row in [`bom/BOM.csv`](bom/BOM.csv) stays BLOCKED until the current is known. The module shunt, address, and ADC range are filled from the Matek page and are not a guess at the pack. Nothing in the example file is a suggested pack.

Charge the pack with a 12.6 V CC/CV Li-ion charger (Volton's own charger). Do not use a plain 12 V power adapter.

This is not a battery management system. It does not balance cells and it does not open a contactor.

## What is connected

| Part | Role |
|---|---|
| Matek I2C-INA-BM | In the battery positive lead. Pack current enters BAT+ and leaves ESC+. The conductive path is 200 µΩ typical. |
| JST-GH-4P | Logic and I2C: 5V, SCL, SDA, G. Address 0x45 (decimal 69) with the jumpers open. |
| Jetson Orin Nano Developer Kit | Reads `/dev/i2c-7` on J12 and writes the state file. Pin 2 feeds the module's 4–9 V pin. UART is off. |

The bus range is 0 V to 85 V (Matek page and TI SLYS021). If the pack can exceed 85 V, do not connect it. The profile loader rejects that case. Matek rates the path at 150 A continuous and 204.8 A burst. At 200 µΩ that burst is 40.96 mV, so the profile uses the ±40.96 mV ADC range. Full-scale calibration is CURRENT_LSB = 204.8 / 2^19 = 390.625 µA and SHUNT_CAL = 4096 (SLYS021). The shipped profile has no pack current, so the driver keeps that full-scale calibration. After a pack current limit is filled in, the driver recomputes SHUNT_CAL from that current, still with 200 µΩ and the ±40.96 mV range. Continuous current above 150 A produces a warning. This code has not been run on a Matek board.

The official page lists INA228 and INA238. The driver accepts only DEVICE_ID 0x2281 and refuses any other ID. Which chip is fitted is unverified until that register is read.

Positive current is discharge, from BAT+ toward ESC+. Negative current is charge. Power uses the same sign.

![Matek module to Jetson Orin Nano J12. UART is optional and unused](wiring/battery_monitor_wiring.png)

The module is I2C only. It has no UART pins.

The cable from the module to the Jetson is the JST-GH-4P lead supplied with the module: Matek 5V to J12 pin 2 (5 V), SDA to pin 3 (I2C1_SDA), SCL to pin 5 (I2C1_SCL), G to pin 6 (GND). Pins 3 and 5 are I2C bus 7, `/dev/i2c-7` (Jetson Orin Nano Developer Kit Carrier Board Specification, SP-11324-001, header J12; Linux device map on the [JetsonHacks Orin Nano pinout](https://jetsonhacks.com/nvidia-jetson-orin-nano-gpio-header-pinout/)). `sudo i2cdetect -y -r 7` should show 0x45. The module's 5V pin is a 4–9 V input and draws about 1 mA, so pin 2 (5 V) can feed it. Pin 1 is 3.3 V and must not be tied to that pin. Do not use pin 4. Do not put pack voltage on a header pin.

Pin 1 (3.3 V) is the end of J12 nearest the USB and Ethernet ports. Pins 39 and 40 are toward the fan. The JetsonHacks photo marks pin 1 beside the Ethernet jack, and the [NVIDIA hardware layout](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html) shows that port cluster at one end of the header and the module fan at the other. Before wiring, confirm with a multimeter: pin 1 is 3.3 V and pin 2 is 5 V.

Jetson I2C is 3.3 V, not 5 V tolerant. SP-11324-001 says every signal on J12 uses 3.3 V levels. The I2C pull-up rail on the Matek module is unverified. Matek's red LED is labeled a 3.3 V indicator, which only says the board has a regulator; it does not say the pull-ups go to 3.3 V. With only the 5V pin and GND connected, measure idle SDA. About 3.3 V: connect SDA and SCL to pins 3 and 5. Above about 3.6 V: use a BSS138 level shifter before those pins.

UART pins 8 (UART1_TXD) and 10 (UART1_RXD) are `/dev/ttyTHS0`. That port is optional and is not used. The shipped profile sets `uart_enabled` to false. It is not the connection to the module.

The power leads are the pack conductors on BAT+ and ESC+. Their gauge is not chosen, because the pack current is unknown. Do not size them from the module's 150 A rating.

## How the HAEBOT web app reads the data

The display is the HAEBOT robot web app. Its source is not in this repo. This service does not serve a page, and the app should not open the module itself. There is no HTTP or WebSocket server in this folder. The app reads the JSON file below. The optional UART CSV is not part of this design.

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

The service samples every `sample_period_s` (0.5 s in the shipped profile) and rewrites the file every `persist_interval_s` (also 0.5 s). Voltage alarms use 12.6 V and 9.0 V, which are assumed for 3S Li-ion; verify with a meter at full charge. Charge and discharge current are null, so those overcurrent alarms are off. The module ceilings the loader does enforce are 85 V and, once a pack current is filled in, the shunt full scale. A nameplate above 150 A warns against the Matek continuous rating.

UART logging is optional code and is off by default (`uart_enabled` false). Turning it on prints the same row on `/dev/ttyTHS0` at 115200 baud, 3.3 V, one CSV line per sample:

```text
unix_s,voltage_v,current_a,power_w,soc_percent,capacity_ah,energy_wh,status,faults
```

`capacity_ah` on that line is the remaining ampere-hours. `faults` are joined with `|`. The current design does not enable this.

## Case

The printed case holds the Matek module. The shunt is on that board, so there is no separate shunt plate. Body **33.8 × 26.8 × 11.8 mm**. With the two mounting tabs, the base is **49.8 × 26.8 × 10.0 mm**. Cavity **29.4 × 22.4 × 8.2 mm**. The board size used here is Matek's 27 × 20 × 6 mm. Wall 2.2 mm, floor 1.8 mm, lid 1.8 mm. Fit clearance is 1.2 mm per side. The lid print is **33.8 × 26.8 × 4.2 mm** with the outer face on the bed.

Openings, all open at the top: a power-lead slot in each short wall (6 mm, a printable default, not a chosen gauge), and two JST-GH slots in one long wall (11 mm). The JST side follows the product photo, not a dimensioned drawing. A retailer φ3 mm PCB hole is not on mateksys.com and is not used. Tabs take M3 clearance holes (3.4 mm). Floor and lid vents sit over the on-board shunt. The bottom pad Matek calls dead is held off the floor by 1.2 mm pads at the corners.

The Jetson is not in the box.

![Matek module case, base and lifted lid](enclosure/preview.png)

Regenerate with `python3 enclosure.py` from `battery/enclosure`. Details are in [`enclosure/README.md`](enclosure/README.md).

## Software

Run and test notes: [`software/README.md`](software/README.md). Parts: [`bom/BOM.csv`](bom/BOM.csv).
