# Parts List – Kiro power system (Rev F)

Updated 2026-10-26. Quantities are for one robot as built
(one leader arm, one follower arm, mecanum base). **On hand** = already bought.

## A. Power components

| # | Item | Spec | Qty | Status | Role |
|---|---|---|---|---|---|
| A1 | SMPS | **HS-350-12** – 12 V ~29 A, 350 W, fan, 193 × 100 × 45 mm, mounting ears | 1 | on hand | single 12 V main bus |
| A2 | Buck converter | **TOBSUN EA75-5V** – 12/24 V → 5 V, 15 A max, 75 W | 1 | on hand | 5 V rail for both arm adapters |
| A3 | Blade fuse box | **Dorhea 4-way**, ATO, single live input, no negative bus | 2 | on hand | FB1 12 V, FB2 5 V |
| A4 | Blade fuses (ATO) | kit 5 / 10 / 15 / 20 A | 1 kit | on hand | F1–F3, F5 |
| A5 | Blade fuse 2 A (or 3 A) | ATO | 2 | **to buy** | F4 leader (+ spare) |
| A6 | AC inlet | IEC C14 with rocker switch and fuse drawer | 1 | on hand | mains switch + fuse |
| A7 | Inlet fuse | 5 × 20 mm, **5 A slow-blow** | 3 | check | F0 (+ spares) |
| A8 | Mains cord | IEC C13, 3-core with earth | 1 | on hand | – |

## B. Compute and USB

| # | Item | Spec | Qty | Status |
|---|---|---|---|---|
| B1 | Jetson Orin Nano Super Developer Kit | 100 × 90 mm, DC jack 9–20 V | 1 | on hand |
| B2 | USB hub | ST Lab, 4 downstream ports, own DC input (verify voltage), 157 × 37 × 40 mm | 1 | on hand |
| B3 | Servo bus adapters | CH343 boards (Waveshare Bus Servo Adapter (A) type) – base, leader, follower | 3 | on hand |

## C. Wire and connectors

| # | Item | Spec | Qty | Use |
|---|---|---|---|---|
| C1 | Silicone wire 12 AWG | red | 0.5 m | SMPS +V → FB1 |
| C2 | Silicone wire 14 AWG | red + black, 3 m each | 1 | wheels, buck in/out, follower |
| C3 | Silicone wire 18 AWG | red + black, 2 m each | 1 | Jetson, AC (or 0.75 mm² 3-core) |
| C4 | Silicone wire 20 AWG | red + black, 2 m each | 1 | leader |
| C5 | DC barrel plug 5.5 × 2.5 mm | centre positive, strain relief | 1 | Jetson |
| C6 | XT60 / XT30 pairs | Amass | 2 / 4 | riser connectors to the upper floors |
| C7 | Molex 5264 leads, 22 AWG | pre-crimped kit | 1 | servo leads |
| C8 | Bootlace ferrules + crimper | 12–20 AWG | 1 | every screw terminal |
| C9 | Ring / fork terminals M4 | 12–14 AWG | 10 | SMPS and fuse box studs |
| C10 | Heat-shrink, zip ties, spiral wrap / braided sleeve, labels | assorted | 1 | harness; label FB2 "5 V ONLY" |

## D. Printed parts (Bambu Lab P1S, PETG or ASA)

| # | Part | File | Notes |
|---|---|---|---|
| D1 | Base plate, left half | `3d_models/print_files/base_plate_left.3mf` | 118 × 231 × 15 mm |
| D2 | Base plate, right half (AC tower) | `3d_models/print_files/base_plate_right.3mf` | 217 × 231 × 112 mm, glue the dovetails |
| D3 | USB hub tray | `3d_models/print_files/usb_hub_tray.3mf` | middle floor, zip-tied to the mesh |
| D4 | Screws | M4 × 10 (SMPS ears), M3 / M2.5 self-tapping (Jetson, fuse boxes, buck) | – |

## E. Test equipment

| # | Item | Why |
|---|---|---|
| E1 | Digital multimeter | set the SMPS, check the buck output before connecting loads |
| E2 | DC clamp meter (≥ 40 A DC) | branch currents and the SMPS peak during the demo |

## F. Planned upgrades (not in this build)

| Item | For |
|---|---|
| 22 mm mushroom E-stop (NC) + key switch + 12 V 40 A automotive relay + 1N4007 | hardware E-stop on the wheel and follower rails |
| 8–12 A buck set to 7.2 V + 2200 µF / 16 V capacitor | follower rail upgrade |
| Regulated 12 V power station or 3S Li-ion pack with BMS | battery operation |
