# Wiring connection table: Anker design (Rev C)

[English](wiring_connections.md) | [한국어](wiring_connections.ko.md)

Matches `kicad/HAEBOT_ANKER.kicad_sch` and `exports/HAEBOT_ANKER_NETLIST.net` exported with kicad-cli 7.0.11 on 2026-11-16.
Reference designators are the ones on the schematic. Power leads and USB data links are separate: a USB data cable is never the power feed of a servo rail.

**AS BUILT per builder report. Not independently measured.** Wire gauge was not in the builder report. Gauges below are the V1 sizes for the same current, kept so a later repair uses the same class of wire. Where the builder did not describe the connector, the cell says so.

| ID | From | To | Net / signal | Voltage | Current | Cable and connector | Status |
|---|---|---|---|---|---|---|---|
| W-D1 | PS1 USB-C2 | P02 VBUS / GND | USB-C | 12 V measured | not measured | USB-C to USB-C cable, as fitted. E-mark not reported | AS BUILT |
| W-D2 | P02 OUT+ | FB1 input, then F1 and F5 | DRIVE_12V | 12 V | see power budget | pair back to P02 OUT-. Gauge not reported | AS BUILT |
| W-D3 | F1 | K1 pole 1 (pins 1-2) -> U30 VIN+ | WHEEL_F / WHEEL_SW | 12 V | 6 A design, 10.8 A stall | 14 AWG class (V1), ferrules, screw terminal on U30 | AS BUILT path. Gauge from V1 |
| W-D4 | U30 VIN- | P02 OUT- | GND_C2 | 0 V | as W-D3 | return pair. FB1 has no negative bus | AS BUILT |
| W-D5 | U30 port 1 | M31 (FR ID7) -> M33 (RR ID9) | servo bus | 12 V | <= 2 servos per port | Molex 5264 3-pin, GND / VCC / SIG, 22 AWG | Verified (V1) |
| W-D6 | U30 port 2 | M32 (FL ID8) -> M34 (RL ID10) | servo bus | 12 V | <= 2 servos per port | Molex 5264 3-pin | Verified (V1) |
| W-E1 | F5 | U20 DC jack, before K1 | JETSON_12V | 12 V | 3.0 A design, 3.8 A peak | 18 AWG class (V1), 5.5 x 2.5 mm, centre +. Stays on after E-stop | AS BUILT path. Jack verified (V1) |
| W-E2 | U20 DC- | P02 OUT- | GND_C2 | 0 V | as W-E1 | return to P02 OUT- | AS BUILT |
| W-C1 | PS1 USB-C1 | P01 VBUS / GND | USB-C | 5 V | 3 A max | USB-C to USB-C cable | AS BUILT |
| W-C2 | P01 OUT+ | K1 pole 2 (pins 3-4) -> U42 VIN+ | ARM2_5V / ARM2_SW | 5 V | 3 A available; 5 A design, 8 A burst | screw terminal on U42. No buck, no extra fuse | AS BUILT. Over the port limit at design load |
| W-C3 | U42 VIN- | P01 OUT- | GND_C1 | 0 V | as W-C2 | own return | AS BUILT |
| W-C4 | U42 port 1 | M42 arm 2 chain | servo bus | 5 V | arm current | Molex 5264 3-pin | Verified (V1) |
| W-K1 | DRIVE_12V | F3 -> S1 (NC) -> SW2 \|\| K1 aux 13-14 -> K1 A1 | control loop | 12 V | < 0.5 A | 20 AWG class (V1). F3 is drawn 1 A; builder did not state the rating | AS BUILT |
| W-K2 | K1 A2 and D1 anode | GND_C2 | control return | 0 V | < 0.5 A | D1 cathode on A1. Confirm D1 is fitted | Shown on the Rev C schematic |
| W-B1 | PS1 USB-A1 | W3 -> U41 DC jack | ARM1_5V | 5 V | 0.3 A design, 0.6 A peak | USB-A to DC jack lead. No fuse. Not switched by K1 | AS BUILT |
| W-B2 | U41 VIN- | W3 return | GND_A1 | 0 V | as W-B1 | lead return | AS BUILT |
| W-B3 | U41 port 1 | M41 arm 1 chain | servo bus | 5 V | 0.6 A peak | Molex 5264 3-pin | Verified (V1) |
| W-A1 | PS1 USB-A2 | W1 -> U50 DC input | HUB1_5V | 5 V | <= 2.4 A | USB-A to DC barrel. Size and polarity not recorded | BLOCKED |
| W-A2 | - | U54 DC input | none | - | - | no power port assigned | BLOCKED |
| U-1 | U20 USB-A1 | U51 Orbbec Gemini 335 | USB 3 data + bus power | 5 V | 0.9 A max | bundled cable, never via a hub | Verified (V1) |
| U-2 | U20 USB-A2 | U52 wrist webcam | USB 2 data + bus power | 5 V | 0.5 A | direct | Verified (V1) |
| U-3 | U20 USB-A3 | U50 hub 1 upstream | USB_JET_HUB1 | - | - | USB 3 cable | Verified (V1) |
| U-4 | U20 USB-A4 | U54 hub 2 upstream | USB_JET_HUB2 | - | - | USB cable | AS BUILT data path. Power is BLOCKED |
| U-5 | U50 DS1, DS2, DS3 | U30, U41, U42 USB | USB data | 5 V | logic only | USB-A to USB-C. Not the servo power feed | Verified (V1) |
| U-6 | U50 DS4 | U53 RPLIDAR C1 adapter | USB data + 5 V | 5 V | 0.23 A typ | shielded USB, away from the 12 V pair | Verified (V1) |

Not connected, on purpose: PS1 USB-C3, USB-C4, CAR12V+ and CAR12V-.

Rules carried over from V1, with the as-built exception called out:

- Feed the wheel adapter and the arm 2 adapter through the screw terminal. Arm 1 is the exception: the builder plugged a USB-A to DC jack lead into the adapter DC jack. Leader current is about 0.3 A.
- Wheel servos stay on two chains so no Molex 5264 contact carries more than two servos.
- Ferrules on every screw terminal. Strain relief on every lead at both ends.
- Label the arm 2 rail "5 V ONLY". The follower servos trip above 8.0 V. The source cannot raise that rail above 5 V.
- Never join the positive of USB-C2 to any other port positive.
