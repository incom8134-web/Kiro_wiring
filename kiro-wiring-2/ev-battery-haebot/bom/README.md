# Bill of materials: EV battery design (Rev A)

Full table with every column: [`HAEBOT_EV_BOM.csv`](HAEBOT_EV_BOM.csv). "not selected" means no part number has been
chosen. No part number in this file is invented.

| Ref | Component | Function | Manufacturer / model | Operating voltage | Rated current | Peak current | Qty | Status | Verification |
|---|---|---|---|---|---|---|---|---|---|
| BT1 | Battery 12 V 45 Ah | Main energy source | not identified | 12 V nominal | TBD (BMS) | TBD | 1 | Existing (user brief) | Blocked |
| J2 | Charger inlet + matching charger | Charging | not identified | per chemistry | TBD | - | 1 | Blocked | Blocked |
| F1 | Main fuse 40 A + holder | Battery protection | ANL or MIDI type, not selected | 32 V or more | 40 A | - | 1 | Proposed | Calculated |
| F2 | Charge fuse 15 A | Charge lead protection | not selected | 32 V | 15 A | - | 1 | Proposed | Placeholder |
| SW1 | Battery disconnect switch | Main disconnect | not selected | 12 V DC | >= 100 A | - | 1 | Proposed | Not verified |
| K1 | DC contactor with 1 NO aux | E-stop power contactor | not selected | 12 V coil | >= 80 A contacts | - | 1 | Proposed | Not verified |
| U3 | 12 V regulator (buck-boost) | Motion rail stabiliser | not selected | in 9-16 V, out 12.0 V | >= 20 A | - | 1 | Proposed, conditional | Not verified |
| FB1 | 4-way blade fuse box | 12 V motion distribution | Dorhea 4-way (V1) | 12 V | per slot | - | 1 | Existing (V1) | Verified part |
| FB2 | 4-way blade fuse box | 5 V distribution | Dorhea 4-way (V1) | 5 V | per slot | - | 1 | Existing (V1) | Verified part |
| F11 | Blade fuse 15 A | Wheel branch | ATO | 32 V | 15 A | - | 1 | Existing (V1 kit) | Value verified (V1) |
| F12, F13 | Blade fuse 10 A | Arm 1, arm 2 branches | ATO | 32 V | 10 A | - | 2 | Existing (V1 kit) | Estimate |
| F21, F22 | Blade fuse 3 A | Hub 1, hub 2 | ATO | 32 V | 3 A | - | 2 | Proposed (to buy) | Placeholder |
| F23 | Blade fuse 2 A | 5 V electronics | ATO | 32 V | 2 A | - | 1 | Proposed (to buy) | Placeholder |
| F3 | Fuse 5 A + inline holder | Jetson | ATO | 32 V | 5 A | - | 1 | Fuse existing; holder new | Value verified (V1) |
| F4 | Fuse 10 A + inline holder | Buck input | ATO | 32 V | 10 A | - | 1 | Fuse existing; holder new | Value verified (V1) |
| F5 | Fuse 2 A + inline holder | E-stop loop | not selected | 32 V | 2 A | - | 1 | Proposed | Placeholder |
| U4 | Buck converter 5 V | 5 V rail | TOBSUN EA75-5V | in 8-40 V, out 5 V | 15 A | 75 W | 1 | Existing (V1) | Verified (V1, vendor range) |
| S1 | E-stop mushroom 22 mm, 1 NC | Emergency stop | not selected | 12 V control | < 1 A | - | 1 | Proposed | Not verified |
| SW2 | Pushbutton, momentary NO | START / re-arm | not selected | 12 V control | < 1 A | - | 1 | Proposed | Not verified |
| D1 | Diode | Coil suppression | 1N4007 | 12 V | 1 A | - | 1 | Proposed (V1 parts list) | Not verified |
| - | Negative bus bar | POWER_GND star point | not selected | 12 V | >= 60 A | - | 1 | Proposed | Not verified |
| U20 | Jetson Orin Nano Super Developer Kit 8 GB | Main computer | NVIDIA | 9-20 V | 3.0 A design at 12 V | 3.8 A | 1 | Existing (V1) | Verified (V1 records) |
| U30, U41, U42 | Bus Servo Adapter (A), CH343 | Servo bus drivers | Waveshare (per V1 'most likely') | 9-12.6 V | per branch | - | 3 | Existing (V1) | USB ID verified |
| M31-M34 | Bus servo ST3215-C018 | Mecanum wheel drive | Feetech / Waveshare | 12 V (max 12.6 V) | 1.5 A design each | 2.7 A stall each | 4 | Existing (V1) | Verified (V1 measured) |
| M41, M42 | Bus servo STS3215-C018, 12 V, 30 kg.cm, 1:345 | Arm joints, 6 per arm | Feetech | 12 V | about 0.5 A each (estimate) | 2.7 A stall each | 12 | Proposed (new) | Part exists (vendor); fit on this robot not verified |
| U50 | USB 3 hub, VIA VL815 | USB data hub | model not recorded | TBD | TBD | - | 1 | Existing (V1) | Blocked |
| U54 | Second USB hub | USB data hub | not selected | TBD | TBD | - | 1 | Proposed | Blocked |
| J5 | 5 V aux terminal | 5 V control electronics feed | not selected | 5 V | 2 A | - | 1 | Proposed | Not verified |
| U51, U52, U53 | Gemini 335, wrist webcam, RPLIDAR C1 | Sensors | Orbbec, Suyin, Slamtec | 5 V USB | 0.9 / 0.5 / 0.23 A | - | 3 | Existing (V1) | Verified (V1 measured) |
