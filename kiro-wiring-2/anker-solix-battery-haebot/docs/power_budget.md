# Power budget and runtime: Anker SOLIX C300 DC design (Rev C)

[English](power_budget.md) | [한국어](power_budget.ko.md)

Load figures are the V1 Rev F records (`kiro-wiring/docs/power_system_design.md`). Nothing in this file was measured on the Anker station.
The 12 V on USB-C2 is the builder's measurement. The current that port will hold was not measured.

**Status: Calculated from V1 loads on the as-built ports. AS BUILT per builder report, not independently measured.**

## 1. Loads at each station port

There is no buck in this revision, so the port sees the load current directly.

| Branch | Port | Load (typ / design / peak) | At the port | Usual port ceiling | Result |
|---|---|---|---|---|---|
| D wheels | USB-C2, with the Jetson | 1.2 / 6.0 / 10.8 A at 12 V | 14.4 / 72 / 130 W | see below | shares the port |
| E Jetson | same USB-C2 | 25 / 36 / 45 W (2.1 / 3.0 / 3.8 A) | included above | see below | stays on after E-stop |
| K1 coil | same USB-C2, from DRIVE_12V | about 3 W (0.25 A), assumption | included when K1 is closed | see below | AS BUILT, coil power not measured |
| C arm 2 | USB-C1, 5 V PD | 1.5 / 5.0 / 8.0 A at 5 V | 7.5 / 25 / 40 W | 3 A, 15 W | typical fits; design and burst do not |
| B arm 1 | USB-A1 | 0.25 / 0.3 / 0.6 A at 5 V | 1.3 / 1.5 / 3.0 W | 2.4 A, 12 W | OK. Not E-stop switched |
| A hub 1 | USB-A2 | about 10 W if the input is 5 V | unknown | 2.4 A, inside the 20 W USB-A group | BLOCKED |
| Hub 2 | none | - | - | - | BLOCKED |

USB-C2 current, wheels + Jetson, coil not included: **3.3 A typical, 9.0 A design, 14.6 A with all four wheels stalled.**
With the 3 W coil assumption: **3.5 A typical, 9.3 A design.** That is the pair of numbers on the schematic.

A 12 V USB-C contract, on sources that offer one, is commonly **3 A / 36 W**. The A1726 manual lists no 12 V profile, so 36 W is not a published Anker rating. It is the usual USB-C ceiling the warnings use. 3.5 A typical and 9.3 A design are both above it.

USB-C1 at 5 V is 3 A in the manual. Arm 2 typical (1.5 A) fits. The 5 A design and the 8 A burst do not.

USB-A1 + USB-A2 + USB-C4 share 20 W. USB-C4 is unused. Arm 1 is about 1.5 W. A 5 V hub at the full 2.4 A would be 12 W, and 1.5 + 12 = 13.5 W of 20 W. That sum is only valid after the hub input voltage is known.

## 2. Usable energy

- Nominal: 288 Wh (Anker specification).
- Usable at the DC ports, assumed: 288 Wh x 0.85 = **245 Wh**. Anker does not publish the factor. It stays an assumption until one full discharge is measured.

## 3. Runtime estimates

Runtimes use 245 Wh. They count the power the robot asks for, then say whether the ports can deliver it.

| Scenario | Power asked | Runtime if delivered | Ports |
|---|---|---|---|
| 1. K1 open, Jetson typical, hub not counted | 25 W | 9.8 h | Jetson alone is inside 36 W |
| 2. Same, plus a 10 W hub assumption | 35 W | 7.0 h | Hub is BLOCKED |
| 3. Typical combined: wheels typical, both arms typical, Jetson typical, coil, hub 10 W | 61 W | 4.0 h | USB-C2 is already about 3.5 A. Expect sag |
| 4. Teleop, not driving, arm 2 held at the 3 A port limit | 55 W | 4.5 h | Arm 2 cannot reach its 25 W design |
| 5. Every branch at design continuous | 148 W | 1.7 h arithmetic | Not deliverable. USB-C2 wants about 111 W, USB-C1 wants 25 W |

Scenario 3 sum: wheels 14.4 W + Jetson 25 W + arm 2 7.5 W + arm 1 1.3 W + coil 3 W + hub 10 W = 61 W.
Scenario 5 sum: wheels 72 W + Jetson 36 W + coil 3 W + arm 2 25 W + arm 1 1.5 W + hub 10 W = 148 W.

No converter-efficiency factor is applied. Rev B had buck losses and a different port map, so its 3.9 h / 1.6 h figures do not carry over.

## 4. What the numbers mean

1. One USB-C port feeds the wheels and the Jetson. At a usual 3 A / 36 W ceiling the rail is expected to sag or cut out when the robot drives. A Jetson brown-out reboots the computer. The computer is on the same port as the wheels, and it is not dropped by the E-stop, so a sag takes the computer with it.
2. Arm 2 is flagged. The follower wants 5 A continuous and 8 A burst. The 5 V PD source gives 3 A.
3. Arm 1 is inside the USB-A rating and is not opened by the E-stop.
4. Wheel servos must stay at or below 12.6 V. The trigger is set to the 12 V the builder measured. Do not trim it up.
