# Shared hardware evidence

What is known about the HAEBOT / KIRO hardware and where each fact comes from. Both V2 designs use this list.
Change an electrical connection only after checking it here.

| Item | Fact | Source |
|---|---|---|
| Computer | NVIDIA Jetson Orin Nano Super Developer Kit, 8 GB. DC jack 5.5 x 2.5 mm, centre positive, 9-20 V. Bundled adapter 19 V | V1 records; V1 runs it from 12 V |
| Jetson power | 25 W typical, 36 W design, 45 W peak including its USB loads | V1 `power_system_design.md` |
| Wheel "motor driver" | One Bus Servo Adapter (A) type board, USB chip CH343 (1a86:55d3). 9-12.6 V. Feed through the screw terminal | V1 records (USB ID measured; board name "most likely") |
| Wheel motors | 4 x Feetech ST3215-C018 bus servos, IDs FR 7, FL 8, RR 9, RL 10. Max 12.6 V, trip 14.0 V, stall 2.7 A each | V1 measured, vendor |
| Wheel wiring | Two chains: port 1 -> 7 -> 9, port 2 -> 8 -> 10 | V1 records |
| Follower arm servos | 6 x STS3215, 7.4 V type, `Max_Voltage_Limit` 8.0 V, run on 5 V (5.2-5.3 V measured). 5 A design, 8 A burst | V1 measured and estimate |
| Leader arm servos | 6 x STS3215, torque off, about 0.3 A | V1 estimate |
| Servo connector | Molex 5264 3-pin, GND / VCC / SIG, about 3 A per contact | V1 records |
| 5 V converter | TOBSUN EA75-5V, 8-40 V in, 5 V 15 A, 75 W | V1 on hand, vendor listing |
| Fuse boxes | 2 x Dorhea 4-way blade, single live input, no negative bus | V1 on hand |
| USB hub | VIA VL815 USB 3 hub, self-powered. **Input voltage, current and plug not recorded** | V1 records |
| Cameras | Orbbec Gemini 335 (0.9 A max) and a Suyin webcam (0.5 A), both directly on Jetson ports | V1 measured |
| Lidar | Slamtec RPLIDAR C1 with CP2102N adapter, 5 V 0.23 A, on the hub | V1 measured |
| Anker station | SOLIX C300 DC, A1726, 288 Wh LiFePO4, 300 W. No 12 V USB-C profile. 5 V USB-C limited to 3 A | Anker manual |
| EV battery | "12 V 45 Ah". **Chemistry, BMS, charger and connector unknown** | user brief |
| 12 V arm servo | Feetech STS3215-C018, 12 V, 30 kg.cm, used in 12 V SO-ARM101 followers | vendor pages, Waveshare wiki |

V1 source documents: [`../kiro-wiring/docs/power_system_design.md`](../kiro-wiring/docs/power_system_design.md),
[`../kiro-wiring/docs/parts_list.md`](../kiro-wiring/docs/parts_list.md).

## Still needed from the hardware

1. Photo of the EV battery label and the charger label.
2. Photo of the USB hub label and its power adapter label.
3. Photo of a servo adapter board (silkscreen).
4. Which two arms the V2 robot carries (leader + follower, or two followers).
5. Whether a second USB hub is fitted.
