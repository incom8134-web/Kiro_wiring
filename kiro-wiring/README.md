# HAEBOT / KIRO V1: AC / SMPS power system (legacy reference)

V1 is the mains-powered system that was built first: one 12 V SMPS, two fuse boxes, one 12 V to 5 V buck converter and
a relay E-stop. It is kept as the **reference design**. New work happens in [`../kiro-wiring-2/`](../kiro-wiring-2).
Its electrical design was not changed by the 2026-11-13 reorganisation; files were only moved.

| | |
|---|---|
| Schematic (KiCad, Rev F) | [`kicad/KIRO_FINAL.kicad_sch`](kicad/KIRO_FINAL.kicad_sch) |
| Schematic PDF (Rev F, 2026-11-02) | [`exports/haebot_wiring_FINAL_revF_2026_11_02.pdf`](exports/haebot_wiring_FINAL_revF_2026_11_02.pdf) |
| Power system design | [`docs/power_system_design.md`](docs/power_system_design.md) |
| Parts list | [`docs/parts_list.md`](docs/parts_list.md) |
| Wiring pictures | [`../images/haebot_wiring_rev3_2026_11_02_eng.png`](../images/haebot_wiring_rev3_2026_11_02_eng.png), [Korean](../images/haebot_wiring_rev3_2026_11_02_kr.png) |
| Older drawings | [`../images/old_versions/`](../images/old_versions) |

## Architecture

| Rail | Voltage | Source | Fuse | Load |
|---|---|---|---|---|
| Jetson | 12 V | SMPS HS-350-12 | F1 5 A (FB1) | Jetson Orin Nano Super, DC jack 9-20 V |
| Wheels | 12 V | SMPS | F2 15 A (FB1) | wheel adapter + 4 x ST3215-C018 |
| Buck input | 12 V | SMPS | F3 15 A (FB1) | TOBSUN EA75-5V |
| Leader arm | 5 V | buck | F4 2 A (FB2) | leader adapter + 6 x STS3215, torque off |
| Follower arm | 5 V | buck | F5 15 A (FB2) | follower adapter + 6 x STS3215 (7.4 V type) |

The measured and specified values in `docs/power_system_design.md` are the hardware evidence that both V2 designs use.

## Editing

The schematic is a single KiCad 10 file without a project file. Open `kicad/KIRO_FINAL.kicad_sch` directly in KiCad 10.
