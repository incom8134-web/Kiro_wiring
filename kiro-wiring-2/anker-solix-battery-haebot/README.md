# HAEBOT V2-A: Anker SOLIX C300 DC power system

[English](README.md) | [한국어](README.ko.md)

Battery version of the HAEBOT / KIRO robot that runs from one **Anker SOLIX C300 DC (A1726)** portable power station.
This revision records the wiring the builder fitted.

**Status: Rev C, 2026-11-16. AS BUILT per builder report. Not independently measured.**

| | |
|---|---|
| Schematic (KiCad) | [`kicad/HAEBOT_ANKER.kicad_pro`](kicad/HAEBOT_ANKER.kicad_pro) |
| Schematic PDF | [`exports/HAEBOT_ANKER_SCHEMATIC.pdf`](exports/HAEBOT_ANKER_SCHEMATIC.pdf) |
| Block diagram | [`exports/HAEBOT_ANKER_BLOCK_DIAGRAM.pdf`](exports/HAEBOT_ANKER_BLOCK_DIAGRAM.pdf), [Korean](exports/HAEBOT_ANKER_BLOCK_DIAGRAM_KO.pdf), source [`block-diagrams/`](block-diagrams) |
| Bill of materials | [`bom/README.md`](bom/README.md) |
| Power budget and runtime | [`docs/power_budget.md`](docs/power_budget.md) |
| Wiring connection table | [`docs/wiring_connections.md`](docs/wiring_connections.md) |
| Distribution and protection | [`docs/power_distribution_and_protection.md`](docs/power_distribution_and_protection.md) |
| Verification report | [`docs/verification_report.md`](docs/verification_report.md) |
| Assembly and power-up | [`docs/assembly_instructions.md`](docs/assembly_instructions.md) |
| Agent instructions | [`AGENTS.md`](AGENTS.md) |

## How it is wired

| Branch | Station port | Path | Load |
|---|---|---|---|
| D + E | USB-C2 | USB-C cable, PD trigger set to 12 V (builder measurement), Dorhea 4-way fuse box | Wheels through F1 15 A and K1; Jetson through F5 5 A, before K1 |
| C | USB-C1 | 5 V PD trigger, K1 pole | Arm 2 (follower), 6 x STS3215 on 5 V. Source is 3 A max |
| B | USB-A1 (5 V 2.4 A) | USB-A to DC jack lead, no fuse | Arm 1 (leader), straight into the adapter DC jack. Not switched by the E-stop |
| A | USB-A2 (5 V 2.4 A) | USB-A to DC lead | One 7-port USB 3 hub, 5 V input, load under 2 A. **RECOMMENDED**, not confirmed as fitted |
| - | none | do not fit | USB hub 2. **RECOMMENDED**: leave it off. USB-C3 stays free for recharging |
| - | USB-C3, USB-C4, car socket | not connected | Left unused. USB-C3 stays free for recharging |

The E-stop is fitted: `DRIVE_12V -> fuse -> E-stop (NC) -> START || K1 aux -> K1 coil`. One button cuts the wheels and arm 2. The Jetson, the hubs and arm 1 stay on.

Calculated runtime, if the ports hold: about 4.0 h at a typical 61 W. Typical driving already asks USB-C2 for about 3.5 A, and a 12 V USB-C contract is usually 3 A (36 W), so expect the 12 V rail to sag. See the power budget.

## What changed from Rev B

Rev B was a proposal. Rev C is the builder's wiring.

1. The car socket, the car-plug lead, the 12 V buck and the EA75-5V arm buck are not fitted.
2. Wheels and the Jetson share USB-C2 at 12 V. The builder measured 12 V. The Anker A1726 manual lists no 12 V USB-C profile, so that voltage is a builder measurement, not a manual rating.
3. K1 has two power poles, not three. Arm 1 is not on the E-stop.
4. Arm 2 is fed by a 5 V PD trigger. The port gives 3 A. The follower design load is 5 A and the burst is 8 A.

## Still blocked

The hub spec and the 1 A coil fuse are recommendations. The builder had no hub label and does not know the fuse rating. The current USB-C2 can actually hold at 12 V was not measured. Details are in the verification report.

## Editing

Open `kicad/HAEBOT_ANKER.kicad_pro` in KiCad 7 or newer. Export commands are in `AGENTS.md`.
The block-diagram PDFs in `exports/` are rendered from the SVG sources. The hub row is the recommendation above.
