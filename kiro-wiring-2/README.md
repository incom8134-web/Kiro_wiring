# HAEBOT / KIRO V2: battery-powered systems

V2 removes the mains cable. There are two independent designs because two different batteries are being considered.
Each folder is complete by itself: KiCad project, PDFs, block diagram, BOM, calculations, verification report,
assembly instructions and its own `AGENTS.md`.

| | [Anker SOLIX design](anker-solix-battery-haebot) | [EV battery design](ev-battery-haebot) |
|---|---|---|
| Source | Anker SOLIX C300 DC (A1726), 288 Wh, 300 W | 12 V 45 Ah battery, chemistry not identified |
| Idea | plug-and-play leads on the station's protected ports | V1 layout with the SMPS replaced by a battery |
| Wheels | USB-C2, 12 V PD trigger (builder measurement), F1 15 A, K1 | fuse box 1 through a 12.0 V regulator |
| Arms | arm 2 on USB-C1 through a 5 V PD trigger and K1 (3 A source); arm 1 on USB-A1, DC jack, not on the E-stop | both arms on new 12 V servos (STS3215-C018) |
| Jetson | same USB-C2, F5 5 A, ahead of K1, so it stays on after E-stop | battery bus, direct |
| E-stop | 2-pole contactor: wheels and arm 2; hardware loop. Jetson, hubs and arm 1 stay on | battery contactor, hardware loop |
| Typical runtime (calculated) | about 4.0 h at 61 W if the ports hold; USB-C2 is already over a usual 3 A / 36 W contract | 3.7 h lead-acid, 6.3 h LiFePO4, 5.4 h 3S Li-ion |
| Status | Rev C, 2026-11-16. AS BUILT per builder report. Not independently measured | Proposed; battery and charger are blocked items |
| Schematic PDF | [HAEBOT_ANKER_SCHEMATIC.pdf](anker-solix-battery-haebot/exports/HAEBOT_ANKER_SCHEMATIC.pdf) | [HAEBOT_EV_SCHEMATIC.pdf](ev-battery-haebot/exports/HAEBOT_EV_SCHEMATIC.pdf) |
| Block diagram PDF | [HAEBOT_ANKER_BLOCK_DIAGRAM.pdf](anker-solix-battery-haebot/exports/HAEBOT_ANKER_BLOCK_DIAGRAM.pdf) | [HAEBOT_EV_BLOCK_DIAGRAM.pdf](ev-battery-haebot/exports/HAEBOT_EV_BLOCK_DIAGRAM.pdf) |

Combined review document: [`exports/HAEBOT_V2_POWER_SYSTEM_COMPARISON.pdf`](exports/HAEBOT_V2_POWER_SYSTEM_COMPARISON.pdf).
That PDF is the 2026-11-13 review. A cover page now says the Anker column is superseded by Rev C in `anker-solix-battery-haebot/`. The original nine pages were not redrawn. The EV pages are unchanged.

## Archive

[`archive/flat-v2-2026-11-12/`](archive/flat-v2-2026-11-12) holds the earlier single-sheet V2 schematic (KiCad 10, with
the `ESTOP_OK` input and the warning beacon) and its design basis. It is the predecessor of the EV battery design and is
kept for reference. It is not maintained.
