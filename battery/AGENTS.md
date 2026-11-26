# AGENTS.md: battery monitor

This folder is a Jetson Orin Nano Developer Kit charge/discharge monitor: a Matek I2C-INA-BM module on J12 I2C (`/dev/i2c-7`). The shunt is the module's 200 µΩ path. The display is the HAEBOT web app, which reads the atomic state file. The path is Matek INA, I2C, Jetson, `state.json`, web app. UART on J12 pins 8 and 10 (`/dev/ttyTHS0`) is optional and unused; the profile ships with `uart_enabled` false. Do not add a web server, an LCD, a temperature sensor, a fuse, or a buck here.

It is not the robot power system in `kiro-wiring/` or `kiro-wiring-2/`. Do not edit those trees to match this one.

## Do not invent the battery

The pack is the user-confirmed YOLTON e-bike pack (Coupang 9101801616): li-ion, nominal 12.0 V, capacity 45 Ah. Volton's 12 V 45 Ah page says LG cells. `cell_configuration` 3S, `max_voltage_v` 12.6, and `min_voltage_v` 9.0 are assumed for 3S Li-ion; verify with a meter at full charge. Do not replace those with a different series count.

`max_charge_current_a` and `max_discharge_current_a` stay null. There is no unverified-number flag, so do not insert a placeholder current. The service starts with those fields null, and the overcurrent alarms stay off. Do not copy the synthetic simulator profile or `config/examples/example_DO_NOT_USE.json` into a hardware profile.

The module shunt (0.0002 ohm), the ±40.96 mV range, address 0x45, and the 204.8 A full scale are Matek and TI facts. Do not clear them to look like a missing pack shunt. While the pack current is null, SHUNT_CAL stays at that full scale. The power-lead row in `bom/BOM.csv` stays BLOCKED until the pack current is known. Do not pick a wire gauge from the module's 150 A continuous rating. Charge with a 12.6 V CC/CV Li-ion charger (Volton's own charger), not a plain 12 V power adapter.

## Specs

Cite the page for any electrical number you add. Module ratings are from https://www.mateksys.com/?portfolio=i2c-ina-bm . The INA228 register math is from TI SLYS021. The Jetson Orin Nano header facts are from the Jetson Orin Nano Developer Kit Carrier Board Specification, SP-11324-001, connector J12. Linux `/dev/i2c-7` and `/dev/ttyTHS0` follow https://jetsonhacks.com/nvidia-jetson-orin-nano-gpio-header-pinout/ . The module is I2C only. The sensor cable is JST-GH-4P: 5V to pin 2, SDA to pin 3 (I2C1_SDA, bus 7), SCL to pin 5 (I2C1_SCL, bus 7), G to pin 6. Pin 2 is the 4–9 V logic feed (about 1 mA). Pin 1 is 3.3 V and must not feed the module. Do not use pin 4. Do not put pack voltage on the header. Pin 1 is the header end nearest the USB and Ethernet ports; pins 39 and 40 are toward the fan. Confirm with a meter that pin 1 is 3.3 V and pin 2 is 5 V. `sudo i2cdetect -y -r 7` should show 0x45. Header signals are 3.3 V and are not 5 V tolerant. The I2C pull-up rail is unverified: measure idle SDA before connecting. If it is above about 3.6 V, use a BSS138 level shifter. Do not fit a shifter when the idle voltage is already about 3.3 V. Pins 8 and 10 are the optional UART, `/dev/ttyTHS0`, and stay unused.

## Software

Run `pytest` from `software/` after a code change. `--simulate` must keep working with no hardware. Hardware mode must still refuse a profile that is missing chemistry, voltage, or capacity. Null charge and discharge current is a warning, and the service still starts. The live reading for the HAEBOT web app is the atomic state file documented in `README.md`. UART stays off unless `uart_enabled` is true. The driver accepts only DEVICE_ID 0x2281.
