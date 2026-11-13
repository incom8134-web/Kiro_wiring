# Power budget and runtime: 12 V 45 Ah EV battery design (Rev A)

Status: **Calculated**, on a battery whose chemistry is **Blocked**. Loads come from the V1 Rev F records. The 12 V arm
figures are estimates because those servos are not fitted yet.

## 1. Loads

| Load | Rail | Typical | Design continuous | Peak | Basis |
|---|---|---|---|---|---|
| Jetson Orin Nano Super incl. its USB loads | battery, unswitched | 25 W | 36 W | 45 W | V1 record |
| Wheels, 4 x ST3215-C018 | regulated 12 V | 1.2 A (14 W) | 6.0 A (72 W) | 10.8 A (130 W), all stalled | V1 measured, vendor stall |
| Arm, 6 x STS3215-C018 12 V, each arm | regulated 12 V | 0.6 A (7 W) | 3 A (36 W) | 8 A (96 W) | **Estimate.** V1 follower power at 5 V with margin; peak is the fuse-limited value |
| 5 V rail: hubs, lidar, 5 V electronics | 5 V via EA75-5V | 10 W | 10 W | 10 W | assumption from the 2026-11-11 draft |
| K1 coil | battery, unswitched | 6 W | 6 W | 6 W | assumption until K1 is selected |

Conversion efficiencies (assumptions): 12 V regulator 92%, EA75-5V 90%.

## 2. Battery current

| Scenario | Power at the battery | Current at 12.0 V | Current at 10.5 V |
|---|---|---|---|
| 1. Idle robot (K1 open, Jetson typical) | 36 W | 3.0 A | 3.4 A |
| 2. Jetson and electronics active, armed, no motion | 64 W | 5.3 A | 6.1 A |
| 3. Two arms operating | 134 W | 11.2 A | 12.8 A |
| 4. Robot driving, arms holding | 147 W | 12.3 A | 14.0 A |
| 5. Typical combined operation | 73 W | 6.1 A | 7.0 A |
| 6. High load (wheels stalled, both arms at design) | 281 W | 23.4 A | 26.8 A |
| Worst case, everything at peak together | 412 W | 34.3 A | 39.2 A |

The preliminary 40 A main fuse covers the high-load case. The worst case is close to 40 A at low battery voltage; it
needs both arms at their fuse limit while all four wheels are stalled.

## 3. Nominal and usable energy

Nominal energy = nominal voltage x capacity. It is not the usable energy.

| Chemistry | Nominal voltage | Nominal energy | Usable share (assumption) | Usable energy |
|---|---|---|---|---|
| Lead-acid (AGM / gel) | 12.0 V | 540 Wh | 50% | 270 Wh |
| LiFePO4 4S | 12.8 V | 576 Wh | 80% | 461 Wh |
| Li-ion 3S | 11.1 V | 500 Wh | 80% | 400 Wh |

For the "12 V x 45 Ah = 540 Wh" figure of the brief, the usable part is 270 Wh if the battery is lead-acid.

## 4. Runtime estimates

| Scenario | Power | Lead-acid (AGM / gel) | LiFePO4 4S | Li-ion 3S |
|---|---|---|---|---|
| 1. Idle robot (K1 open, Jetson typical) | 36 W | 7.5 h | 12.8 h | 11.1 h |
| 2. Jetson and electronics active, armed, no motion | 64 W | 4.2 h | 7.3 h | 6.3 h |
| 3. Two arms operating | 134 W | 2.0 h | 3.4 h | 3.0 h |
| 4. Robot driving, arms holding | 147 W | 1.8 h | 3.1 h | 2.7 h |
| 5. Typical combined operation | 73 W | 3.7 h | 6.3 h | 5.4 h |
| 6. High load (wheels stalled, both arms at design) | 281 W | 1.0 h | 1.6 h | 1.4 h |

Assumptions: usable shares as above; converter losses included in the power column; no ageing or cold derating;
lead-acid loses further capacity at high current (Peukert effect), so its high-load figures are optimistic.

## 5. Open inputs

Battery chemistry and BMS current limit, measured 12 V arm current, K1 coil current, hub power.
