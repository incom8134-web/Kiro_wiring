# Wiring connection table: EV battery design (Rev B, 2026-11-26)

Matches `kicad/HAEBOT_EV.kicad_sch` and `exports/HAEBOT_EV_NETLIST.net`. Power wires (W), USB data links (U-) and I2C links (I-) are listed separately. Physical header pin mapping remains pending.

| ID | From | To | Net / signal | Voltage | Current | Cable and connector | Status |
|---|---|---|---|---|---|---|---|
| W01 | BT1 + | F1 -> SW1 -> U6 BAT+; U6 ESC+ -> battery bus | BATT_F / BATT_SW / BATT_MON | 10.0-14.6 V | 17 A design, 34 A worst | 8 AWG, ring terminals, F1 within 150 mm of B+ | Proposed |
| W02 | BT1 - | negative bus bar (star point) | POWER_GND | 0 V | as W01 | 8 AWG | Proposed |
| W03 | J2 charger inlet | F2 -> battery side of SW1 | BATT_F | charge voltage | TBD | 14 AWG, keyed connector | Blocked |
| W04 | battery bus | K1 pole -> U3 in+ | MOTION_RAW | 10.0-14.6 V | up to 30 A | 8 AWG | Proposed |
| W05 | U3 out+ | FB1 input stud | MOTION_12V | 12.0 V | 12 A design | 10 AWG, ring terminal | Proposed |
| W06 | FB1 F11 | U30 VIN+ (screw) | WHEEL_12V | 12.0 V | 6 A design, 10.8 A stall | 14 AWG, ferrule | Verified layout (V1) |
| W07 | FB1 F12 | U41 VIN+ (screw) | ARM1_12V | 12.0 V | 3 A design, 8 A peak (estimate) | 14 AWG, ferrule | Proposed |
| W08 | FB1 F13 | U42 VIN+ (screw) | ARM2_12V | 12.0 V | 3 A design, 8 A peak (estimate) | 14 AWG, ferrule | Proposed |
| W09 | U30, U41, U42 VIN-; U3 in-/out- | negative bus bar | POWER_GND | 0 V | as feeds | same gauge as feed, one wire each | Proposed |
| W10 | battery bus | F3 -> U20 DC jack | JETSON_BATT | 10.0-14.6 V | 3.0 A design, 3.8 A peak | 18 AWG, 5.5 x 2.5 mm barrel, centre + | Verified layout (V1) |
| W11 | battery bus | F4 -> U4 in+ | BUCK_IN | 10.0-14.6 V | about 1 A, 7 A max | 14 AWG | Verified layout (V1) |
| W12 | U4 out+ | FB2 input stud | RAIL_5V | 5.0-5.2 V | 2 A | 14 AWG | Verified layout (V1) |
| W13 | FB2 F21 | U50 hub 1 DC in | HUB1_5V | 5 V | TBD | 18 AWG, barrel TBD | Blocked |
| W14 | FB2 F22 | U54 hub 2 DC in | HUB2_5V | 5 V | TBD | 18 AWG, barrel TBD | Blocked |
| W15 | FB2 F23 | J5 auxiliary feed -> U6 5V | AUX_5V | regulated 5 V | U6 about 1 mA; total <= harness/fuse rating | 20 AWG feeder; JST harness rating TBD | Selected module; wiring untested |
| W16 | battery bus | F5 -> S1 latching NC -> K1 coil positive; coil negative -> POWER_GND | coil control | battery voltage; coil envelope TBD | actual coil current TBD | 20 AWG provisional; follow coil polarity markings | Proposed; no START or aux loop |
| W17 | U30 port 1 / port 2 | M31 -> M33 / M32 -> M34 | servo bus | 12 V | <= 2 servos per port | Molex 5264 3-pin | Verified (V1) |
| W18 | U41 port 1, U42 port 1 | M41, M42 arm chains | servo bus | 12 V | arm current | Molex 5264 3-pin | Proposed |
| W19 | U6 G | negative star bus | POWER_GND | 0 V | monitor electronics only | JST harness ground; main current never through JST | Proposed |
| I-1 | U6 SDA | Jetson GPIO/I2C functional interface | I2C_SDA | logic level/pull-ups TBD | signal only | short JST/twisted ground-paired wiring; actual header pin TBD | Blocked pending interface verification |
| I-2 | U6 SCL | Jetson GPIO/I2C functional interface | I2C_SCL | logic level/pull-ups TBD | signal only | actual header pin and Linux bus TBD | Blocked pending interface verification |
| U-1 | U20 USB-A1 / A2 | Gemini 335 / wrist webcam | USB data + bus power | 5 V | 0.9 A / 0.5 A | direct, never via a hub | Verified (V1) |
| U-2 | U20 USB-A3 / A4 | hub 1 / hub 2 upstream | USB data | - | - | USB cable | Verified (V1) / Proposed |
| U-3 | U50 DS1-DS3 | U30, U41, U42 USB-C | USB data (logic power only) | 5 V | small | USB-A to USB-C | Verified (V1) |
| U-4 | U50 DS4 | RPLIDAR C1 adapter | USB data + 5 V | 5 V | 0.23 A typ | shielded USB | Verified (V1) |

J6 on the schematic represents the existing U20 Jetson GPIO/I2C header as a functional endpoint, not an additional
board to buy. Its semantic SDA/SCL/GND ports are not physical header pin numbers. U6 BAT/LOAD/V5/GND functional
ports correspond to the module BAT+/ESC+/5V/G markings respectively; verify the actual connector orientation.

Rev B control behaviour: **S1 released = coil powered; pressed/locked = coil off; twist to release = immediate
motion-power restoration**. There is no timed stop and no restart interlock. Both arms are confirmed new 12 V
servos; their exact MPN, current and fit remain unverified. K1 coil/main-terminal labels in the schematic are
functional, not confirmed physical terminal numbering. Charge inlet stays before SW1 and is not measured by U6.

Rules carried over from V1:

- Bus Servo Adapters are fed through the **screw terminal**, not the barrel jack.
- Fuse box 2 is labelled "5 V ONLY" and is never fed from 12 V.
- Wheel servos stay on two chains (port 1: ID 7 -> 9, port 2: ID 8 -> 10).
- Ferrules on screw terminals, ring terminals on studs, heat-shrink on every exposed terminal.
