# AGENTS.md: Anker SOLIX battery HAEBOT

Instructions for coding agents and engineers working in `kiro-wiring-2/anker-solix-battery-haebot/`.
This folder is self-contained. Do not rely on the EV battery folder to understand it.

## Purpose

A portable, plug-and-play power system for the HAEBOT / KIRO robot built on one **Anker SOLIX C300 DC (A1726)**
power station. Status: **Rev B, PROPOSED, not bench-verified.**

## Read first

1. `docs/verification_report.md`: what is verified, calculated, proposed and blocked.
2. `docs/power_distribution_and_protection.md`: port limits and branch assignment.
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
| Car socket | 12 V 10 A |
| Total | 300 W |

There is **no 12 V USB-C profile** and no PPS. With USB-C1, USB-C2, the USB group and the car socket all in use the
manual gives 30 W, 100 W, 20 W and 120 W.

## Power branch assignment (Rev B)

| Branch | Port | Path | Load |
|---|---|---|---|
| A | USB-A1, USB-A2 | USB-A to DC lead | USB hub 1, hub 2 (blocked) |
| B | USB-C4 | USB-C 5 V lead -> F4 3 A -> K1 | arm 1, leader only |
| C | USB-C1 | 20 V PD trigger -> EA75-5V -> F2 15 A -> K1 | arm 2, follower, 5 V |
| D | USB-C2 | 20 V PD trigger -> 12.0 V buck -> F1 15 A -> K1 | wheel adapter, 4 x ST3215-C018 |
| E | Car socket | fused plug lead -> F5 5 A | Jetson DC jack (9-20 V) |
| - | USB-C3 | unused | keep free for recharging |

## Rules

### Power rails

- **No undocumented power-rail change.** A change to a voltage, a source port, a fuse value or a converter must update,
  in the same commit: the schematic, the block diagram, `docs/wiring_connections.md`, `docs/power_budget.md`,
  the BOM and this file.
- Never join the positive of two station ports. Never parallel two ports for more current.
- Follower servos (7.4 V type) must never see more than 8.0 V. Wheel servos must never see more than 12.6 V.
- Do not wire 12 V PD triggers. Do not power a follower arm from a 5 V USB-C source.
- The E-stop must stay a hardware loop that opens K1. Never replace it with a software command.
- K1 has three power poles: wheels, arm 2 and arm 1. The E-stop must always cut all three together.

### Plug-and-play principles

- Prefer ready-made leads and the station's own protected outputs to custom distribution.
- One branch, one lead pair. No shared returns between branches.
- Every connector is labelled with its reference designator and voltage.

### Connectors

- Jetson: 5.5 x 2.5 mm barrel, centre positive.
- Bus Servo Adapter power: screw terminal with ferrules, never the barrel jack.
- Servo bus: Molex 5264 3-pin, GND / VCC / SIG, at most two wheel servos per adapter port.
- USB data cables are data only. They are never the power feed of a servo rail.

### Schematic editing

- Source of truth: `kicad/HAEBOT_ANKER.kicad_pro` and `kicad/HAEBOT_ANKER.kicad_sch`. Edit them in KiCad (Konnect MCP
  or the GUI). The file is in KiCad 7 format; KiCad 8 or newer converts it on save.
- Do not invent pins or part numbers. Off-the-shelf products stay functional blocks.
- Keep the status words (EXISTING, PROPOSED, BLOCKED) on the drawing in step with `docs/verification_report.md`.
- Bump the revision letter and date in the title block for any electrical change.
- Run ERC and investigate every message. Do not suppress a real ERC error to get a clean result.

### Exports

```bash
kicad-cli sch export pdf --no-background-color kicad/HAEBOT_ANKER.kicad_sch -o exports/HAEBOT_ANKER_SCHEMATIC.pdf
kicad-cli sch export netlist kicad/HAEBOT_ANKER.kicad_sch -o exports/HAEBOT_ANKER_NETLIST.net
rsvg-convert -f pdf -o exports/HAEBOT_ANKER_BLOCK_DIAGRAM.pdf block-diagrams/HAEBOT_ANKER_BLOCK_DIAGRAM.svg
rsvg-convert -f pdf -o exports/HAEBOT_ANKER_BLOCK_DIAGRAM_KO.pdf block-diagrams/HAEBOT_ANKER_BLOCK_DIAGRAM_KO.svg
```

The block diagram exists in English and Korean. Change both SVG files together. The Korean file needs the
Noto Sans CJK KR font installed.

Open each PDF after export and check that nothing is clipped or overlapping. A3 landscape for the schematic,
A4 landscape for the block diagram.

### Verification procedure

1. Export the netlist and compare it with `docs/wiring_connections.md`.
2. Re-run the numbers in `docs/power_budget.md` for any load or port change.
3. Update `docs/verification_report.md`. Never mark an item Verified without a datasheet, manual or measurement.

## Open items (TODO)

- [ ] Hub 1 input voltage, current, barrel size and polarity (label photo).
- [ ] Is a second hub really fitted? Model and input.
- [ ] Which physical arm is "arm 1" and which is "arm 2" (leader / follower).
- [ ] Select PD triggers, the 12 V buck, K1, S1, START and the leads. Record part numbers in the BOM.
- [ ] Bench test: 20 V on USB-C1 when capped at 30 W; behaviour when a port is plugged in while armed.
- [ ] Continuity between the station's port negatives.
- [ ] Decide on the recommended alternative (arm buck on the car socket).
- [ ] Run KiCad ERC in KiCad 8 or newer and record the result.
