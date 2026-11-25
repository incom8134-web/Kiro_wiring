# INA228 case and shunt plate

[English](README.md) | [한국어](README.ko.md)

A printed base and lid for the INA228 breakout, and a separate plate that bolts to the case and holds the shunt. The case cavity, slots, and flanges are unchanged. The Jetson stays where it already is.

Body **48.8 × 46.4 × 20.1 mm**. With the two side flanges, **72.8 × 46.4 × 20.1 mm**. Cavity **43.8 × 41.4 × 15.1 mm**. Wall 2.5 mm, floor 2.5 mm, lid 2.5 mm. Fit clearance is 0.25 mm per side.

The board is the Adafruit INA228, product 5832. The product page lists 25.8 × 20.2 × 10.1 mm. The Eagle board is 25.4 × 20.32 mm, with 2.5 mm holes at (2.54, 17.78) and (22.86, 17.78) mm. The keep-out used here is 25.8 × 20.4 × 10.1 mm. It sits on 3 mm standoffs. The standoff height is a parameter, not a measured solder-side height.

Two slots in the north wall, open at the top:

| Slot | Carries |
|---|---|
| sensor | Sensor cable: pin 1 3.3 V, pin 6 GND, pin 3 SDA, pin 5 SCL |
| sense | IN+, IN−, VBUS |

The INA228 is I2C only. UART pins 8 and 10 stay on the Jetson and do not enter this box.

## Shunt plate

The plate is its own part, `export/shunt_base.step` and `export/shunt_base.stl`. It bolts through the two M3 holes that are already in the case flanges. Nothing was added to the case solid.

The plate’s bounding box is **116.0 × 69.8 × 18.05 mm**. The sheet is 4 mm thick. Standoffs and the cable-channel ribs make up the rest of the height. With the case on it, the assembly is **116.0 × 86.0 × 24.15 mm**.

The shunt outline is the Accuenergy Shunt-100A, 75 mV, from the [datasheet dated August 2024, version 1.0.3](https://www.accuenergy.com/wp-content/uploads/DC-Current-Shunt-100A-75mV.pdf):

| Callout | Value |
|---|---|
| Length, width, thickness | 104 × 21.6 × 2.0 mm |
| Current holes | two, Φ8.5 mm, 85 mm apart |
| Sense screws | two, M5, 62 mm apart |

The 85 mm and 62 mm spans are centered on the 104 mm length. That is how those callouts sit on one axis of the drawing. The pack current is still unknown. This is the mechanical outline of that common bar, not a chosen resistance. `SHUNT_L`, `SHUNT_W`, `SHUNT_T`, `SHUNT_CURRENT_PITCH`, `SHUNT_CURRENT_HOLE`, and `SHUNT_SENSE_PITCH` are the parameters.

The bar sits on four standoffs, 12 mm tall, on the north side of the case. Twelve millimetres clears an ISO 4032 M8 nut, which is 6.8 mm thick, under each current terminal. Each terminal also has an 18 mm through-window in the plate so the nut is not buried in plastic. The battery lugs are the owner’s.

A channel, 8 mm wide, runs from the sense slot to the near edge of the shunt. The sense leads stay short. They are still unfused.

Each flange has one M3 clearance hole, 3.4 mm (ISO 273 medium). The lid uses four M2 screws. The insert hole is 3.2 mm by 4.0 mm and is not from an insert datasheet. The INA228 uses M2 screws and ISO 4032 nuts.

Print the base floor-down. The lid STL already has the outer face on the bed. Print the shunt plate with the sheet on the bed and the standoffs pointing up. PETG or ABS, 0.2 mm layers, 0.4 mm nozzle. The slots are open at the top so they need no support. The lug windows are vertical through-holes.

These defaults are parameters. Change them in `enclosure.py` and run it again.

| Parameter | Default | Why it is unverified |
|---|---|---|
| `INA_STANDOFF` | 3.0 mm | Clearance under the PCB. Not on the product page. |
| `AIR_ABOVE` | 2.0 mm | Gap from the tallest part to the lid. |
| `SENSOR_CABLE_OD` | 4.0 mm | The sensor cable is not chosen. |
| `SENSE_CABLE_OD` | 4.0 mm | The sense cable is not chosen. |
| `BEND_CLEAR` | 12.0 mm | Open floor north of the board. |
| `INSERT_HOLE_D`, `INSERT_DEPTH` | 3.2 mm, 4.0 mm | Match the inserts you buy. |
| `TAB_LEN`, `TAB_W` | 12 mm, 14 mm | Flange size. Not from a robot drawing. |
| `SHUNT_L`, `SHUNT_W`, `SHUNT_T` | 104, 21.6, 2.0 mm | Accuenergy drawing. Change them for another bar in the same family. |
| `SHUNT_CURRENT_PITCH`, `SHUNT_CURRENT_HOLE` | 85 mm, 8.5 mm | Same drawing. |
| `SHUNT_SENSE_PITCH` | 62 mm | Same drawing. The screws are M5. |
| `PLATE_T` | 4.0 mm | Sheet thickness. |
| `STANDOFF_H` | 12.0 mm | Room for an ISO 4032 M8 nut under the terminal. |
| `LUG_CLEAR_D` | 18.0 mm | Window under each current hole. |
| `GAP_NORTH`, `CHANNEL_W` | 14 mm, 8 mm | Gap and guide from the sense slot to the shunt. |

```bash
python3 enclosure.py
```

Outputs: `export/base.step`, `export/base.stl`, `export/lid.step`, `export/lid.stl`, `export/shunt_base.step`, `export/shunt_base.stl`, `export/assembly.step`, `export/dimensions.json`, `export/manifold.txt`, `preview.png`.

Last check: base, lid, and shunt plate watertight, windings consistent. Intersections are 0 mm³. Base volume 15450.669 mm³. Lid volume 5658.788 mm³. Shunt plate volume 22184.255 mm³. Case base extents are still 72.8 × 46.4 × 17.6 mm.

Citations: [Adafruit INA228](https://www.adafruit.com/product/5832), Adafruit Eagle board `Adafruit INA228 I2C Power Monitor.brd`, [Accuenergy Shunt-100A](https://www.accuenergy.com/wp-content/uploads/DC-Current-Shunt-100A-75mV.pdf), ISO 273, ISO 4032.
