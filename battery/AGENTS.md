# AGENTS.md: battery monitor

This folder is a Jetson Nano charge/discharge monitor. It is not the robot power system in `kiro-wiring/` or `kiro-wiring-2/`. Do not edit those trees to match this one.

## Do not invent the battery

Chemistry, nominal voltage, maximum voltage, minimum voltage, capacity, and maximum charge and discharge current are unknown. Leave them null in `software/config/battery_profile.json`. Do not copy the synthetic simulator profile or `config/examples/example_DO_NOT_USE.json` into a hardware profile.

If a pack fact is missing, the row in `bom/BOM.csv` stays BLOCKED. Do not pick a shunt resistance, a main fuse, a wire gauge, or a buck converter as if the pack were known.

## Specs

Cite the datasheet for any electrical number you add. The INA228 limits used here are from TI SLYS021. The Jetson Nano power and header facts are from the NVIDIA Jetson Nano Developer Kit User Guide. This design is the original Nano (5 V barrel), not the Jetson Orin Nano.

## Software

Run `pytest` from `software/` after a code change. `--simulate` must keep working with no hardware. Hardware mode must still refuse an incomplete profile.
