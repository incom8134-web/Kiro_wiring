# Kiro Wiring

**English** | [한국어](README.ko.md)

Power system and electronics packaging for the **Kiro / SO-101 mobile dual-arm robot**: an XLeRobot-style mobile manipulator built around an NVIDIA Jetson Orin Nano, with two SO-101 leader arms, two SO-101 follower arms and a mecanum-wheel base.

The goal of this repository is to replace the pile of wall adapters and loose cables on the robot cart with a **single SMPS, fused 12 V / 5 V distribution and a buck converter**, mounted on 3D-printed hardware so the robot looks and behaves like a consumer-grade product instead of an R&D prototype.

<p align="center">
  <img src="blender/renders/hero.png" alt="Kiro power plate – Blender render" width="820">
</p>

---

## Where to find things

```
kiro_wiring/
├── blender/                    Detailed Blender scene of the power plate
│   ├── KIRO_power_plate.blend      current scene (v3 layout, all parts and wires)
│   ├── renders/                    hero, top, close, side, ac, hub renders
│   ├── update_blend_v3.py          script that rebuilt the scene from the v2 file
│   └── archive/                    previous scene versions
├── cad/                        Parametric CAD (CadQuery)
│   ├── base_plate/                 lower-tray base plate
│   │   ├── step/                       STEP for Fusion 360 (full, left, right)
│   │   ├── print_3mf/                  print-ready 3MF for the Bambu Lab P1S
│   │   ├── images/                     preview renders
│   │   └── power_plate.py              source – all sizes at the top
│   ├── usb_hub_tray/               middle-floor USB hub tray (step/, print_3mf/, hub_tray.py)
│   └── assembly/                   combined STEP + OBJ of both parts, renders
├── electrical/
│   ├── schematic/                  KIRO_FINAL.kicad_sch (KiCad)
│   └── wiring_diagram/             wiring diagram PNG + SVG, generator, reference concept image
└── docs/
    ├── design_and_printing_guideline.md   rules for designing P1S-printable robot parts
    ├── power_system_design/               RevA design package (docx + Markdown sources)
    └── demo_captures_2026-10-21/          software setup demo captures
```

| I want to… | Open |
|---|---|
| Print the base plate | `cad/base_plate/print_3mf/plate_left.3mf` + `plate_right.3mf` |
| Print the USB hub tray | `cad/usb_hub_tray/print_3mf/hub_tray.3mf` |
| Edit in Fusion 360 | `cad/base_plate/step/plate_full.step` or `cad/assembly/kiro_power_tray.step` |
| See the full 3D scene | `blender/KIRO_power_plate.blend` |
| Wire the robot | `electrical/wiring_diagram/kiro_wiring_diagram.png` |
| Design a new body part | `docs/design_and_printing_guideline.md` |

---

## Cart power base plate

A single plate that sits in the cart's lower basket (330 × 235 mm, 55 mm deep, R40 corners) and holds all power electronics with clean, short cable runs.

<p align="center">
  <img src="cad/base_plate/images/preview_plate_iso.png" alt="Base plate" width="640">
</p>

### Components

| Component | Mounting |
|---|---|
| SMPS HS-350-12 (12 V, ~29 A, fan on top), 193 × 100 × 45 mm | Lies flat, fan up. Four 10 mm riser pads with long M4 slots under its mounting ears, plus two support rails; air gap underneath |
| Jetson Orin Nano Super Dev Kit (100 × 90 mm) | Four 10 mm standoffs (M2.5/M3 self-tap pilot), I/O edge facing the side wall |
| 2 × Dorhea 4-way blade fuse box (FB1 12 V, FB2 5 V) | Locating tabs + self-tapping screws |
| DC-DC buck 12 V → 5 V 15 A | Locating tabs + self-tapping screws |
| IEC C14 AC inlet with fuse and switch | 112 mm wall with side braces at the +X edge; inlet lower edge 67 mm above the plate bottom so the cord clears the basket rim |

No ground bus bar: 12 V returns land on the SMPS COM terminals, 5 V returns on the buck's OUT−.

### Features

- Honeycomb cut-outs (10 mm hex, 2.6 mm ribs) for airflow and less filament
- Zip-tie anchor slots along every cable route (AC, 12 V, 5 V, Jetson I/O)
- Engraved labels: `AC IN 220V`, `12V`, `5V OUT`, `JETSON I/O`
- Split into two halves with dovetail joints for printing on a Bambu Lab P1S

### Files (`cad/base_plate/`)

| File | Use |
|---|---|
| `step/plate_full.step` | Complete plate – open in Fusion 360 (**File → Open**) |
| `print_3mf/plate_full.3mf` | One-piece print (needs a bed larger than 256 mm) |
| `step/` + `print_3mf/` `plate_left` | Left half, 118 × 231 × 15 mm |
| `step/` + `print_3mf/` `plate_right` | Right half with AC tower, 217 × 231 × 112 mm |

### Printing (Bambu Lab P1S)

