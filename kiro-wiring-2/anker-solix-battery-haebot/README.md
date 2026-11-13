# HAEBOT V2-A: Anker SOLIX C300 DC power system

Battery version of the HAEBOT / KIRO robot that runs from one **Anker SOLIX C300 DC (A1726)** portable power station
with ready-made leads and a minimum of extra modules.

**Status: Rev A, PROPOSED. Not built, not bench-verified.**

| | |
|---|---|
| Schematic (KiCad) | [`kicad/HAEBOT_ANKER.kicad_pro`](kicad/HAEBOT_ANKER.kicad_pro) |
| Schematic PDF | [`exports/HAEBOT_ANKER_SCHEMATIC.pdf`](exports/HAEBOT_ANKER_SCHEMATIC.pdf) |
| Block diagram | [`exports/HAEBOT_ANKER_BLOCK_DIAGRAM.pdf`](exports/HAEBOT_ANKER_BLOCK_DIAGRAM.pdf), source [`block-diagrams/`](block-diagrams) |
| Bill of materials | [`bom/`](bom) |
| Power budget and runtime | [`docs/power_budget.md`](docs/power_budget.md) |
| Wiring connection table | [`docs/wiring_connections.md`](docs/wiring_connections.md) |
| Distribution and protection | [`docs/power_distribution_and_protection.md`](docs/power_distribution_and_protection.md) |
| Verification report | [`docs/verification_report.md`](docs/verification_report.md) |
| Assembly instructions | [`docs/assembly_instructions.md`](docs/assembly_instructions.md) |
| Agent instructions | [`AGENTS.md`](AGENTS.md) |

## How it is powered

| Branch | Station port | Path | Load |
|---|---|---|---|
| A | USB-A1, USB-A2 (5 V 2.4 A) | USB-A to DC lead | USB hub 1 and hub 2 |
| B | USB-C4 (5 V 3 A) | USB-C 5 V lead, fuse 3 A | Arm 1 (leader) |
| C | USB-C1 (20 V PD) | PD trigger, 5 V 15 A buck, fuse 15 A, E-stop | Arm 2 (follower) |
| D | USB-C2 (20 V PD) | PD trigger, 12.0 V buck, fuse 15 A, E-stop | Wheel driver and four mecanum servos |
| E | Car socket (12 V 10 A) | fused plug lead, fuse 5 A | Jetson Orin Nano Super |

Estimated runtime: about 3.9 h in typical use, about 1.6 h with every branch at its design load.

## Three things differ from the original request

1. The wheels use a **20 V** PD trigger and a 12 V buck. The station has no 12 V USB-C output.
2. The follower arm uses a **20 V** PD trigger and the existing 5 V 15 A buck. USB-C gives only 3 A at 5 V.
3. The Jetson runs straight from the car socket. Its DC jack accepts 9-20 V, so no boost converter is fitted.

## Before building

Hub power is blocked until the hub's input voltage is read from its label. The remaining open items and the bench
checks are in the verification report.

## Editing

Open `kicad/HAEBOT_ANKER.kicad_pro` in KiCad 7 or newer. Export commands are in `AGENTS.md`.
