# AGENTS.md: battery monitor

This folder is a Jetson Nano charge/discharge monitor: an external shunt, an INA228 on J41 I2C, and a UART log. The display is the web app that already runs on the Jetson. Do not add a web server, an LCD, a temperature sensor, a fuse, a buck, or a level shifter here.

It is not the robot power system in `kiro-wiring/` or `kiro-wiring-2/`. Do not edit those trees to match this one.

## Do not invent the battery

Chemistry, nominal voltage, maximum voltage, minimum voltage, capacity, and maximum charge and discharge current are unknown. Leave them null in `software/config/battery_profile.json`. Do not copy the synthetic simulator profile or `config/examples/example_DO_NOT_USE.json` into a hardware profile.

If a pack fact is missing, the shunt row in `bom/BOM.csv` stays BLOCKED. Do not pick a shunt resistance or a wire gauge as if the pack were known.

The sense and VBUS leads are unfused because the owner accepted that short-circuit risk. Do not put the fuses back unless the owner asks.

## Specs

Cite the datasheet for any electrical number you add. The INA228 limits used here are from TI SLYS021. The Jetson Nano header facts are from the NVIDIA Jetson Nano Developer Kit User Guide, DA_09402. The INA228 is I2C only. The sensor cable is pins 1, 3, 5, and 6. Pins 8 and 10 are the UART data output, `/dev/ttyTHS1`.

## Software

Run `pytest` from `software/` after a code change. `--simulate` must keep working with no hardware. Hardware mode must still refuse an incomplete profile. The live reading for the Jetson web app is the atomic state file documented in `README.md`.
