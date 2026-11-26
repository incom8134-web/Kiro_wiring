# HAEBOT photo wiring guide - Rev B supplement

This is a pictorial companion to the saved Rev B schematic and wiring table. Connections are drawn as editable
vector lines, with real reference photographs, so wire labels remain legible when zooming or printing.

- [Three-page printable guide](../exports/HAEBOT_EV_PHOTO_WIRING_GUIDE.pdf)
- [Power harness image](../exports/HAEBOT_EV_PHOTO_WIRING_01.png)
- [E-stop and contactor image](../exports/HAEBOT_EV_PHOTO_WIRING_02.png)
- [Matek and adapter close-ups](../exports/HAEBOT_EV_PHOTO_WIRING_03.png)

Sheet 1 follows the main discharge path, three fused motion branches, separate Jetson/buck feeds and one NC coil
stop. **N** means a separate return wire to the battery-negative star bus; it does not mean a return through USB.
Sheet 2 explains the main/coil stud groups and mechanically latching stop. Sheet 3 identifies the Matek and servo
adapter connectors. The photo positions are not a substitute for actual polarity markings.

## Battery selected during this update

The user selected **VOLTON 12 V, 45 Ah lithium-ion** and explicitly confirmed the 45 Ah option. This supersedes the
earlier unidentified-battery description for product selection. The specific pack's cell-series configuration,
full-charge/minimum voltage, BMS continuous/burst current, discharge lead/connector rating and charger remain
unverified. The existing generic Rev B electrical design is retained; this supplement does not authorise bypassing
U3 or finalise the main fuse/coil protection. Nominal 12 V and capacity 45 Ah do not establish the discharge-current
capability. Do not infer a confirmed 3S configuration from the product-family name.

- User's selected listing: https://www.coupang.com/vp/products/9101801616?vendorItemId=93727752087
- Manufacturer's 45 Ah product: https://www.voltonbattery.com/12v/?idx=407
- Official title identifies 12 V 45 Ah lithium-ion; exact electrical limits above are not established by the title.
- The barrel lead visible in the pack photo is not automatically the robot discharge connection. Identify charge
  and discharge leads, connector polarity and current ratings on the actual pack before making the harness.

## Reference pictures and limitations

Original images are bundled unchanged in `assets/`; the document uses clipped image viewports. It contains no
AI-generated component photographs and does not fabricate an unknown battery/regulator/connector pinout.
The asset manifest is [assets/sources.json](assets/sources.json).

| Picture | Status / source |
|---|---|
| VOLTON battery | Official selected 12 V 45 Ah product-family photograph; physical pack label still needed |
| K1 contactor | User's actual photograph, labelled 500A DC12V; exact MPN, coil polarity/duty and DC breaking rating unverified |
| Matek I2C-INA-BM | Manufacturer photograph; sample XT60 leads in that picture are not included with the board |
| Servo adapters | Waveshare Bus Servo Adapter (A) V1.1 manufacturer photograph; verify the actual CH343 boards match |
| Jetson | NVIDIA hardware-layout photograph; green numbers are feature callouts, not GPIO pin numbers |
| EA75-5V | Seller photograph of the recorded converter model; actual terminal labels override image orientation |
| FB1 fuse block | Clipped legacy project 3D render for appearance only; use the NEW fuse labels next to it, not the old fuse colours/values in the render |
| E-stop | Native drawing of a latching NC mushroom; no particular switch has been selected or purchased |
| U3 | Dashed functional placeholder because the regulator has not been selected |

Technical references:

- Matek: https://www.mateksys.com/?portfolio=i2c-ina-bm
- Waveshare interfaces: https://docs.waveshare.com/Bus_Servo_Adapter_A
- NVIDIA hardware layout: https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/hardware_layout.html
- Example of the latching NC type (not a selected part or a coil-load compatibility approval):
  https://www.se.com/us/en/product/XB5AS8442/emergency-stop-switching-off-harmony-xb5-plastic-red-mushroom-40mm-22mm-trigger-latching-turn-to-release-1nc/

## Checks and remaining work

All three PDF pages are rendered and visually checked for readable labels, routing and clipping. Main feeds and
branch labels are checked against `../docs/wiring_connections.md`; the electrical topology is unchanged.
This pictorial supplement is not evidence of a powered hardware test. In particular:

- Twisting S1 to release immediately restores motor power; there is no START or restart interlock.
- K1 coil continuous duty/current/voltage/polarity/suppression and S1's DC inductive rating need verification.
- Matek 5V is regulated 5 V from F23/J5, not battery positive. G returns to POWER_GND.
- Jetson I2C physical header pins, signal voltage/pull-ups, chip variant and driver remain TBD.
- New arms use 12 V servos; exact models, current and connector ratings remain unverified.
- Fit and size protection using actual battery and component ratings before building.

Regenerate with `python tools/render_photo_wiring.py` using Python + ReportLab + Pillow + pypdf and the same font
paths as the existing diagram tool. Sources with embedded images are in `../block-diagrams/HAEBOT_EV_PHOTO_WIRING_*.svg`.
Render the final PDF to PNG previews with PyMuPDF. Existing KiCad files and their electrical exports are unchanged by
this supplement.
