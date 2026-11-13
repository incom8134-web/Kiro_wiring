# Moving the two arms to 12 V servos (Proposed)

## What is fitted today (V1 records)

- Follower arms: 6 x STS3215 each, **7.4 V type**, `Max_Voltage_Limit` 8.0 V, run on 5 V.
- Leader arms: 6 x STS3215 each, torque off, mixed voltage limits.
- These servos must never be connected to the 12 V rail.

## Proposed replacement

**Feetech STS3215-C018, 12 V, 30 kg.cm, gear ratio 1:345, TTL serial bus.** It is the servo sold for the 12 V
SO-ARM101 follower, and it is the same model already driving the HAEBOT wheels.

| Question | Answer | Status |
|---|---|---|
| Does the SO-101 structure accept it? | Same STS3215 housing and horn pattern as the 7.4 V type | Expected, not checked on this robot |
| Brackets or printed parts to change? | None expected | Check one joint before ordering twelve servos |
| Does the controller support it? | Yes. Bus Servo Adapter (A) is specified for 9-12.6 V | Verified (vendor, V1 wheel board) |
| Communication | Unchanged: TTL half-duplex serial, 1 Mbps, Molex 5264 | Verified for the C018 on the wheels |
| Supply voltage | 12.0 V, never above 12.6 V. Needs the regulated rail (U3) for lead-acid and LiFePO4 | Verified limit |
| Software | Servo IDs 1-6 must be written to each new servo; redo LeRobot calibration for both arms | Required |
| Control settings | Check `Max_Voltage_Limit`, torque limit and P/I/D. More torque at 12 V: start with the gripper limited as today | Required |
| Leader arms | A leader is moved by hand with torque off and uses different gear ratios. It does not need 12 V servos | Decide which two arms the brief means |
| Current | Stall 2.7 A per servo. One arm is one six-servo chain on one Molex contact (about 3 A rating) | Measure before fixing F12 / F13 |

Mixing rule: once an arm adapter is on fuse box 1 (12 V), every servo on that bus must be the 12 V type.
