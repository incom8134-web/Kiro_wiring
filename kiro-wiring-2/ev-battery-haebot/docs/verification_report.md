# Verification report: EV battery design (Rev A, 2026-11-13)

**Overall status: PROPOSED. This design is not validated.** The battery itself is not identified.

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
| Net connectivity | KiCad netlist export compared with the intended connection table | Pass after one fix: tee connections on the battery bus were not joined in the first export and were corrected |
| Unconnected pins | netlist review | Only intended ones: spare fuse slots, second adapter ports, last servo in each chain, hub 2 downstream ports |
| KiCad ERC | not run | **Open.** The CLI available here (7.0.11) has no ERC command. Run ERC in KiCad 8 or newer |
| PDF readability | exported PDF rendered and inspected | Pass |
| Battery voltage range against each load | table in the protection notes | Servo rail needs a regulator unless the pack is 3S Li-ion |
| Fuse and wire sizes | V1 values and calculation | Preliminary; see below |
| E-stop behaviour | schematic review | Opens K1 with no software; no restart on release |

## 2. Results

| Item | Status | Evidence or reason |
|---|---|---|
| Jetson on raw battery voltage | Verified by V1 records | DC jack 9-20 V; envelope 10.0-14.6 V |
| EA75-5V on raw battery voltage | Verified by vendor range | 8-40 V input, 15 A output |
| Wheel servo voltage and current | Verified | V1 measured, vendor |
| Two-fuse-box layout, F3, F4, F11 values | Verified layout | same as V1 Rev F |
| Battery current and runtime | Calculated | `power_budget.md` |
| Voltage drop on main and branch runs | Calculated | protection notes section 5 |
| 12 V arm servos (STS3215-C018) | Proposed | part exists; mechanical fit and current on this robot not checked |
| F12, F13, arm current | Proposed | estimate |
| U3 12 V regulator, K1, SW1, S1, START, bus bar | Proposed | no part selected |
| Battery chemistry, voltage range, BMS limits | Blocked | battery label |
| Main fuse rating and interrupt rating | Blocked | needs BMS limit and fault current |
| Charger and charging connection | Blocked | charger label |
| Low-voltage disconnect | Blocked | depends on chemistry |
| Hub power (voltage, current, plug) | Blocked | hub label |
| 5 V control electronics | Blocked | no 5 V accessory is identified in the records |

## 3. Bring-up order

1. Check battery polarity at the connector with a meter. Fit only F1 and F5.
2. Test the E-stop loop with fuse box 1 empty: latch, drop-out, no restart on release, drop-out with a wire pulled.
3. Fit F4. Measure 5.0-5.2 V at fuse box 2 before any 5 V load is connected.
4. Fit F3. Boot the Jetson.
5. Set U3 to 12.0 V with fuse box 1 empty. Then fit F11 and test the wheels on blocks.
6. Fit F12 and F13 only after the 12 V servos are installed and the arms are calibrated.
7. Clamp-meter the battery lead during a full run and record the peak.

## Sources

- Anker SOLIX C300 DC user manual (A1726), specifications and USB power distribution table:
  https://www.santansolar.com/wp-content/uploads/TEM_A1726_V1_EN_UM_Web_20240913.pdf
- Anker SOLIX C300 DC product page: https://anker.com/products/a17260z1
- Anker SOLIX C300X DC datasheet (car outlet 10.8-14 V, LiFePO4):
  https://solarhandel24.de/cdn/shop/files/Datenblatt_Anker_Solix_C300X_DC_Powerstation.pdf
- Waveshare SO-ARM100/101 wiki (12 V follower servos): https://www.waveshare.com/wiki/SO-ARM100/101
- V1 records in this repository: `kiro-wiring/docs/power_system_design.md`, `kiro-wiring/docs/parts_list.md`
- Earlier V2 draft: `kiro-wiring-2/archive/flat-v2-2026-11-12/docs/KIRO_V2_design_basis.md`
