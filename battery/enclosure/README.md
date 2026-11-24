# Enclosure

Printable base and lid for the display and sense pod on the hover-robot head. The Korean summary is in [`../README.ko.md`](../README.ko.md), section 11. This file is the source of the dimensions.

![Base with the boards in place, and the lid lifted](preview.png)

The Jetson Nano, the buck, and the main fuse are not in this box. The shunt stays at the battery. This shell is a little larger than the LCD, deep enough for the backpack and the two boards behind it.

Regenerate everything in this folder with:

```bash
python3 -m pip install -r requirements.txt
python3 enclosure.py
```

Tested with CadQuery 2.8.0, trimesh 5.2.2, and Python 3.12. The script writes `export/`, `preview.png`, and `export/manifold.txt`. It exits non-zero if the base and the lid are not single valid solids, if they intersect, or if either STL is not watertight.

Only `export/base` and `export/lid` are for printing. `export/assembly.step` is the base, the lid, and reference envelopes. Envelope names start with `REF_`. Names that also contain `UNVERIFIED` are boxes for parts that have no datasheet size yet.

| File | What it is |
|---|---|
| `enclosure.py` | Parametric model |
| `export/base.step`, `export/base.stl` | Base, print it floor-down |
| `export/lid.step`, `export/lid.stl` | Lid, outer face already on Z=0 |
| `export/assembly.step` | Base, lid, and reference envelopes |
| `export/dimensions.json` | Numbers the model actually built |
| `preview.png` | The figure above |

Last run: base STL watertight, 101474 mm³. Lid STL watertight, 26070 mm³. Both windings consistent (trimesh). Base and lid intersection 0 mm³.

## What this pod is

Body **125.0 × 88.0 × 54.1 mm**. The two side flanges and the north tie-down tab bring the footprint to **153.0 × 100.0 mm**. Cavity **120.0 × 83.0 × 48.6 mm**. Walls 2.5 mm, floor 3.0 mm, lid 2.5 mm. Board clearance is 0.25 mm per side. The floor is 3.0 mm because the mounting flanges are the floor.

The LCD faces out. The floor faces the robot head. One flange sticks out of the east wall and one out of the west wall, each 14 mm long and 18 mm wide, with an M3 clearance hole (ISO 273 medium, 3.4 mm). Bolt those flanges to a plate on the head. The tab length and width are parameters, not a measured bracket.

## What is inside

| Place | What | Basis |
|---|---|---|
| Lid | Winstar WH2004A, window 75.0 × 23.2 mm | Module 98.0 × 60.0 × 13.6 mm MAX, view area 77.0 × 25.2 mm, four Ø2.5 holes, pitch 93.0 × 55.0 mm. The window is 1 mm inside the view area on each side. |
| Floor, under the LCD | INA228, then the USB-I2C adapter beside it | INA228 outline and holes from Adafruit's Eagle board. The adapter envelope is unverified. |
| Between them and the LCD | PCF8574 backpack | Depth is a parameter. It is not on the Winstar drawing. |

The LCD corner holes hold the module to the lid. The INA228 uses its own two holes on floor standoffs. The adapter is held by cleats, because its holes are not known. The boards sit in the stack behind the LCD. They do not share the LCD screw pattern.

The 10 Ω Kelvin resistors and the 100 Ω VBUS resistor sit next to the INA228. They are not separate printed features.

Not in this box: the Jetson, the buck, F1, F2, the shunt, and the TMP117. The TMP117 stays on the pack and is wired at the Jetson header.

## Cables

Three slots in the north wall, open at the top so they print without a support. The lid closes the top of each slot. A hole in the north floor tab is the cable tie. Slot width is the jacket diameter plus 0.25 mm per side. Both diameters are unverified.

| Slot, west to east | Width | What is in the jacket |
|---|---|---|
| Shunt, battery side | 4.5 mm | IN+ and VBUS |
| Shunt, bus side | 4.5 mm | IN−. Leave the spare conductor open. It is not pack power. |
| UART | 6.5 mm | Pin 1 3.3 V, pin 6 GND, pin 3 SDA, pin 5 SCL, pin 8 TX, pin 10 RX |

