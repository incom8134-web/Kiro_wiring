# HAEBOT / KIRO V2: battery-powered systems

V2 removes the mains cable. There are two independent designs because two different batteries are being considered.
Each folder is complete by itself: KiCad project, PDFs, block diagram, BOM, calculations, verification report,
assembly instructions and its own `AGENTS.md`.

| | [Anker SOLIX design](anker-solix-battery-haebot) | [EV battery design](ev-battery-haebot) |
|---|---|---|
| Source | Anker SOLIX C300 DC (A1726), 288 Wh, 300 W | 12 V 45 Ah battery, chemistry not identified |
| Idea | plug-and-play leads on the station's protected ports | V1 layout with the SMPS replaced by a battery |
| Wheels | USB-C2, 20 V PD, 12.0 V buck | fuse box 1 through a 12.0 V regulator |
| Arms | existing 5 V servos; leader on USB-C4, follower on USB-C1 through a 5 V buck | both arms on new 12 V servos (STS3215-C018) |
| Jetson | car socket, direct | battery bus, direct |
| E-stop | 2-pole contactor, hardware loop | battery contactor, hardware loop |
| Typical runtime (calculated) | about 3.9 h | 3.7 h lead-acid, 6.3 h LiFePO4, 5.4 h 3S Li-ion |
| Status | Proposed, not bench-verified | Proposed; battery and charger are blocked items |
| Schematic PDF | [HAEBOT_ANKER_SCHEMATIC.pdf](anker-solix-battery-haebot/exports/HAEBOT_ANKER_SCHEMATIC.pdf) | [HAEBOT_EV_SCHEMATIC.pdf](ev-battery-haebot/exports/HAEBOT_EV_SCHEMATIC.pdf) |
| Block diagram PDF | [HAEBOT_ANKER_BLOCK_DIAGRAM.pdf](anker-solix-battery-haebot/exports/HAEBOT_ANKER_BLOCK_DIAGRAM.pdf) | [HAEBOT_EV_BLOCK_DIAGRAM.pdf](ev-battery-haebot/exports/HAEBOT_EV_BLOCK_DIAGRAM.pdf) |

Combined review document: [`exports/HAEBOT_V2_POWER_SYSTEM_COMPARISON.pdf`](exports/HAEBOT_V2_POWER_SYSTEM_COMPARISON.pdf)

## Archive

[`archive/flat-v2-2026-11-12/`](archive/flat-v2-2026-11-12) holds the earlier single-sheet V2 schematic (KiCad 10, with
the `ESTOP_OK` input and the warning beacon) and its design basis. It is the predecessor of the EV battery design and is
kept for reference. It is not maintained.