- Print `plate_left.3mf` and `plate_right.3mf` as two separate jobs, flat side down, no supports needed.
- PETG or ASA/ABS recommended (the SMPS runs warm); 0.2 mm layers, 3 walls, 15–20 % infill.
- Glue the dovetails with CA or epoxy.

### Regenerating the model

The model is fully parametric. Edit the constants at the top of [`power_plate.py`](cad/base_plate/power_plate.py), then:

```bash
pip install cadquery trimesh networkx lxml vtk
cd cad/base_plate && python power_plate.py && python render.py
cd ../usb_hub_tray && python hub_tray.py
cd ../assembly && python make_exports.py
```

### Open items

Values marked `VERIFY` in the script are estimates and must be measured on the real parts before final printing:

- Jetson carrier mounting-hole pattern (currently 86 × 58 mm)
- SMPS mounting-ear positions (`SMPS_EAR_X`, `SMPS_EAR_OUT`) – the 30 mm slots cover ±12 mm of error
- Exact footprints of the two fuse boxes and the buck converter

> Keep at least 20 mm of free air above the SMPS fan. The USB hub is deliberately **not** on this plate – it sits on the middle floor in its own tray.

---

## USB hub tray (middle floor)

<p align="center">
  <img src="blender/renders/hub.png" alt="USB hub tray" width="640">
</p>

Holds one ST Lab USB hub (157 × 37 × 40 mm) flat with its ports facing up. Both ends are open for the upstream USB and DC input cables, the floor has hex vents, and six zip-tie slot pairs in the side flanges tie it to the basket mesh. 165 × 73 × 25 mm – one print on the P1S, no supports.

Keeping the hub on the middle floor puts it next to the devices it feeds (servo adapters, lidar, gamepad, cameras), shortens the USB cables, and keeps USB away from the SMPS, mains wiring and servo power.

---

## Blender scene

`blender/KIRO_power_plate.blend` (Blender 5.2) contains every part in detail – SMPS with terminal strip and fan, Jetson, both fuse boxes with fuses, buck converter, C14 inlet, XT60/XT30 riser connectors, the C13 cord, the USB hub in its tray – and every wire as a curve with crimps and zip ties. Cameras: `CAM_hero`, `CAM_top`, `CAM_close`, `CAM_side`, `CAM_ac`, `CAM_hub`.

To rebuild it from the archived v2 scene:

```bash
blender -b blender/archive/KIRO_power_plate_v2_original.blend --python blender/update_blend_v3.py -- .
```

---

## Electrical wiring

<p align="center">
  <img src="electrical/wiring_diagram/kiro_wiring_diagram.png" alt="Kiro electrical wiring diagram" width="100%">
</p>

Rev F, based on `KIRO_FINAL.kicad_sch` with two Dorhea 4-way fuse boxes and no bus bar:

| Fuse | Box | Rail | Load | Wire |
|---|---|---|---|---|
| F0 5 A T | J1 inlet | 220 V AC | SMPS input | 0.75 mm² (18 AWG) |
| F1 5 A | FB1 | 12 V | Jetson Orin Nano (barrel 5.5 × 2.5 mm) | 18 AWG |
| F2 15 A | FB1 | 12 V | Wheel adapter + 4 × ST3215-C018 | 14 AWG |
| F3 15 A | FB1 | 12 V | Buck 12 V → 5 V input | 14 AWG |
| F4 2 A | FB2 | 5 V | Leader adapter + 6 × STS3215 | 20 AWG |
| F5 15 A | FB2 | 5 V | Follower adapter + 6 × STS3215 (5 V test) | 14 AWG |

- SMPS +V → FB1 uses 12 AWG.
- Returns go back to their source: Jetson, base adapter and buck IN− → **PSU1 COM**; leader and follower adapters → **buck OUT−**. One wire per screw terminal, never daisy-chained.
- FB2 is fed only from the buck's 5 V output – never from 12 V.

Regenerate the diagram with `python electrical/wiring_diagram/make_wiring.py` (needs Chrome or Edge for the PNG).

---

## Power system design (summary)

From the RevA design package in [`docs/power_system_design/`](docs/power_system_design):

- One 12 V SMPS replaces all wall adapters.
- The wheel servos and the Jetson run directly from 12 V (Jetson jack accepts 9–20 V).
- A buck converter makes 5 V for the arm adapters (followers on 5 V as a test, per the schematic).
- See `Kiro_SO101_Power_System_Design_RevA.docx` for the full load budget, schematics, cable schedule and parts list.

---

## Designing new robot parts

All Kiro body parts are printed on a Bambu Lab P1S. Before modelling anything, read the **[Design & Printing Guideline](docs/design_and_printing_guideline.md)** – it covers the 245 mm part limit, dovetail splitting, tolerances, print orientation, materials and the file hand-off format (`.step` + `.3mf`).

---

## Safety

The AC side carries mains voltage. Insulate all spade terminals with heat-shrink, connect protective earth to the SMPS earth terminal, use a slow-blow fuse in the inlet, and always unplug the robot before working on the wiring.
