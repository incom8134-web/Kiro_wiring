# AGENTS.md: battery monitor

This folder is a Jetson Nano charge/discharge monitor: a Matek I2C-INA-BM module on J41 I2C, and a UART log. The shunt is the module's 200 µΩ path. The display is the HAEBOT web app, which reads the atomic state file or the UART line. Do not add a web server, an LCD, a temperature sensor, a fuse, a buck, or a level shifter here.

It is not the robot power system in `kiro-wiring/` or `kiro-wiring-2/`. Do not edit those trees to match this one.

## Do not invent the battery

Chemistry, nominal voltage, maximum voltage, minimum voltage, capacity, and maximum charge and discharge current are unknown. Leave them null in `software/config/battery_profile.json`. Do not copy the synthetic simulator profile or `config/examples/example_DO_NOT_USE.json` into a hardware profile.

The module shunt (0.0002 ohm), the ±40.96 mV range, address 0x45, and the 204.8 A full scale are Matek and TI facts. Do not clear them to look like a missing pack shunt. The power-lead row in `bom/BOM.csv` stays BLOCKED until the pack current is known. Do not pick a wire gauge from the module's 150 A continuous rating.

## Specs

Cite the page for any electrical number you add. Module ratings are from https://www.mateksys.com/?portfolio=i2c-ina-bm . The INA228 register math is from TI SLYS021. The Jetson Nano header facts are from the NVIDIA Jetson Nano Developer Kit User Guide, DA_09402. The module is I2C only. The sensor cable is JST-GH-4P: 5V to pin 2, SCL to pin 5, SDA to pin 3, G to pin 6. Pin 2 is the 4–9 V logic feed (about 1 mA). Pin 1 is 3.3 V and must not feed the module. Do not use pin 4. Do not put pack voltage on the header. Pins 8 and 10 are the UART data output, `/dev/ttyTHS1`. The I2C pull-up rail is unverified: measure idle SDA before connecting, and do not add a level shifter in this folder.

## Software

Run `pytest` from `software/` after a code change. `--simulate` must keep working with no hardware. Hardware mode must still refuse an incomplete profile. The live reading for the HAEBOT web app is the atomic state file documented in `README.md`, with the same row on the UART. The driver accepts only DEVICE_ID 0x2281.
