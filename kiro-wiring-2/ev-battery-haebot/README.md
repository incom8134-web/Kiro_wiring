# HAEBOT V2-B: 12 V 45 Ah EV battery power system

Battery version of the HAEBOT / KIRO robot that keeps the V1 layout (two fuse boxes and the 12 V to 5 V buck) and
replaces the AC supply with one 12 V 45 Ah battery. Both arms move to 12 V servos.

**Status: Rev A, PROPOSED. The battery chemistry, BMS and charger are not identified yet.**

| | |
|---|---|
| Schematic (KiCad) | [`kicad/HAEBOT_EV.kicad_pro`](kicad/HAEBOT_EV.kicad_pro) |
| Schematic PDF | [`exports/HAEBOT_EV_SCHEMATIC.pdf`](exports/HAEBOT_EV_SCHEMATIC.pdf) |
| Block diagram | [`exports/HAEBOT_EV_BLOCK_DIAGRAM.pdf`](exports/HAEBOT_EV_BLOCK_DIAGRAM.pdf), source [`block-diagrams/`](block-diagrams) |
| Bill of materials | [`bom/`](bom) |
| Power budget and runtime | [`docs/power_budget.md`](docs/power_budget.md) |
| Wiring connection table | [`docs/wiring_connections.md`](docs/wiring_connections.md) |
| Distribution and protection | [`docs/power_distribution_and_protection.md`](docs/power_distribution_and_protection.md) |
| 12 V arm servo notes | [`docs/arm_servo_12v_notes.md`](docs/arm_servo_12v_notes.md) |
| Verification report | [`docs/verification_report.md`](docs/verification_report.md) |
| Assembly instructions | [`docs/assembly_instructions.md`](docs/assembly_instructions.md) |
| Agent instructions | [`AGENTS.md`](AGENTS.md) |

## How it is powered

```text
Battery -> main fuse 40 A -> disconnect -> battery bus
  battery bus -> E-stop contactor -> 12.0 V regulator -> FUSE BOX 1 (12 V): wheels 15 A, arm 1 10 A, arm 2 10 A
  battery bus -> fuse 5 A  -> Jetson (9-20 V jack)
  battery bus -> fuse 10 A -> 12 V to 5 V buck -> FUSE BOX 2 (5 V): hub 1, hub 2, 5 V electronics
  battery bus -> fuse 2 A  -> E-stop button and START -> contactor coil
```

Estimated runtime in typical use: about 3.7 h (lead-acid), 6.3 h (LiFePO4) or 5.4 h (3S Li-ion).

## Main points

1. The servos accept at most 12.6 V. A lead-acid or LiFePO4 battery reaches 14.4 V or more, so the motion rail has a
   12.0 V regulator. Only a 3S Li-ion pack makes it unnecessary.
2. The proposed arm servo is the STS3215-C018 (12 V). It is the model already used on the wheels.
3. The E-stop is hardware only. It cuts wheels and arms and leaves the Jetson running.

## Before building

Send a photo of the battery label and the charger label. Main fuse, contactor, regulator and charging connection
depend on them.

## Editing

Open `kicad/HAEBOT_EV.kicad_pro` in KiCad 7 or newer. Export commands are in `AGENTS.md`.
