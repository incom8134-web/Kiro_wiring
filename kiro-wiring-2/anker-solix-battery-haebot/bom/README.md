# Bill of materials: Anker design (Rev B)

Full table with every column: [`HAEBOT_ANKER_BOM.csv`](HAEBOT_ANKER_BOM.csv). "not selected" means no part number has
been chosen. No part number in this file is invented.

| Ref | Component | Function | Manufacturer / model | Operating voltage | Rated current | Peak current | Qty | Status | Verification |
|---|---|---|---|---|---|---|---|---|---|
| PS1 | Anker SOLIX C300 DC | Power source | Anker A1726 | 5-28 V USB-C, 5 V USB-A, 12 V socket | see port table | 300 W total | 1 | Existing (user-reported on hand) | Verified (manual) |
| PD1 | USB-C PD trigger, fixed 20 V | Arm 2 PD sink | not selected | 20 V out | >= 3 A | - | 1 | Proposed | Not verified |
| PD2 | USB-C PD trigger, fixed 20 V | Wheel PD sink | not selected | 20 V out | >= 5 A | - | 1 | Proposed | Not verified |
| U3 | Buck converter 20 V -> 12.0 V | Wheel 12 V regulator | not selected | in 20 V, out 12.0 V | >= 12 A | current-limited | 1 | Proposed | Not verified |
| U4 | Buck converter 5 V | Arm 2 5 V rail | TOBSUN EA75-5V | in 8-40 V, out 5 V | 15 A | 75 W | 1 | Existing (V1) | Verified part (V1), 20 V input per vendor range |
| K1 | Relay / contactor, 3 NO power poles + 1 NO aux | E-stop power switch | not selected | 12 V DC coil | >= 20 A per pole | - | 1 | Proposed | Not verified |
| S1 | E-stop mushroom, 22 mm, 1 NC, twist release | Emergency stop | not selected | 12 V control | < 1 A | - | 1 | Proposed (V1 planned part) | Not verified |
| SW2 | Pushbutton, momentary NO | START / re-arm | not selected | 12 V control | < 1 A | - | 1 | Proposed | Not verified |
| D1 | Diode | K1 coil suppression | 1N4007 | 12 V | 1 A | - | 1 | Proposed (V1 parts list) | Not verified |
| F1, F2 | Blade fuse 15 A + inline holder | Wheel and arm 2 branch fuses | ATO | 32 V | 15 A | - | 2 | Fuses existing (V1 kit); holders new | Value verified (V1) |
| F3 | Fuse 1 A + inline holder | E-stop loop fuse | not selected | 32 V | 1 A | - | 1 | Proposed | Calculated |
| F4 | Blade fuse 3 A + inline holder | Arm 1 fuse | ATO | 32 V | 3 A | - | 1 | Proposed (V1 lists 2-3 A to buy) | Calculated |
| F5 | Fuse 5 A + inline holder | Jetson fuse | ATO | 32 V | 5 A | - | 1 | Fuse existing (V1 kit); holder new | Value verified (V1) |
| J41 | USB-C 5 V power lead to screw terminal | Arm 1 supply lead | not selected | 5 V | 3 A | - | 1 | Proposed | Not verified |
| P1 | Car plug to 5.5 x 2.5 mm barrel lead | Jetson supply lead | not selected | 12 V | 10 A plug | - | 1 | Proposed | Not verified |
| W1, W2 | USB-A to DC barrel lead | Hub power leads | not selected | 5 V | 2.4 A | - | 2 | Blocked | Not verified |
| U20 | Jetson Orin Nano Super Developer Kit 8 GB | Main computer | NVIDIA | 9-20 V DC jack | 3.0 A design at 12 V | 3.8 A | 1 | Existing (V1) | Verified (V1 records) |
| U30, U41, U42 | Bus Servo Adapter (A), CH343 | Servo bus drivers | Waveshare (model per V1 'most likely') | wheels 12 V; arms 5 V | per branch | - | 3 | Existing (V1) | USB ID verified; silkscreen photo open |
| M31-M34 | Bus servo ST3215-C018 | Mecanum wheel drive | Feetech / Waveshare | 12 V (max 12.6 V, trip 14.0 V) | 1.5 A design each | 2.7 A stall each | 4 | Existing (V1) | Verified (V1 measured) |
| M41 | SO-101 leader arm, 6 x STS3215 | Arm 1 | Feetech | 5 V | 0.3 A | 0.6 A | 1 | Existing (V1) | Verified (V1 doc) |
| M42 | SO-101 follower arm, 6 x STS3215 (7.4 V type) | Arm 2 | Feetech | 5 V (trip 8.0 V) | 5 A design | 8 A burst | 1 | Existing (V1) | Verified (V1 measured) |
| U50 | USB 3 hub, VIA VL815, self-powered | USB data hub | model not recorded | TBD | TBD | - | 1 | Existing (V1) | Blocked |
| U54 | Second USB hub | USB data hub | not selected | TBD | TBD | - | 1 | Proposed | Blocked |
| U51 | Orbbec Gemini 335 | Head camera | Orbbec | 5 V USB | 0.9 A max | - | 1 | Existing (V1) | Verified (V1 measured) |
| U52 | Wrist webcam (Suyin 1e45:8022) | Wrist camera | retail model unknown | 5 V USB | 0.5 A | - | 1 | Existing (V1) | Verified (V1 measured) |
| U53 | RPLIDAR C1 + CP2102N adapter | 2D lidar | Slamtec | 5 V USB | 0.23 A typ | - | 1 | Existing (V1) | Verified (V1 measured) |
| C1 | Electrolytic capacitor 1000-2200 uF / 25 V | Wheel rail bulk capacitor | not selected | 12 V | - | - | 1 | Proposed | Not verified |