F3 is three 100 mA fuses at the shunt, outside the pod, one on each of IN+, IN−, and VBUS. The series resistors stay inside, next to the INA228.

The UART slot has to carry 3.3 V, GND, SDA, and SCL. TX and RX alone do not power the LCD or the INA228, and they do not speak to either part. Those four conductors share the jacket so the wall still has one UART opening. Keep the cable short. Pin 8 is a weak driver.

The USB-I2C adapter is mounted in the pod and has no slot. Leave it unwired. If pins 3 and 5 are already taken, add a USB lead and take SDA and SCL out of the UART jacket. Do not connect both. If you do that, the TMP117 on the pack is not on the adapter's bus unless its wires come into the pod as well.

## Fasteners

Four M3 screws hold the lid, one in the middle of each wall, in the margin around the LCD. The insert hole defaults to 4.0 mm diameter and 6.0 mm deep. That pair is not from an insert datasheet. Set `INSERT_HOLE_D` and `INSERT_DEPTH` from the insert you buy.

LCD and INA228 screws are M2, with ISO 4032 nuts in pockets (M2 across flats 4.0 mm, thickness 1.6 mm, plus 0.25 mm per side). Clearance holes follow ISO 273 medium: M2 2.4 mm, M3 3.4 mm.

## Print

- Material: PETG or ABS.
- Base: floor on the bed. The flanges and the tie-down tab are in that layer.
- Lid: the STL already has the outer face on Z=0 and the skirt and LCD standoffs pointing up. Do not flip it again.
- 0.2 mm layers, 0.4 mm nozzle, 5 perimeters, 20% infill.
- No supports are designed in. Vents are 3 mm wide vertical slots. Cable slots are open at the top. Nut pockets on the lid open upward in the print orientation. Nut pockets on the base open downward, into the first layers.
- A 160 × 110 mm bed fits the base, including the flanges.

## Citations

- Winstar WH2004A contour drawing, module 98.0 × 60.0 × 13.6 mm MAX, view area 77.0 × 25.2 mm, four Ø2.5 holes, pitch 93.0 mm and 55.0 mm, inset 2.5 mm. [Winstar PDF](https://www.winstar.com.tw/uploads/files/6e5109c5ba979085d164c6b48a5bb66d.pdf).
- Adafruit INA228, product 5832. PCB outline 25.4 × 20.32 mm and 2.5 mm holes at (2.54, 17.78) and (22.86, 17.78) mm, read from Adafruit's Eagle board. Assembled size 25.8 × 20.2 × 10.1 mm from the [product page](https://www.adafruit.com/product/5832). The keep-out uses 25.8 × 20.4 × 10.1 mm.
- ISO 273 medium clearance holes. ISO 4032 hex nuts.
- Jetson pin numbers used on the UART cable are the ones in `battery/README.md` and NVIDIA user guide DA_09402, connector J41. The Jetson itself is not in this box.

## Unverified parameters

Change these in `enclosure.py`. The cavity grows when a part no longer fits.

| Name | Default | Note |
|---|---|---|
| `LCD_STANDOFF` | 13.6 mm | WH2004A maximum module thickness, if the PCB is the back face. The drawing also shows 9.0 mm and 1.6 mm for the LED backlight. |
| `LCD_BACKPACK_DEPTH` | 16.0 mm | Sets most of the pod depth. Not on the Winstar drawing. |
| `ADAPTER_L/W/H` | 54 × 22 × 14 mm | No USB-I2C adapter is selected. |
| `UART_CABLE_OD` | 6.0 mm | Six-conductor jacket. Not a chosen cable. |
| `SENSE_CABLE_OD` | 4.0 mm | Small pair. Not a chosen cable. |
| `BEND_CLEAR` | 12 mm | Open floor between the LCD and the north wall. |
| `INSERT_HOLE_D`, `INSERT_DEPTH` | 4.0 mm, 6.0 mm | Match the heat-set insert. |
| `TAB_LEN`, `TAB_W` | 14 mm, 18 mm | Flange that bolts to the robot head. |
| `TIE_HOLE` | 4.0 mm | Cable-tie hole in the north tab. |
