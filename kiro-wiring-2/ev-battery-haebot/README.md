# HAEBOT V2-B: 12 V 45 Ah EV battery power system

**Rev B - 2026-11-26. PROPOSED wiring; not hardware-validated.** This revision follows the user's choice:
both new arms use 12 V servos, one mechanically latching NC E-stop controls the DC contactor, and one
Matek I2C-INA-BM measures battery discharge. There is no START/RESET button, auxiliary holding loop or safety controller.

| File | Purpose |
|---|---|
| [KiCad project](kicad/HAEBOT_EV.kicad_pro) | Editable circuit source |
| [Schematic PDF](exports/HAEBOT_EV_SCHEMATIC.pdf) | Export of the circuit |
| [English block diagram](exports/HAEBOT_EV_BLOCK_DIAGRAM.pdf) | Printable power and control overview |
| [한국어 블록도](exports/HAEBOT_EV_BLOCK_DIAGRAM_KO.pdf) | 한국어 전원 및 제어 구성도 |
| [English SVG](block-diagrams/HAEBOT_EV_BLOCK_DIAGRAM.svg), [한국어 SVG](block-diagrams/HAEBOT_EV_BLOCK_DIAGRAM_KO.svg) | Editable vector diagrams |
| [Parts list](bom/README.md) | Components and selection status |
| [Wiring connections](docs/wiring_connections.md) | Power, control, USB and I2C wiring |
| [Protection plan](docs/power_distribution_and_protection.md) | Fuses, voltage limits and monitoring |
| [Power budget](docs/power_budget.md) | Preliminary load and runtime estimates |
| [12 V arm notes](docs/arm_servo_12v_notes.md) | Confirmed voltage choice and remaining checks |
| [Assembly](docs/assembly_instructions.md) | Installation and operation |
| [Verification](docs/verification_report.md) | Actual checks and unresolved hardware inputs |

## Power path

```text
BT1 battery + -> F1 main fuse -> SW1 disconnect -> U6 Matek BAT+ -> ESC+ -> battery bus
  bus -> K1 main contact -> U3 regulated 12.0 V -> FB1: F11 wheels, F12 arm 1, F13 arm 2
  bus -> F3 5 A -> Jetson DC jack (stays powered after E-stop)
  bus -> F4 10 A -> EA75-5V -> FB2: F21 hub 1, F22 hub 2, F23 monitor + auxiliary feed
  bus -> F5 control fuse -> S1 latching NC E-stop -> K1 coil -> POWER_GND
FB2 F23 / J5 AUX_5V -> U6 5V; U6 G -> POWER_GND
U6 SDA / SCL -> Jetson I2C interface (header pins, bus, pull-ups and software TBD)
```

All returns have their own wire to the battery-negative star bus. U6 high-current pads carry the main positive
current; its small JST connector carries electronics power and I2C only. The charge inlet remains on the battery
side of SW1, so this placement measures discharge, not charging with SW1 open.

## One E-stop: how it holds and releases

S1 is a **positive-opening NC, push-to-lock / twist-to-release mushroom**. When released, it powers the K1 coil.
Pressing it opens the coil circuit, and K1 disconnects the wheels and both arms. The mushroom stays down mechanically
until twisted; no electrical holding contact is needed. The Jetson, hubs and monitor electronics remain powered.

**Twisting S1 to release restores motor power immediately. SW1 on with S1 released also enables motor power.
There is no restart interlock.** Motor commands must be cleared before restoring power. Power removal also removes arm
holding torque; support the arms during testing. This is a single-contactor prototype power cut, not a validated
functional-safety system; a welded K1 contact can defeat the cut-off.

## Hardware facts still needed

- Battery chemistry, full voltage range, BMS limits and matching charger.
- K1 is the user's photographed unit labelled **500A DC12V**. Manufacturer/model, continuous coil duty, actual coil
  current, polarity, DC breaking capacity and suppression remain unverified. The label alone does not verify 500 A
  continuous or breaking capability. F5 2 A and the former 6 W coil allowance are preliminary.
- U3 is retained: new 12 V servos do not imply tolerance of a 14.6 V battery. Bypass only after voltage compatibility
  is established. Exact new servo model, fit and current remain unverified; STS3215-C018 is the existing candidate.
- Matek electronics use regulated 5 V (manufacturer input 4-9 V), never raw battery. The manufacturer lists INA228/INA238
  variants; identify the fitted IC before selecting Jetson software. Default address is decimal 69 / hex 0x45.
- Hub voltage/plug and whether hub 2 is fitted remain unresolved.

## Regenerating outputs

Rev B is saved in **KiCad 10** format; use KiCad 10 or newer. Final ERC: **0 errors, 0 warnings**. Saved-source
connection checks are in [verification](docs/verification_report.md); hardware operation is still untested.
The block diagram generator is
`tools/render_block_diagrams.py`; it emits both SVGs and PDFs from one geometry with English/Korean labels.
Run it with Python + ReportLab; Windows Malgun Gothic fonts are used for embedded Korean text.

Manufacturer reference: https://www.mateksys.com/?portfolio=i2c-ina-bm
