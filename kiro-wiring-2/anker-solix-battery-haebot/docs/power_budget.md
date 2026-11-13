# Power budget and runtime: Anker SOLIX C300 DC design (Rev A)

All load figures come from the V1 Rev F records (`kiro-wiring/docs/power_system_design.md`). Nothing here was measured on
the Anker station. Status of this document: **Calculated**.

## 1. Loads at each station port

| Branch | Port | Load side (typ / design / peak) | Conversion | At the port (typ / design / peak) | Port limit in this mix | Result |
|---|---|---|---|---|---|---|
| D wheels | USB-C2 | 1.2 / 6.0 / 10.8 A at 12 V | buck 92% (assumption) | 16 / 78 / 141 W | 100 W | design OK; all four wheels stalled exceeds the port |
| C arm 2 (follower) | USB-C1 | 1.5 / 5.0 / 8.0 A at 5 V | EA75-5V 90% (V1 doc) | 8 / 28 / 44 W | 30 W | design marginal (93 % of limit); 8 A burst exceeds the port |
| B arm 1 (leader) | USB-C4 | 0.25 / 0.3 / 0.6 A at 5 V | none | 1.2 / 1.5 / 3.0 W | 15 W, inside the shared 20 W | OK |
| E Jetson | Car socket | 25 / 36 / 45 W | none | 25 / 36 / 45 W | 120 W (10 A) | OK |
| A hubs | USB-A1, USB-A2 | about 10 W total (assumption) | none | 10 W | 12 W each, 20 W shared with USB-C4 | Blocked: hub input voltage unknown |
| E-stop coil | from DRIVE_12V | about 3 W (assumption) | buck | 3.3 W | inside USB-C2 | Proposed |

Port limits are the 4-port case of the Anker A1726 manual: USB-C1 + USB-C2/C3 + (USB-A1, USB-A2, USB-C4) + car socket
= 30 W + 100 W + 20 W + 120 W. See `power_distribution_and_protection.md` for the full table.

## 2. Usable energy

- Nominal: 288 Wh (Anker specification).
- Usable at the DC ports: 288 Wh x 0.85 = **245 Wh**. The 0.85 factor is an assumption covering the station's
  internal conversion and cut-off. Anker does not publish this figure. Measure one full discharge to replace it.

## 3. Runtime estimates

| Scenario | Power at the station | Estimated runtime |
|---|---|---|
| 1. Idle robot (K1 open, Jetson typical) | 38 W | 6.4 h |
| 2. Jetson and electronics active (K1 open) | 50 W | 4.9 h |
| 3. Two arms operating (teleoperation) | 81 W | 3.0 h |
| 4. Robot driving, arms holding | 137 W | 1.8 h |
| 5. Typical combined operation | 63 W | 3.9 h |
| 6. High load (every branch at design continuous) | 157 W | 1.6 h |

Assumptions: converter efficiencies as in section 1; 2 W allowance for converter no-load losses in scenarios 1 and 2;
no ageing or cold-temperature derating. The total stays under the 300 W station limit in every scenario.

## 4. What the numbers mean

1. The wheel branch works for normal driving but the station cannot hold all four wheels in stall. The buck or the
   port will current-limit. Expect the drive rail to sag in that case.
2. The follower arm fits only at its design-continuous load. Fast moves with a payload can exceed 30 W at USB-C1.
3. A better port mix exists and needs one module less. See "Recommended alternative" in
   `power_distribution_and_protection.md`.
