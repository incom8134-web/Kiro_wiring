# Verification report: Anker design (Rev A, 2026-11-13)

**Overall status: PROPOSED. This design is not validated.** No part of it has been built or measured.

| Word | Meaning |
|---|---|
| **Verified** | Supported by a datasheet, a manual, or a measurement recorded in this repository |
| **Calculated** | Derived from verified values with stated assumptions |
| **Proposed** | Not bought, not built, not tested |
| **Blocked** | Cannot be finalised until a hardware fact is supplied |


## 1. Checks performed

| Check | Method | Result |
|---|---|---|
| KiCad file validity | `kicad-cli` 7.0.11 loads the schematic and plots it | Pass |
| Net connectivity | KiCad netlist export compared with the intended connection table | Pass after one fix: tee connections were not joined in the first export and were corrected |
| Unconnected pins | netlist review | Only intended ones: USB-C3, second adapter ports, last servo in each chain, hub 2 downstream ports |
| KiCad ERC | not run | **Open.** The CLI available here (7.0.11) has no ERC command. Run ERC in KiCad 8 or newer |
| PDF readability | exported PDF rendered and inspected | Pass: no clipping, no overlapping labels found |
| Source voltage per branch | manual and V1 records | See section 2 |
| Continuous current per branch | calculation in `power_budget.md` | See section 2 |
| Shared output limits | manual power distribution table | Design uses the 4-port row: 30 + 100 + 20 + 120 W |
| Backfeed / cross-connection | schematic review | No positive of one port is joined to another. Negatives join through USB shields (see protection notes) |

## 2. Results by branch

| Item | Status | Evidence or reason |
|---|---|---|
| Station model, capacity, port ratings | Verified | Anker A1726 manual |
| No 12 V USB-C profile, 5 V limited to 3 A | Verified | Anker A1726 manual |
| Jetson DC jack accepts the car-socket voltage | Verified by V1 records | jack 9-20 V; V1 runs it from 12 V. Confirm the carrier is the stock one |
| Wheel servos: 12 V, max 12.6 V, stall 2.7 A | Verified | V1 measured and vendor |
| Follower servos trip above 8.0 V; run on 5 V | Verified | V1 register read and measurement |
| EA75-5V accepts 20 V input | Verified by vendor range | 8-40 V listing; not tested at 20 V |
| Wheel branch within USB-C2 at design load | Calculated | 78 W of 100 W |
| Wheel branch with all four wheels stalled | Calculated: not supported | 141 W against 100 W |
| Arm 2 within USB-C1 at design load | Calculated: marginal | 28 W of 30 W |
| Arm 2 at 8 A burst | Calculated: not supported | 44 W against 30 W |
| Arm 1 on USB-C4 | Calculated | 3 W of 15 W; leader arm only |
| PD triggers, 12 V buck, K1, S1, START, leads | Proposed | no part selected |
| Hub 1 power from USB-A | Blocked | hub input voltage, current and plug are not recorded |
| Hub 2 | Blocked | not in the hardware records |
| Station negatives common internally | Blocked | not published; measure continuity between port grounds with the station off |
| USB-C1 still offers 20 V when capped at 30 W | Blocked | bench test with the trigger and a USB-C meter |
| Usable energy factor 0.85 | Blocked | one measured discharge |

## 3. Requested items that cannot work as written

1. **12 V PD trigger for the wheels.** The station has no 12 V USB-C profile. Rev A uses a 20 V trigger and a 12.0 V buck.
2. **5 V PD trigger for a powered arm.** USB-C gives at most 3 A at 5 V. Rev A uses a 20 V trigger and the existing
   5 V 15 A buck.
3. **Plain USB-C cable for a powered arm.** Same 3 A limit. Branch B is restricted to the leader arm.

## 4. Bench checks before first use

1. Read the hub label and its adapter label (voltage, current, plug size, polarity).
2. With a USB-C meter: trigger voltage on USB-C1 and USB-C2 with all four port groups loaded.
3. Set U3 to 12.0 V and check U4 at 5.0-5.2 V with no servo connected.
4. Check the barrel plug polarity of P1 with a meter before it touches the Jetson.
5. Test the E-stop loop: latch, drop-out on S1, no restart on release, drop-out with one loop wire pulled.
6. Drive on blocks, then on the floor, and log the port power on the station display.

## Sources

- Anker SOLIX C300 DC user manual (A1726), specifications and USB power distribution table:
  https://www.santansolar.com/wp-content/uploads/TEM_A1726_V1_EN_UM_Web_20240913.pdf
- Anker SOLIX C300 DC product page: https://anker.com/products/a17260z1
- Anker SOLIX C300X DC datasheet (car outlet 10.8-14 V, LiFePO4):
  https://solarhandel24.de/cdn/shop/files/Datenblatt_Anker_Solix_C300X_DC_Powerstation.pdf
- Waveshare SO-ARM100/101 wiki (12 V follower servos): https://www.waveshare.com/wiki/SO-ARM100/101
- V1 records in this repository: `kiro-wiring/docs/power_system_design.md`, `kiro-wiring/docs/parts_list.md`
- Earlier V2 draft: `kiro-wiring-2/archive/flat-v2-2026-11-12/docs/KIRO_V2_design_basis.md`
