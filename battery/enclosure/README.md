# INA228 case

A printed base and lid for the INA228 breakout only. The shunt stays at the battery. The Jetson stays where it already is.

Body **48.8 × 46.4 × 20.1 mm**. With the two side flanges, **72.8 × 46.4 × 20.1 mm**. Cavity **43.8 × 41.4 × 15.1 mm**. Wall 2.5 mm, floor 2.5 mm, lid 2.5 mm. Fit clearance is 0.25 mm per side.

The board is the Adafruit INA228, product 5832. The product page lists 25.8 × 20.2 × 10.1 mm. The Eagle board is 25.4 × 20.32 mm, with 2.5 mm holes at (2.54, 17.78) and (22.86, 17.78) mm. The keep-out used here is 25.8 × 20.4 × 10.1 mm. It sits on 3 mm standoffs. The standoff height is a parameter, not a measured solder-side height.

Two slots in the north wall, open at the top:

| Slot | Carries |
|---|---|
| sensor | Sensor cable: pin 1 3.3 V, pin 6 GND, pin 3 SDA, pin 5 SCL |
| sense | IN+, IN−, VBUS |

The INA228 is I2C only. UART pins 8 and 10 stay on the Jetson and do not enter this box.

Each flange has one M3 clearance hole, 3.4 mm (ISO 273 medium). The lid uses four M2 screws. The insert hole is 3.2 mm by 4.0 mm and is not from an insert datasheet. The INA228 uses M2 screws and ISO 4032 nuts.

Print the base floor-down. The lid STL already has the outer face on the bed. PETG or ABS, 0.2 mm layers, 0.4 mm nozzle. The slots are open at the top so they need no support.

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

```bash
python3 enclosure.py
```

Outputs: `export/base.step`, `export/base.stl`, `export/lid.step`, `export/lid.stl`, `export/assembly.step`, `export/dimensions.json`, `export/manifold.txt`, `preview.png`.

Last check: base and lid watertight, windings consistent, intersection 0 mm³. Base volume 15450.669 mm³. Lid volume 5658.788 mm³.

Citations: [Adafruit INA228](https://www.adafruit.com/product/5832), Adafruit Eagle board `Adafruit INA228 I2C Power Monitor.brd`, ISO 273, ISO 4032.
