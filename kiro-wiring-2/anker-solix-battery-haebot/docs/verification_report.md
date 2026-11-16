# Verification report: Anker design (Rev C, 2026-11-16)

[English](verification_report.md) | [한국어](verification_report.ko.md)

**Overall status: AS BUILT per builder report. Not independently measured.**
The wiring in this folder is the circuit the builder fitted. Currents, the 12 V hold-up of USB-C2, and the hub inputs were not measured on this station.

| Word | Meaning |
|---|---|
| **Verified** | Supported by a datasheet, a manual, or a measurement recorded in this repository |
| **Calculated** | Derived from verified values with stated assumptions |
| **AS BUILT** | Reported by the builder as fitted. Not independently measured |
| **BLOCKED** | Cannot be closed until a hardware fact is supplied |

Do not mark the builder's 12 V reading as Verified. The Anker A1726 manual lists no 12 V USB-C profile.

## 1. Checks performed

| Check | Method | Result |
|---|---|---|
| KiCad file validity | `kicad-cli` 7.0.11 loads `kicad/HAEBOT_ANKER.kicad_sch` and plots `exports/HAEBOT_ANKER_SCHEMATIC.pdf` | Pass |
| Net connectivity | Netlist `exports/HAEBOT_ANKER_NETLIST.net` compared with `wiring_connections.md` | Pass. Jetson is on F5, ahead of K1. Arm 1 is on USB-A1 with no fuse and no K1 pole. Car socket, USB-C3 and USB-C4 are unconnected |
| Unconnected pins | netlist review | Intended: PS1 CAR12V, USB-C3, USB-C4; hub 2 DC and its downstream ports; unused adapter ports; chain ends of the second wheel pair |
| KiCad ERC | not run | **Open.** kicad-cli 7.0.11 has no ERC command. Run ERC in KiCad 8 or 9 before treating the sheet as released |
| Block diagrams | approved Rev C PDFs placed at the existing export filenames | Pass as approved drawings. SVG sources are the same revision and were not used to overwrite those PDFs |
| Source voltage per branch | builder report plus the A1726 manual | See section 2 |
| Continuous current per branch | calculation in `power_budget.md` from V1 Rev F loads | See section 2 |

## 2. Results by branch

| Item | Status | Evidence or reason |
|---|---|---|
| Station model, capacity, port ratings | Verified | Anker A1726 manual |
| No 12 V USB-C profile; 5 V USB-C limited to 3 A | Verified | Anker A1726 manual |
| 12 V on USB-C2 | AS BUILT, builder measurement | Builder measured 12 V at the PD trigger. Current capability not measured |
| Car socket, car-plug lead, both bucks, K1 third pole | AS BUILT: not fitted | Builder report. Removed from the Rev C drawing |
| Wheels: USB-C2 -> 12 V trigger -> Dorhea box -> F1 15 A -> K1 pole 1 | AS BUILT | Builder report. F1 value is the V1 15 A wheel fuse |
| Jetson: F5 5 A, taken before K1, so it stays on after E-stop | AS BUILT | Builder report. Jack 9-20 V is a V1 record |
| Arm 2: USB-C1 -> 5 V PD trigger -> K1 pole 2 | AS BUILT | Builder report. Flagged: source 3 A, design 5 A, burst 8 A |
| Arm 1: USB-A1 -> USB-A to DC jack, no fuse, not on K1 | AS BUILT | Builder report. Leader is about 0.3 A (V1 estimate) |
| E-stop: DRIVE_12V -> fuse -> NC -> START \|\| K1 aux -> coil | AS BUILT | Builder report. F3 is drawn as 1 A; the builder did not state the rating. D1 1N4007 is on the schematic; confirm it is fitted |
| One button cuts wheels and arm 2; Jetson, hubs and arm 1 stay on | AS BUILT | Builder report. Arm 1 remaining live is a warning |
| Wheel servos: 12 V, max 12.6 V, stall 2.7 A | Verified | V1 measured and vendor |
| Follower servos trip above 8.0 V; run on 5 V | Verified | V1 register read and measurement |
| USB-C2 wheels + Jetson vs a usual 3 A / 36 W contract | Calculated: over the usual ceiling | 3.3 A typical and 9.0 A design without the coil; 3.5 A / 9.3 A with a 3 W coil assumption. 36 W is not an Anker rating |
| Arm 2 vs USB-C1 at 5 V | Calculated: typical fits, design does not | 1.5 A typical of 3 A. 5 A design and 8 A burst are not available |
| Arm 1 vs USB-A1 | Calculated | 0.3 A design, 0.6 A peak, of 2.4 A |
| Hub 1 on USB-A2 | BLOCKED | Hub input voltage, current and plug are not recorded |
| Hub 2 | BLOCKED | No power port assigned |
| Station negatives common internally | BLOCKED | Not published. Measure continuity between port grounds with the station off |
| Current USB-C2 holds at the measured 12 V | BLOCKED | Needs a USB-C meter under the wheel and Jetson load |
| Usable energy factor 0.85 | Calculated assumption | Anker does not publish it. One measured discharge would close it |
| PD trigger, K1, S1 and START part numbers | AS BUILT, part numbers not recorded | Do not invent them |

## 3. Limits the as-built circuit does not remove

These were reasons Rev B avoided a 12 V trigger and a 5 V arm source. The builder fitted both. The drawing records that, and the limits stay in force:

1. **12 V on USB-C2 is not a manual profile.** Expect the rail to sag or cut out. A sag on this port browns out the Jetson, because the computer shares the port and is not dropped by the E-stop.
2. **Arm 2 on 5 V PD is limited to 3 A.** The follower design load is 5 A and the burst is 8 A. Do not put the EA75-5V back unless a later revision asks for it.
3. **Arm 1 is not cut by the E-stop.** One button cuts the wheels and arm 2 only.
4. **Never join the positives of two ports.** Negatives meet through the USB shields.

## 4. Still to measure

1. Read the hub label and its adapter label (voltage, current, plug size, polarity) before hub 1 is treated as powered.
2. Assign a power port to hub 2, or record that it is bus-powered.
3. With a USB-C meter, read voltage and current on USB-C2 while the wheels and the Jetson are both on. Record whether the trigger stays at 12 V above 3 A.
4. Confirm F3's fuse rating and that D1 is across the coil, cathode to A1.
5. Confirm the Jetson carrier is the stock developer-kit carrier (P3768).
6. Test the E-stop: latch, drop-out of wheels and arm 2 on S1, no restart on release, Jetson and arm 1 still powered, drop-out with one loop wire pulled.
7. Run KiCad ERC in KiCad 8 or 9 and record every message.
8. One full discharge, if a usable-energy number is needed. Until then, 245 Wh stays an assumption.

## Sources

- Anker SOLIX C300 DC user manual (A1726), specifications and USB power distribution table:
  https://www.santansolar.com/wp-content/uploads/TEM_A1726_V1_EN_UM_Web_20240913.pdf
- Anker SOLIX C300 DC product page: https://anker.com/products/a17260z1
- Anker SOLIX C300X DC datasheet (car outlet 10.8-14 V, LiFePO4):
  https://solarhandel24.de/cdn/shop/files/Datenblatt_Anker_Solix_C300X_DC_Powerstation.pdf
- Waveshare SO-ARM100/101 wiki (12 V follower servos): https://www.waveshare.com/wiki/SO-ARM100/101
- V1 records in this repository: `kiro-wiring/docs/power_system_design.md`, `kiro-wiring/docs/parts_list.md`
- Builder report recorded in this revision (2026-11-16). Not independently measured.
