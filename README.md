# Kiro Wiring (HAEBOT / KIRO)

**English** | [한국어](README.ko.md)

Power system and electronics packaging for **HAEBOT**, also called **KIRO**: one robot, two names. It is a mobile
dual-arm robot with a Jetson Orin Nano, SO-101 arms and a mecanum base.

<p align="center">
  <img src="images/hero.png" alt="Kiro power plate" width="820">
</p>

## Versions

| Version | Folder | Power source | Status |
|---|---|---|---|
| **V1** | [`kiro-wiring/`](kiro-wiring) | AC mains, 12 V SMPS | Built. Legacy reference |
| **V2-A** | [`kiro-wiring-2/anker-solix-battery-haebot/`](kiro-wiring-2/anker-solix-battery-haebot) | Anker SOLIX C300 DC power station | Proposed, not bench-verified |
| **V2-B** | [`kiro-wiring-2/ev-battery-haebot/`](kiro-wiring-2/ev-battery-haebot) | 12 V 45 Ah battery | Proposed; battery and charger not identified |

There are two V2 designs because two batteries are under consideration. V2-A is the quick, plug-and-play option built
on a ready-made power station. V2-B is the long-runtime option that keeps the V1 fuse-box layout and moves the arms to
12 V servos.

## Where things are

| Need | V1 | V2-A Anker | V2-B EV battery |
|---|---|---|---|
| KiCad schematic | [`KIRO_FINAL.kicad_sch`](kiro-wiring/kicad/KIRO_FINAL.kicad_sch) | [`HAEBOT_ANKER.kicad_pro`](kiro-wiring-2/anker-solix-battery-haebot/kicad/HAEBOT_ANKER.kicad_pro) | [`HAEBOT_EV.kicad_pro`](kiro-wiring-2/ev-battery-haebot/kicad/HAEBOT_EV.kicad_pro) |
| Schematic PDF | [Rev F](kiro-wiring/exports/haebot_wiring_FINAL_revF_2026_11_02.pdf) | [Rev A](kiro-wiring-2/anker-solix-battery-haebot/exports/HAEBOT_ANKER_SCHEMATIC.pdf) | [Rev A](kiro-wiring-2/ev-battery-haebot/exports/HAEBOT_EV_SCHEMATIC.pdf) |
| Block diagram PDF | - | [PDF](kiro-wiring-2/anker-solix-battery-haebot/exports/HAEBOT_ANKER_BLOCK_DIAGRAM.pdf) | [PDF](kiro-wiring-2/ev-battery-haebot/exports/HAEBOT_EV_BLOCK_DIAGRAM.pdf) |
| BOM | [parts list](kiro-wiring/docs/parts_list.md) | [`bom/`](kiro-wiring-2/anker-solix-battery-haebot/bom) | [`bom/`](kiro-wiring-2/ev-battery-haebot/bom) |
| Design notes | [`docs/`](kiro-wiring/docs) | [`docs/`](kiro-wiring-2/anker-solix-battery-haebot/docs) | [`docs/`](kiro-wiring-2/ev-battery-haebot/docs) |

- V2 side-by-side review: [`HAEBOT_V2_POWER_SYSTEM_COMPARISON.pdf`](kiro-wiring-2/exports/HAEBOT_V2_POWER_SYSTEM_COMPARISON.pdf)
- Shared hardware facts and their sources: [`docs/hardware_evidence.md`](docs/hardware_evidence.md)
- Shared pictures: [`images/`](images). Shared 3D models and print files: [`3d_models/`](3d_models)

## What is verified

| | V1 | V2-A Anker | V2-B EV battery |
|---|---|---|---|
| Built and running | yes | no | no |
| Source ratings | SMPS on hand | verified from the Anker manual | **blocked**: battery not identified |
| Loads | measured | taken from V1 | taken from V1; 12 V arm servos are proposed |
| Schematic connectivity | - | checked by KiCad netlist | checked by KiCad netlist |
| KiCad ERC | - | not run yet | not run yet |
| Open items | - | hub power, PD parts, bench tests | battery, charger, main fuse, regulator, arm servos |

Each V2 folder has a `docs/verification_report.md` that separates verified, calculated, proposed and blocked items.

## Editing and exporting

1. Install KiCad. V2 projects open in KiCad 7 or newer. V1 and the archived V2 draft need KiCad 10.
2. Open the `.kicad_pro` file of the design (V1: open the `.kicad_sch` file).
3. After a change, export again from the design folder:

```bash
kicad-cli sch export pdf --no-background-color kicad/HAEBOT_ANKER.kicad_sch -o exports/HAEBOT_ANKER_SCHEMATIC.pdf
rsvg-convert -f pdf -o exports/HAEBOT_ANKER_BLOCK_DIAGRAM.pdf block-diagrams/HAEBOT_ANKER_BLOCK_DIAGRAM.svg
```

The block diagrams are plain SVG files and can be edited in Inkscape or a text editor. Rules for changing a design
are in each folder's `AGENTS.md`.
