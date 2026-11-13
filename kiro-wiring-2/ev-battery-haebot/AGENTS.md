# AGENTS.md: EV battery HAEBOT

Instructions for coding agents and engineers working in `kiro-wiring-2/ev-battery-haebot/`.
This folder is self-contained. Do not rely on the Anker folder to understand it.

## Purpose

Successor of the V1 AC/SMPS system. The SMPS is replaced by one **12 V 45 Ah battery** with battery-grade protection.
Status: **Rev A, PROPOSED.** The battery chemistry, its BMS and the charger are not identified.

## Read first

1. `docs/verification_report.md`
2. `docs/power_distribution_and_protection.md`
3. `docs/arm_servo_12v_notes.md`
4. Repository hardware evidence: `../../docs/hardware_evidence.md` and the V1 records in `../../kiro-wiring/docs/`.

You must review that evidence before changing any electrical connection.

## Design constraints

- Design for the full battery voltage range, not for 12.0 V. Until the chemistry is known the envelope is 10.0-14.6 V.
- Servo rail: 12.0 V regulated, never above 12.6 V. U3 may be removed only for a 3S Li-ion pack.
- Both arms use 12 V servos (STS3215-C018, proposed). The existing 7.4 V servos (limit 8.0 V) must never be connected
  to fuse box 1.
- Jetson: 9-20 V DC jack, on its own fused branch from the battery bus. Never on the 5 V rail.

## Two fuse boxes

| Box | Fed from | Slots |
|---|---|---|
| FB1, 12 V motion | K1 -> U3 | F11 15 A wheels, F12 10 A arm 1, F13 10 A arm 2, spare |
| FB2, 5 V only | EA75-5V buck | F21 3 A hub 1, F22 3 A hub 2, F23 2 A 5 V electronics, spare |

FB1 is after the E-stop contactor. FB2 is never fed from 12 V. Both boxes have one live input and no negative bus.

## Buck converter

TOBSUN EA75-5V, 8-40 V in, 5 V 15 A. It may be reused because its input range covers the battery envelope. Measure
5.0-5.2 V before connecting loads. Feed it through F4 from the unswitched battery bus.

## Battery protection, fuses and wire

Procedure for any change:

1. Take the branch design-continuous and peak current from `docs/power_budget.md`.
2. Choose the wire for the peak current and the run length. Check the voltage drop.
3. Choose the fuse above the design-continuous current and below the wire and connector rating.
4. The main fuse sits within 150 mm of the battery positive. Its interrupt rating must exceed the battery fault current.
5. Record the value and its basis in `docs/power_distribution_and_protection.md` and the BOM.

Every return is its own wire to the star point at the battery negative. No return through USB.

## Charging

- Charger and charge voltage must match the chemistry. Charge with SW1 open.
- The charge inlet is fused (F2) and keyed differently from the load connectors.

## Emergency stop and disconnect

- SW1 isolates the battery. K1 removes power from wheels and both arms.
- The E-stop is a self-holding hardware loop. Never route it through software or the Jetson.
- The Jetson, hubs and the 5 V rail stay on after an E-stop. No automatic restart.

## KiCad editing

- Source of truth: `kicad/HAEBOT_EV.kicad_pro` and `kicad/HAEBOT_EV.kicad_sch`. Edit in KiCad (Konnect MCP or GUI).
  KiCad 7 format; KiCad 8 or newer converts on save.
- Do not invent pins or part numbers. Off-the-shelf products stay functional blocks.
- Keep the status words on the drawing in step with `docs/verification_report.md`.
- Bump the revision and date for any electrical change.
- Run ERC and investigate every message. Do not suppress a real ERC error.
- No undocumented power-rail change: schematic, block diagram, wiring table, power budget, BOM and this file change
  in the same commit.

## Exports

```bash
kicad-cli sch export pdf --no-background-color kicad/HAEBOT_EV.kicad_sch -o exports/HAEBOT_EV_SCHEMATIC.pdf
kicad-cli sch export netlist kicad/HAEBOT_EV.kicad_sch -o exports/HAEBOT_EV_NETLIST.net
rsvg-convert -f pdf -o exports/HAEBOT_EV_BLOCK_DIAGRAM.pdf block-diagrams/HAEBOT_EV_BLOCK_DIAGRAM.svg
```

Open each PDF after export and check that nothing is clipped or overlapping.

## Verification procedure

1. Export the netlist and compare it with `docs/wiring_connections.md`.
2. Re-run `docs/power_budget.md` for any load change.
3. Update `docs/verification_report.md`. Never mark an item Verified without a datasheet or a measurement.

## Unresolved design items

- [ ] Battery label: chemistry, nominal / maximum / minimum voltage, BMS continuous and peak current, connector.
- [ ] Charger label and charging connector.
- [ ] Final F1 value and type; SW1, K1 and U3 part numbers.
- [ ] Low-voltage disconnect behaviour.
- [ ] Which two arms get 12 V servos; trial fit of one STS3215-C018 in an arm joint; measured arm current.
- [ ] Hub 1 input voltage and plug; whether hub 2 exists.
- [ ] What the "5 V control electronics" are.
- [ ] Optional: `ESTOP_OK` input to the Jetson and the warning beacon from the archived draft.
- [ ] Run KiCad ERC in KiCad 8 or newer and record the result.
