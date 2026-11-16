# Bill of materials: Anker design (Rev C)

[English](README.md) | [한국어](README.ko.md)

Full table: [`HAEBOT_ANKER_BOM.csv`](HAEBOT_ANKER_BOM.csv).

**AS BUILT per builder report, 2026-11-16. Not independently measured.** "part number not recorded" means the builder fitted a part and did not give a manufacturer part number. No part number in this file is invented.

Removed from the Rev B proposal and not fitted: the 12 V buck, the TOBSUN EA75-5V arm buck, the car-plug lead, the USB-C 5 V lead to arm 1, the second hub power lead, fuses F2 and F4, and the third K1 power pole.

| Ref | Component | Function | Manufacturer / model | Operating voltage | Rated current | Peak | Qty | Status | Verification |
|---|---|---|---|---|---|---|---|---|---|
| PS1 | Anker SOLIX C300 DC | Power source | Anker A1726 | USB-C, USB-A; car socket not used | see port table | 300 W | 1 | AS BUILT | Verified model (manual) |
| P02 | USB-C PD trigger, set to 12 V | Wheels and Jetson | part number not recorded | 12 V out, builder measurement | not measured | - | 1 | AS BUILT | Builder measurement, not a manual profile |
| P01 | USB-C PD trigger, fixed 5 V | Arm 2 | part number not recorded | 5 V out | 3 A max | - | 1 | AS BUILT | AS BUILT. Below the 5 A / 8 A arm load |
| FB1 | Dorhea 4-way fuse box | 12 V distribution | Dorhea (V1) | 12 V | F1 and F5 fitted | - | 1 | AS BUILT | V1 part. Two slots spare |
| F1 | Blade fuse 15 A | Wheels, then K1 | ATO | 32 V | 15 A | - | 1 | AS BUILT | V1 value |
| F5 | Fuse 5 A | Jetson, before K1 | ATO | 32 V | 5 A | - | 1 | AS BUILT | V1 value |
| F3 | Fuse 1 A | E-stop loop | rating not stated | 32 V | 1 A drawn | - | 1 | AS BUILT position | 1 A is calculated. Builder did not state the rating |
| K1 | Contactor, 2 NO poles + aux NO | E-stop | part number not recorded | 12 V coil | wheels, arm 2 | - | 1 | AS BUILT | Third pole not fitted |
| S1 | E-stop, NC | Emergency stop | part number not recorded | 12 V | < 1 A | - | 1 | AS BUILT | AS BUILT |
| SW2 | START, momentary NO | Re-arm | part number not recorded | 12 V | < 1 A | - | 1 | AS BUILT | AS BUILT |
| D1 | Flyback diode | Coil suppression | 1N4007 | 12 V | 1 A | - | 1 | On the Rev C schematic | Confirm it is fitted. Cathode to A1 |
| W3 | USB-A to DC jack lead | Arm 1 | ready-made | 5 V | 2.4 A | - | 1 | AS BUILT | No fuse, not E-stop switched |
| W1 | USB-A to DC barrel lead | Hub 1 | not recorded | 5 V | 2.4 A | - | 1 | BLOCKED | Hub input voltage unknown |
| U20 | Jetson Orin Nano Super 8 GB | Computer | NVIDIA | 9-20 V | 3.0 A design | 3.8 A | 1 | AS BUILT | V1 records. Stays on after E-stop |
| U30 | Bus Servo Adapter (A) | Wheels | Waveshare, per V1 | 12 V | 6 A design | - | 1 | AS BUILT | V1 |
| U42 | Bus Servo Adapter (A) | Arm 2 | Waveshare, per V1 | 5 V | 3 A from the port | - | 1 | AS BUILT | V1 |
| U41 | Bus Servo Adapter (A) | Arm 1 | Waveshare, per V1 | 5 V | 0.6 A peak | - | 1 | AS BUILT | DC jack, as built |
| M31-M34 | ST3215-C018 | Wheels | Feetech / Waveshare | 12 V, max 12.6 V | 1.5 A each | 2.7 A | 4 | AS BUILT | V1 measured |
| M41 | Leader arm, 6 x STS3215 | Arm 1 | Feetech | 5 V | 0.3 A | 0.6 A | 1 | AS BUILT | Torque off |
| M42 | Follower arm, 6 x STS3215 | Arm 2 | Feetech | 5 V, trip 8.0 V | 5 A design | 8 A | 1 | AS BUILT | Source is 3 A |
| U50 | USB hub, VIA VL815 | Hub 1 | model not recorded | TBD | TBD | - | 1 | BLOCKED | Input voltage unknown |
| U54 | USB hub 2 | Hub 2 | not recorded | no port assigned | - | - | 1 | BLOCKED | No power port |
| U51 | Orbbec Gemini 335 | Head camera | Orbbec | 5 V USB | 0.9 A | - | 1 | AS BUILT | V1 measured |
| U52 | Wrist webcam | Wrist camera | unknown retail | 5 V USB | 0.5 A | - | 1 | AS BUILT | V1 measured |
| U53 | RPLIDAR C1 + CP2102N | Lidar | Slamtec | 5 V USB | 0.23 A | - | 1 | AS BUILT | V1 measured |
