# Bill of materials: EV battery design (Rev B, 2026-11-26)

The [CSV](HAEBOT_EV_BOM.csv) is the full parts table. Selection does not mean hardware verification. K1 is the user-photographed 500A DC12V contactor; S1 is one mechanically latching NC E-stop; U6 is the selected Matek module. SW2 and the auxiliary holding loop are removed.

| Ref | Component | Model | Voltage | Status | Verification |
|---|---|---|---|---|---|
| BT1 | Battery 12 V 45 Ah | not identified | 12 V nominal | Existing (user brief) | Blocked |
| J2 | Charger inlet + matching charger | not identified | per chemistry | Blocked | Blocked |
| F1 | Main fuse 40 A + holder | ANL or MIDI type, not selected | 32 V or more | Proposed | Calculated |
| F2 | Charge fuse 15 A | not selected | 32 V | Proposed | Placeholder |
| SW1 | Battery disconnect switch | not selected | 12 V DC | Proposed | Not verified |
| K1 | DC contactor (main NO + coil; no aux loop) | User photo: label 500A DC12V; exact MPN unknown | 12 V coil label; full operating envelope TBD | User-selected photographed hardware | Not verified |
| U3 | 12 V regulator (buck-boost) | not selected | in 9-16 V, out 12.0 V | Proposed, conditional | Not verified |
| FB1 | 4-way blade fuse box | Dorhea 4-way (V1) | 12 V | Existing (V1) | Verified part |
| FB2 | 4-way blade fuse box | Dorhea 4-way (V1) | 5 V | Existing (V1) | Verified part |
| F11 | Blade fuse 15 A | ATO | 32 V | Existing (V1 kit) | Value verified (V1) |
| F12, F13 | Blade fuse 10 A | ATO | 32 V | Existing (V1 kit) | Estimate |
| F21, F22 | Blade fuse 3 A | ATO | 32 V | Proposed (to buy) | Placeholder |
| F23 | Blade fuse 2 A | ATO | 32 V | Proposed (to buy) | Placeholder |
| F3 | Fuse 5 A + inline holder | ATO | 32 V | Fuse existing; holder new | Value verified (V1) |
| F4 | Fuse 10 A + inline holder | ATO | 32 V | Fuse existing; holder new | Value verified (V1) |
| F5 | Control fuse + inline holder (2 A provisional) | not selected | 32 V | Proposed | Placeholder |
| U4 | Buck converter 5 V | TOBSUN EA75-5V | in 8-40 V, out 5 V | Existing (V1) | Verified (V1, vendor range) |
| S1 | Latching E-stop mushroom; positive-opening NC | not selected | 12 V control | Proposed | Not verified |
| D1 | Manufacturer-approved coil suppressor (TBD) | TBD; former 1N4007 is unverified | 12 V | Unverified placeholder | Not verified |
| - | Negative bus bar | not selected | 12 V | Proposed | Not verified |
| U20 | Jetson Orin Nano Super Developer Kit 8 GB | NVIDIA | 9-20 V | Existing (V1) | Verified (V1 records) |
| U30, U41, U42 | Bus Servo Adapter (A), CH343 | Waveshare (per V1 'most likely') | 9-12.6 V | Existing (V1) | USB ID verified |
| M31-M34 | Bus servo ST3215-C018 | Feetech / Waveshare | 12 V (max 12.6 V) | Existing (V1) | Verified (V1 measured) |
| M41, M42 | Bus servo STS3215-C018, 12 V, 30 kg.cm, 1:345 | Feetech | 12 V | Both arms confirmed new 12 V; exact MPN proposed | Voltage choice user-confirmed; MPN/fit/current unverified |
| U50 | USB 3 hub, VIA VL815 | model not recorded | TBD | Existing (V1) | Blocked |
| U54 | Second USB hub | not selected | TBD | Proposed | Blocked |
| J5 | 5 V aux terminal | not selected | 5 V | Proposed | Not verified |
| U51, U52, U53 | Gemini 335, wrist webcam, RPLIDAR C1 | Orbbec, Suyin, Slamtec | 5 V USB | Existing (V1) | Verified (V1 measured) |
| U6 | I2C battery voltage/current monitor | Matek I2C-INA-BM | sense 0-85 V; electronics 4-9 V (use 5 V) | User-selected; not hardware-tested | Manufacturer specifications; Jetson integration unverified |
