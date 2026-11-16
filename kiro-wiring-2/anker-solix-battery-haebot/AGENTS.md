# AGENTS.md: Anker SOLIX battery HAEBOT

Instructions for coding agents and engineers working in `kiro-wiring-2/anker-solix-battery-haebot/`.
This folder is self-contained. Do not rely on the EV battery folder to understand it, and do not edit the EV design to match this one.

## Purpose

A portable power system for the HAEBOT / KIRO robot built on one **Anker SOLIX C300 DC (A1726)** power station.
Status: **Rev C, 2026-11-16. AS BUILT per builder report. Not independently measured.**

The drawing records the wiring the builder fitted. It is not a proposal, and it is not a licence to "correct" the robot back to Rev B.

## Read first

1. `docs/verification_report.md` (Korean: `docs/verification_report.ko.md`): what is verified, calculated, as-built and blocked.
2. `docs/power_distribution_and_protection.md`: port limits and the as-built branch assignment.
3. Repository hardware evidence: `../../docs/hardware_evidence.md` and the V1 records in `../../kiro-wiring/docs/`.

You must review that evidence before changing any electrical connection.

## Verified port limits (Anker A1726 manual)

| Port | Limit |
|---|---|
| USB-C1 | 5/9/15 V 3 A, 20 V 5 A, 100 W |
| USB-C2, USB-C3 | as C1 plus 28 V 5 A, 140 W; also the recharge inputs |
| USB-C4 | 5 V 3 A |
| USB-A1, USB-A2 | 5 V 2.4 A each |
| USB-A1 + USB-A2 + USB-C4 | 20 W together |
| Car socket | 12 V 10 A. Not used on this robot |
| Total | 300 W |

There is **no 12 V USB-C profile** and no PPS. The builder measured 12 V on the USB-C2 trigger anyway. Record that as a builder measurement. Do not relabel it as a manual rating, and do not delete the sag warning.

## Power branch assignment (Rev C, as built)

| Branch | Port | Path | Load |
|---|---|---|---|
| D + E | USB-C2 | 12 V PD trigger (builder measurement) -> Dorhea 4-way box | F1 15 A -> K1 pole 1 -> 4 x ST3215-C018. F5 5 A, before K1 -> Jetson |
| C | USB-C1 | 5 V PD trigger -> K1 pole 2 | arm 2, follower, 6 x STS3215 on 5 V. Source is 3 A; design is 5 A; burst is 8 A |
| B | USB-A1 | USB-A to DC jack lead, no fuse, not on K1 | arm 1, leader, into the adapter DC jack |
| A | USB-A2 | USB-A to DC lead | one 7-port 5 V USB 3 hub. RECOMMENDED, load under 2 A |
| - | none | do not fit hub 2 | spare ports are on hub 1. USB-C3 stays free for recharge |
| - | USB-C3, USB-C4, car socket | not connected | USB-C3 stays free for recharging |

## Rules

### Power rails

- **No undocumented power-rail change.** A change to a voltage, a source port, a fuse value or a converter must update, in the same commit: the schematic, both block diagrams, `docs/wiring_connections.md`, `docs/power_budget.md`, the BOM and this file. Update the Korean counterparts in the same commit.
- Never join the positive of two station ports. Never parallel two ports for more current.
- Follower servos (7.4 V type) must never see more than 8.0 V. Wheel servos must never see more than 12.6 V.
- The 12 V PD trigger and the 5 V arm feed are as-built. Do not remove them, and do not put the 12 V buck or the EA75-5V back, unless a later revision explicitly asks for that hardware change. Keep the warnings: USB-C2 is over a usual 3 A / 36 W contract (about 3.5 A typical, 9.3 A design with the coil), and arm 2 is over the 3 A port at its design load.
- The E-stop must stay a hardware loop that opens K1. Never replace it with a software command.
- K1 has two power poles: wheels and arm 2. One button cuts those two. The Jetson, the hubs and arm 1 stay on. Do not add a third pole unless a later revision asks for it. Arm 1 staying live through an E-stop is a warning that must stay on the drawing.
- Arm 1 uses the adapter DC jack, as built. The wheel adapter and the arm 2 adapter stay on their screw terminals.
- Do not draw a bulk capacitor, a car-plug lead, or a hub 2 power lead that the builder did not report.

