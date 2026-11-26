# Matek I2C-INA-BM case

[English](README.md) | [한국어](README.ko.md)

A printed base and lid for the Matek I2C-INA-BM. The shunt is the module's own conductive path, so there is no shunt plate. The Jetson stays where it already is.

Body **33.8 × 26.8 × 11.8 mm**. With the two mounting tabs, the base is **49.8 × 26.8 × 10.0 mm**. Cavity **29.4 × 22.4 × 8.2 mm**. Wall 2.2 mm, floor 1.8 mm, lid 1.8 mm. Fit clearance is 1.2 mm per side. The lid print, outer face on the bed, is **33.8 × 26.8 × 4.2 mm**.

The board size is the one Matek publishes: 27 × 20 × 6 mm ([product page](https://www.mateksys.com/?portfolio=i2c-ina-bm)). It sits on 1.2 mm corner pads so the bottom pad Matek calls dead is not clamped to the floor. Corner ribs locate the board. Nothing is screwed through the PCB. A φ3 mm hole mentioned by a retailer is not on the Matek page and is not used.

Openings, all open at the top so they need no support:

| Opening | Where | Size |
|---|---|---|
| Power lead | One in each short wall, BAT+ and ESC+ | 6 mm wide. A printable default, not a chosen wire gauge. The pack current is unknown. |
| JST-GH | Two, in one long wall | 11 mm wide |

The JST side follows the product photo, not a dimensioned drawing. Change `JST_W`, `WIRE_W`, and the positions in `enclosure.py` if a drawing shows something else.

Each tab has one M3 clearance hole, 3.4 mm (ISO 273 medium). The lid is a drop-in cover with a skirt. It is not screwed.

Print the base floor-down. The lid STL already has the outer face on the bed. PLA or PETG, 0.2 mm layers, 0.4 mm nozzle, on an Anycubic Kossel Linear Plus. Floor vents and lid vents sit over the on-board shunt.

| Parameter | Default | Why it is unverified |
|---|---|---|
| `BOARD_X`, `BOARD_Y`, `BOARD_Z` | 27, 20, 6 mm | Matek's published module size. The 6 mm figure is not a measured solder-side height. |
| `STANDOFF` | 1.2 mm | Clearance under the dead pad. Not a Matek callout. |
| `AIR` | 1.0 mm | Gap from the module top to the lid. |
| `WIRE_W` | 6.0 mm | Opening, not a conductor. Pack current is unknown. |
| `JST_W` | 11.0 mm | Photo estimate of a JST-GH-4P plug, plus clearance. |
| `FIT` | 1.2 mm | Per side, so the board drops in. |
| `TAB_LEN`, `TAB_W` | 8 mm, 10 mm | Not from a robot drawing. |

```bash
python3 enclosure.py
```

Outputs: `export/base.step`, `export/base.stl`, `export/lid.step`, `export/lid.stl`, `export/assembly.step`, `export/dimensions.json`, `export/manifold.txt`, `preview.png`.

Last check: base and lid watertight, windings consistent. Intersection 0 mm³. Base volume 3537.653 mm³, extents 49.8 × 26.8 × 10.0 mm. Lid volume 1808.772 mm³, extents 33.8 × 26.8 × 4.2 mm.

Citations: [Matek I2C-INA-BM](https://www.mateksys.com/?portfolio=i2c-ina-bm), ISO 273.
