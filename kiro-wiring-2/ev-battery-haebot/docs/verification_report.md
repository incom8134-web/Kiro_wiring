# Verification report: EV battery design (Rev B, 2026-11-26)

**Overall status: PROPOSED / hardware validation incomplete.** No powered hardware test was performed.
User approval establishes design choices, not the actual electrical ratings.

## 1. Accepted changes

- Both new arms are 12 V. Exact servo MPN, installation, current and mechanical fit are not yet verified.
- K1 is the photographed contactor labelled 500A DC12V; exact manufacturer/MPN and specifications are unknown.
- One positive-opening, mechanically latching NC mushroom S1 is in series with F5 and K1's coil.
- SW2 START, K1 auxiliary contact/holding loop and a reset controller are omitted.
- S1 stays locked open mechanically until twist release. Release immediately restores motion power; SW1 on with
  S1 released also powers motion. There is no restart interlock or enforced separate motion-start action.
- U6 Matek I2C-INA-BM senses the main positive discharge path after F1/SW1 and before all load branches.
- U6 electronics use F23/J5 AUX_5V and POWER_GND. I2C is a functional connection to Jetson GPIO, with actual header
  pins, bus, logic levels/pull-ups, fitted INA228/INA238 variant and software still unverified.
- Existing main/branch protection, U3 conditional regulator, charger and USB arrangement are retained.

## 2. Verification evidence

| Check | Rev B evidence / result |
|---|---|
| Scope | Changes restricted to `kiro-wiring-2/ev-battery-haebot/`; unrelated work is not staged |
| Documentation | README, agent notes, BOM, protection, wiring, assembly, arm notes and budget updated together |
| English/Korean diagrams | SVG and embedded-font PDF generated from one geometry; both PDF renders visually inspected |
| KiCad schematic / netlist / ERC | Final results recorded below; historical passes are not current evidence |
| Hardware operation | NOT TESTED; proposed behaviour only |
| Jetson sensor integration | NOT IMPLEMENTED or tested; physical pin mapping remains pending |
| Functional safety | NOT VALIDATED; one contactor cannot detect or tolerate its own welded main contacts |

Historical Rev A evidence: KiCad 10 ERC on 2026-11-16 reported 0 errors / 49 library warnings before a local symbol
table was added. This is history only and does not validate Rev B.

## 3. Hardware inputs still required

| Item | Status / next evidence |
|---|---|
| Battery / BMS / charger | Blocked: labels, chemistry, voltage envelope and limits |
| K1 continuous duty / DC breaking rating | Blocked: exact datasheet; 500 A label is insufficient |
| K1 coil and S1 rating | Blocked: inrush/hold current, full voltage envelope, polarity; S1 DC inductive rating |
| F5 / D1 | 2 A control fuse and former 1N4007 proposal are unverified; use actual coil requirements and approved suppression |
| U3 | Unselected; retain regulation until voltage compatibility established; check 26.8 A assumed motion peak against >=20 A placeholder |
| F1 / charge protection | Preliminary 40 A / 15 A; final interrupt/current ratings depend on battery and charger |
| 12 V arms / connectors | Voltage choice confirmed; MPN/fit/current/power injection and F12/F13 ratings unverified |
| U6 sensor | Manufacturer range/supply specified; installation, direction and readings untested |
| U6 I2C | Header pins/bus, levels/pull-ups, actual IC variant and driver unresolved |
| F23 / JST harness | Check harness rating and other auxiliary loads before retaining 2 A value |
| USB hubs | Input voltages/plugs and second-hub presence unresolved |

## 4. Bring-up checks (not yet performed)

1. Verify battery polarity, wire/fuse ratings, K1 suitability and coil suppression. Support arms and isolate motion
   loads; leave FB1 empty. Lock S1 before closing SW1.
2. Fit necessary main/control protection. Confirm S1 locked = coil off/contact open; let go = still off;
   twist release = coil energises/contact closes immediately; press again = contact opens.
3. Open a control-loop wire and confirm K1 drops out. Restore only with S1 pressed. There is no restart interlock:
   loss/restoration of supply with S1 released re-enables motion power.
4. Fit F4 and measure 5.0-5.2 V before attaching FB2 loads/U6. Confirm U6 small 5V pin never sees battery voltage.
5. Fit F3 and boot Jetson with motor branches isolated. Resolve I2C pin/logic/driver questions before connecting data.
6. Set U3 to 12.0 V. Fit F11 with wheels raised. Confirm all three adapter motor-supply inputs lose power with S1
   pressed even with USB connected; rule out USB backfeed keeping motors energised.
7. Fit F12/F13 after the new 12 V arms are installed/calibrated and supported. Test cut-off and gravity behaviour.
   Release only with commands cleared: power returns without a separate button.
8. Compare U6 readings to independent meters with K1 open/closed. Record battery/arm peaks; refine coil power,
   protection, converter size and runtime estimates from measurements.

## 5. Sources

- User choices/photographs in the 2026-11-26 conversation: new 12 V arms, one latching NC E-stop, photographed
  500A DC12V contactor, Matek I2C-INA-BM. Photo establishes markings, not verified ratings.
- Matek manufacturer: https://www.mateksys.com/?portfolio=i2c-ina-bm (checked 2026-11-26).
- Similar four-terminal seller diagram (not exact K1 identity proof):
  https://ai.esmplus.com/tw6767/homepageimage/ETC/contactor/HCS3104/d2.jpg
- Positive-opening NC contacts: https://www.idec.com/en-apac/solutions/safety/guide/safety02
- Restart distinction: https://www.pilz.com/en-US/support/faq/standards/articles/180045 . Rev B provides immediate
  power restoration and must not be represented as a validated emergency-stop safety system.
- V1 evidence: `../../docs/hardware_evidence.md`, `../../kiro-wiring/docs/power_system_design.md`,
  `../../kiro-wiring/docs/parts_list.md`; servo candidate: https://www.waveshare.com/wiki/SO-ARM100/101 .

## 6. Final Rev B KiCad check results

Circuit-edit checks on the saved schematic using Konnect and KiCad 10.0.7:

| Check | Result |
|---|---|
| Direct KiCad ERC | 0 errors, 0 warnings; report in `../exports/HAEBOT_EV_ERC.json` |
| Component connection validation | Valid; 0 unconnected pins |
| Wire endpoints / orphan items | 0 floating endpoints; 0 orphan items |
| Shorted-net check | 0 shorts |
| Symbol overlap check | 51 bounds resolved, 0 unresolved; 0 overlaps |
| Exported topology assertions | U6 before every load branch; 5 V electronics supply; separate SDA/SCL; no SW2 or K1 auxiliary pins; all three motor branches after K1/U3 |

Final title block is **Rev B / 2026-11-26**. PDF, netlist and PNG were regenerated from the final saved KiCad 10
source. The schematic PDF itself was rendered and visually inspected; the A3 sheet is readable with no clipping.
English and Korean diagram PDFs were also rendered and inspected, including the Korean glyphs.

`python tools/check_rev_b_netlist.py` passes, including metadata, the monitor supply/signal paths and motor branches.
Detailed final evidence and source SHA-256 are in `../exports/HAEBOT_EV_CONNECTIVITY_CHECKS.json`.
The new local functional symbols are in `../kicad/HAEBOT_EV_Local.kicad_sym`; the shared library was not modified.
KiCad GUI save upgraded the schematic/project format to KiCad 10; use KiCad 10 or newer for this revision.

These circuit checks do not establish hardware operation, physical connector mapping or functional safety.
