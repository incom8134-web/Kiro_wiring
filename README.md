# Kiro Wiring

Power system and electronics packaging for the **Kiro / SO-101 mobile dual-arm robot**: an XLeRobot-style mobile manipulator built around an NVIDIA Jetson Orin Nano, with two SO-101 leader arms, two SO-101 follower arms and a mecanum-wheel base.

The goal of this repository is to replace the pile of wall adapters and loose cables on the robot cart with a **single SMPS, fused 12 V distribution and buck converters**, mounted on 3D-printed hardware so the robot looks and behaves like a consumer-grade product instead of an R&D prototype.

<p align="center">
  <img src="cart_power_plate/out/preview_plate_iso.png" alt="Cart power base plate" width="720">
</p>

---

## Repository layout

| Path | Contents |
|---|---|
| [`cart_power_plate/`](cart_power_plate) | Parametric base plate for the cart's lower tray (CadQuery source, STEP + 3MF exports, previews) |
| [`design_and_printing_guideline.md`](design_and_printing_guideline.md) | Rules for designing robot body parts that print on a Bambu Lab P1S (size limits, dovetail joints, tolerances, materials) |
| [`KIRO_FINAL.kicad_sch`](KIRO_FINAL.kicad_sch) | KiCad schematic of the power system |
| [`group_convo/`](group_convo) | Power system design package: design document (RevA), project context, power calculation, parts list, Markdown sources, and the 2026-10-21 software setup demo captures |

---

## Cart power base plate

A single plate that sits in the cart's lower basket (330 × 235 mm, 55 mm deep, R40 corners) and holds all power electronics with clean, short cable runs.

### Components

| Component | Mounting |
|---|---|
| SMPS 12 V 200 W | Two raised rails (10 mm) with M4 slots, screwed from below; airflow channel underneath |
| Jetson Orin Nano Super Dev Kit | Four 10 mm standoffs (M2.5/M3 self-tap pilot), I/O edge facing the side wall |
| 6-way blade fuse block with negative bus | Locating tabs + self-tapping screws |
| DC-DC buck 12 V → 5 V 15 A | Locating tabs + self-tapping screws |
| IEC C14 AC inlet with fuse and switch | Tower raised 4 in (101.6 mm) above the plate so the power cord clears the basket rim |

### Features

- Honeycomb cut-outs (10 mm hex, 2.6 mm ribs) for airflow and ~20 % less filament
- Zip-tie anchor slots along every cable route (AC, 12 V, fused 12 V, 5 V, Jetson I/O)
- Engraved labels: `AC IN 220V`, `12V`, `FUSED 12V`, `5V OUT`, `JETSON I/O`
- Split into two halves with dovetail joints for printing on a Bambu Lab P1S

### Files

All exports are in [`cart_power_plate/out/`](cart_power_plate/out):

| File | Use |
|---|---|
| `plate_full.step` | Complete plate – open in Fusion 360 (**File → Open**) |
| `plate_full.3mf` | One-piece print (needs a bed larger than 256 mm) |
| `plate_left.step` / `.3mf` | Left half, 118 × 231 × 15 mm |
| `plate_right.step` / `.3mf` | Right half with AC tower, 217 × 231 × 158 mm |

### Printing (Bambu Lab P1S)

- Print `plate_left.3mf` and `plate_right.3mf` as two separate jobs, flat side down, no supports needed.
- PETG or ASA/ABS recommended (the SMPS runs warm); 0.2 mm layers, 3 walls, 15–20 % infill.
- Glue the dovetails with CA or epoxy.

### Regenerating the model

The model is fully parametric. Edit the constants at the top of [`power_plate.py`](cart_power_plate/power_plate.py) (component sizes, positions, hole patterns, honeycomb size), then:

```bash
pip install cadquery trimesh networkx lxml vtk
cd cart_power_plate
python power_plate.py   # writes STEP + 3MF to out/
python render.py        # optional: refreshes the preview images
```

### Open items

Values marked `VERIFY` in the script are estimates from product listings and must be measured on the real parts before final printing:

- Jetson carrier mounting-hole pattern (currently 86 × 58 mm)
- SMPS bottom mounting-hole row spacing (currently 50 mm)
- Exact footprints of the SMPS, fuse block and buck converter

> The plate is currently sized for the 12 V 200 W SMPS. The RevA design document specifies a Mean Well LRS-350-12; update the `COMPONENTS` table in the script if the SMPS changes.

---

## Power system design (summary)

From the RevA design package in [`group_convo/`](group_convo):

- One 12 V SMPS replaces all wall adapters.
- The wheel servos and the Jetson run directly from 12 V (Jetson jack accepts 9–20 V).
- Buck converters make 7.2 V for the follower arms and 5 V for the USB hub, lidar and leader arms.
- Two blade-fuse groups and a GND bus bar distribute power in a star:
  - **Group A** (Jetson, 5 V buck, spare) is always on.
  - **Group B** (wheels, follower bucks) sits behind a relay driven by a mushroom E-stop and key switch, so a stop kills motion while compute and sensors stay powered.

See `Kiro_SO101_Power_System_Design_RevA.docx` for the full load budget, schematics, cable schedule and parts list.

---

## Designing new robot parts

All Kiro body parts are printed on a Bambu Lab P1S. Before modelling anything, read the **[Design & Printing Guideline](design_and_printing_guideline.md)** – it covers the 245 mm part limit, dovetail splitting, tolerances, print orientation, materials and the file hand-off format (`.step` + `.3mf`).

---

## Safety

The AC side carries mains voltage. Insulate all spade terminals with heat-shrink, connect protective earth to the SMPS earth terminal, use a slow-blow fuse in the inlet, and always unplug the robot before working on the wiring.
