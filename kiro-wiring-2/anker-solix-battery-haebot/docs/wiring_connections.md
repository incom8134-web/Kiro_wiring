# Wiring connection table: Anker design (Rev A)

Matches `kicad/HAEBOT_ANKER.kicad_sch` and `exports/HAEBOT_ANKER_NETLIST.net`. Reference designators are the ones on
the schematic. Power leads (W-) and USB data links (U-) are listed separately: a USB data cable is never the power feed
of a servo rail.

| ID | From | To | Net / signal | Voltage | Current | Cable and connector | Status |
|---|---|---|---|---|---|---|---|
| W-D1 | PS1 USB-C2 | PD2 input | USB-C PD 20 V | 20 V | 5 A max | USB-C to USB-C, 5 A e-marked | Proposed |
| W-D2 | PD2 out | U3 in | WHEEL_20V | 20 V | 4 A design | 14 AWG pair, screw terminals | Proposed |
| W-D3 | U3 out+ | F1 -> K1 pole 1 -> U30 VIN+ | DRIVE_12V / WHEEL_SW | 12.0 V | 6 A design, 10.8 A stall | 14 AWG, ferrules, screw terminal on U30 | Proposed |
| W-D4 | U30 VIN- | U3 out- | GND_C2 | 0 V | as W-D3 | 14 AWG | Proposed |
| W-D5 | U30 port 1 | M31 (FR ID7) -> M33 (RR ID9) | servo bus | 12 V | <= 2 servos per port | Molex 5264 3-pin, 22 AWG | Verified (V1) |
| W-D6 | U30 port 2 | M32 (FL ID8) -> M34 (RL ID10) | servo bus | 12 V | <= 2 servos per port | Molex 5264 3-pin, 22 AWG | Verified (V1) |
| W-C1 | PS1 USB-C1 | PD1 input | USB-C PD 20 V | 20 V | 1.5 A at 30 W | USB-C to USB-C | Proposed |
| W-C2 | PD1 out | U4 in | ARM2_20V | 20 V | 1.5 A | 18 AWG pair | Proposed |
| W-C3 | U4 out+ | F2 -> K1 pole 2 -> U42 VIN+ | ARM2_5V / ARM2_SW | 5.0-5.2 V | 5 A design, 8 A burst | 14 AWG | Proposed |
| W-C4 | U42 VIN- | U4 out- | return | 0 V | as W-C3 | 14 AWG | Proposed |
| W-C5 | U42 port 1 | M42 arm 2 chain | servo bus | 5 V | arm current | Molex 5264 3-pin | Verified (V1) |
| W-K1 | DRIVE_12V | F3 -> S1 -> SW2 || K1 13-14 -> K1 A1 | control loop | 12 V | < 0.5 A | 20 AWG | Proposed |
| W-K2 | K1 A2 | GND_C2 | control return | 0 V | < 0.5 A | 20 AWG | Proposed |
| W-B1 | PS1 USB-C4 | J41 -> F4 -> U41 VIN+ / VIN- | ARM1_5V | 5 V | 0.3 A design, 3 A max | USB-C 5 V lead with 5.1 k CC resistors, 20 AWG | Proposed |
| W-B2 | U41 port 1 | M41 arm 1 chain | servo bus | 5 V | 0.6 A peak | Molex 5264 3-pin | Verified (V1) |
| W-E1 | PS1 car socket | P1 -> F5 -> U20 DC jack | JETSON_12V | 10.8-14 V | 3.0 A design, 3.8 A peak | car plug to 5.5 x 2.5 mm barrel, centre +, 18 AWG | Proposed lead; jack verified (V1) |
| W-A1 | PS1 USB-A1 | W1 -> U50 DC in | HUB1_5V | 5 V | <= 2.4 A | USB-A to DC barrel (size TBD) | Blocked |
| W-A2 | PS1 USB-A2 | W2 -> U54 DC in | HUB2_5V | 5 V | <= 2.4 A | USB-A to DC barrel (size TBD) | Blocked |
| U-1 | U20 USB-A1 | U51 Orbbec Gemini 335 | USB 3 data + bus power | 5 V | 0.9 A max | bundled cable, never via a hub | Verified (V1) |
| U-2 | U20 USB-A2 | U52 wrist webcam | USB 2 data + bus power | 5 V | 0.5 A | direct | Verified (V1) |
| U-3 | U20 USB-A3 | U50 hub 1 upstream | USB data | - | - | USB 3 cable | Verified (V1) |
| U-4 | U20 USB-A4 | U54 hub 2 upstream | USB data | - | - | USB cable | Proposed |
| U-5 | U50 DS1-DS3 | U30, U41, U42 USB-C | USB data (logic power only) | 5 V | small | USB-A to USB-C | Verified (V1) |
| U-6 | U50 DS4 | U53 RPLIDAR C1 adapter | USB data + 5 V | 5 V | 0.23 A typ | shielded USB, away from 12 V | Verified (V1) |

Rules carried over from V1:

- Feed every Bus Servo Adapter through its **screw terminal**, not the barrel jack (5 A class part).
- Wheel servos stay on two chains so no Molex 5264 contact (about 3 A) carries more than two servos.
- Ferrules on every screw terminal. Strain relief on every lead at both ends.
- Label the follower rail "5 V ONLY". The follower servos trip above 8.0 V.