### Status words

- **AS BUILT** means the builder reported it. It does not mean this repository measured it.
- **RECOMMENDED** is a value or part chosen here because the builder did not have the fact. F3 is 1 A for that reason. The hub spec is RECOMMENDED, not AS BUILT.
- **BLOCKED** means a hardware fact is still missing. Do not put the hubs back to BLOCKED; the recommendation above is the decision. USB-C2 current at 12 V is still unmeasured.
- **Verified** needs a datasheet, a manual, or a measurement already in this repository.
- Do not invent part numbers for the PD triggers, K1, S1, START or the leads.

### Connectors

- Jetson: 5.5 x 2.5 mm barrel, centre positive. Fed from F5, ahead of K1.
- Wheel and arm 2 Bus Servo Adapter power: screw terminal with ferrules.
- Arm 1 Bus Servo Adapter power: the DC jack, as built.
- Servo bus: Molex 5264 3-pin, GND / VCC / SIG, at most two wheel servos per adapter port.
- USB data cables are data only. They are never the power feed of a servo rail.

### Schematic editing

- Source of truth: `kicad/HAEBOT_ANKER.kicad_pro` and `kicad/HAEBOT_ANKER.kicad_sch`. Edit them in KiCad. The file is in KiCad 7 format; KiCad 8 or newer converts it on save.
- Do not invent pins. Off-the-shelf products stay functional blocks.
- Keep the status words on the drawing in step with `docs/verification_report.md`.
- Bump the revision letter and date in the title block for any electrical change.
- ERC was run in KiCad 10.0 on 2026-11-16: 0 errors, 58 warnings, all `lib_symbol_issues`, `endpoint_off_grid`, or `unconnected_wire_endpoint`. The project `sym-lib-table` now points at `kiro-wiring-2/shared/HAEBOT.kicad_sym`, and the dangling wire ends were tied to pins and snapped to the 1.27 mm grid. kicad-cli 7.0.11 can export a PDF and a netlist but has no ERC command, so re-count the warnings in KiCad 10 after further edits. A clean PDF export is not an ERC pass.

### Exports

```bash
kicad-cli sch export pdf --no-background-color kicad/HAEBOT_ANKER.kicad_sch -o exports/HAEBOT_ANKER_SCHEMATIC.pdf
kicad-cli sch export netlist kicad/HAEBOT_ANKER.kicad_sch -o exports/HAEBOT_ANKER_NETLIST.net
```

`exports/HAEBOT_ANKER_BLOCK_DIAGRAM.pdf` and `exports/HAEBOT_ANKER_BLOCK_DIAGRAM_KO.pdf` are rendered from the SVG files in `block-diagrams/`. Change both SVG files together, render both PDFs, and check them by eye. The Korean SVG needs a CJK font (WenQuanYi Micro Hei or Noto Sans CJK KR) to render.

Open each PDF after export and check that nothing is clipped or overlapping. A3 landscape for the schematic, A4 landscape for the block diagram.

### Verification procedure

1. Export the netlist and compare it with `docs/wiring_connections.md`.
2. Re-run the numbers in `docs/power_budget.md` for any load or port change.
3. Update `docs/verification_report.md` and `docs/verification_report.ko.md`. Never mark an item Verified without a datasheet, manual or measurement.

## Open items (TODO)

- [ ] Fit the recommended 7-port 5 V hub and confirm barrel polarity. Do not fit hub 2.
- [ ] Measure the current USB-C2 holds at the builder's 12 V, with wheels and Jetson on.
- [ ] Fit F3 as the recommended 1 A fast blade in a spare Dorhea slot. Confirm D1 (1N4007, cathode to A1) is fitted.
- [ ] Record part numbers for the PD triggers, K1, S1, START and the leads. Do not invent them.
- [ ] Confirm the Jetson carrier is the stock developer kit (P3768).
- [ ] Continuity between the station's port negatives, station off.
- [ ] Re-run KiCad 10 ERC and confirm the 58 warnings from 2026-11-16 are gone.
