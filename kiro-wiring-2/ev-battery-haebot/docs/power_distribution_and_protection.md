# Power distribution and protection: EV battery design (Rev B, 2026-11-26)

This design keeps the V1 Rev F layout (two fuse boxes and the EA75-5V buck) and replaces the AC inlet and the SMPS with
a battery, a main fuse, a disconnect, an E-stop contactor and, if the chemistry needs it, a 12 V regulator.

## 1. The battery is not identified yet (Blocked)

"12 V 45 Ah" does not fix the chemistry. The design envelope covers all realistic cases:

|  | Lead-acid (AGM / gel) | LiFePO4 4S | Li-ion 3S |
|---|---|---|---|
| Nominal | 12.0 V | 12.8 V | 10.8-11.1 V |
| Full / on charge | 14.4-14.7 V | 14.4-14.6 V | 12.6 V |
| Minimum | about 10.5 V | about 10.0 V (BMS) | about 9.0 V (BMS) |
| Charger | 3-stage lead-acid | LiFePO4 CC/CV 14.6 V | Li-ion CC/CV 12.6 V |
| Built-in BMS | none | usual | usual |

These are typical values, not your battery's datasheet. A photo of the battery label and the charger label settles
chemistry, BMS limits, charge voltage and connector. Until then F1, F2, K1, U3, the low-voltage cut-off and the
charging connection stay preliminary.

## 2. Voltage compatibility with raw battery voltage (10.0-14.6 V)

| Load | Accepted input | Raw battery OK? |
|---|---|---|
| Jetson developer-kit DC jack | 9-20 V (V1 record) | yes |
| TOBSUN EA75-5V buck | 8-40 V (vendor) | yes |
| ST3215-C018 wheel servos and the proposed 12 V arm servos | max 12.6 V, trip at 14.0 V (vendor, V1 measured) | **no** for lead-acid and LiFePO4 |
| Bus Servo Adapter (A) | 9-12.6 V | follows the servo rail |
| USB hubs | unknown | blocked; drawn on the 5 V rail |

Therefore the motion branch gets **U3, a 12.0 V regulator (buck-boost, 20 A or more)**. It is conditional: only a
3S Li-ion pack, which never exceeds 12.6 V, allows U3 to be replaced by a link.

## 3. Topology

```text
BT1 -> F1 main -> SW1 disconnect -> U6 Matek BAT+ -> ESC+ -> battery bus
   battery bus -> K1 (E-stop) -> U3 12.0 V regulator -> FUSE BOX 1 (12 V): F11 wheels, F12 arm 1, F13 arm 2
   battery bus -> F3 -> Jetson DC jack                       (stays on after E-stop)
   battery bus -> F4 -> EA75-5V -> FUSE BOX 2 (5 V ONLY): F21 hub 1, F22 hub 2, F23 Matek electronics + auxiliary feed
   battery bus -> F5 -> S1 (mechanically latching NC) -> K1 coil -> POWER_GND
FB2 F23 -> J5 AUX_5V -> U6 5V; U6 G -> POWER_GND
U6 SDA/SCL -> Jetson I2C interface (pin/bus/pull-up/driver selection pending)
J2 charger inlet -> F2 -> battery side of SW1
```

Fuse box 1 sits after the contactor so one E-stop action removes power from every actuator. The Jetson and the buck
input use inline fuse holders on the battery bus because the Dorhea fuse box has a single live input.

## 4. Fuses and wire (preliminary)

| Ref | Value | Wire | Load | Basis | Final when |
|---|---|---|---|---|---|
| F1 | 40 A, ANL or MIDI, within 150 mm of battery + | 8 AWG | everything | high-load case 23 A, worst case 34 A at 12.0 V (39 A at 10.5 V) | BMS rating and battery fault current known; the fuse interrupt rating must exceed the fault current |
| F2 | 15 A | 14 AWG | charger | placeholder | charger selected |
| F3 | 5 A inline | 18 AWG | Jetson | V1 F1 | - |
| F4 | 10 A inline | 14 AWG | buck input | V1 F3 (buck draws about 7 A at most) | - |
| F5 | 2 A inline, provisional | 20 AWG | NC E-stop and K1 coil | former allowance only; actual coil current TBD | coil inrush/hold current, S1 DC inductive rating and suppression verified |
| F11 | 15 A blade (FB1) | 14 AWG | wheel adapter | V1 F2 | - |
| F12, F13 | 10 A blade (FB1) | 14 AWG | arm 1, arm 2 adapters | estimate: 3 A design, 8 A peak | 12 V arm current measured |
| F21, F22 | 3 A blade (FB2) | 18 AWG | hub 1, hub 2 | placeholder | hub input known |
| F23 | 2 A blade (FB2), preliminary | 20 AWG | U6 Matek electronics + J5 auxiliary feed | Matek about 1 mA; fuse protects feeder, not sensor current range | JST cable and any remaining auxiliary load rating checked |
| K1 to U3 to FB1 | - | 8 AWG to U3, 10 AWG after | motion feed | 20 A class | U3 selected |

Connector ratings: Molex 5264 servo contacts about 3 A (V1 record). The wheels stay on two chains. An arm is a single
chain of six servos, so the first connector carries the whole arm current. That is how the 12 V SO-101 kits are built,
but 8 A peak is above the contact rating. Measure arm current before fixing F12 and F13.

## 5. Returns and voltage drop

- Dorhea fuse boxes have no negative bus. Add a negative bus bar at the battery minus as the single star point
  (`POWER_GND`). This part is **Proposed**.
- Every load returns to the star point on its own wire of the same gauge as its feed.
- Do not daisy-chain grounds between boards. A USB cable must never carry motor return current.
- Keep battery to FB1 short. At 20 A, 1 m of 8 AWG (out and back) drops about 0.08 V; 14 AWG branch runs of 1 m at
  10 A drop about 0.17 V. Both are calculated from standard copper resistance.

## 6. Emergency stop and disconnect

- SW1 is the manual battery disconnect. It isolates everything except the charger inlet.
- K1 has a main normally open power contact and a continuously energised coil. Its exact part is the photographed unit labelled 500A DC12V; continuous duty, coil voltage envelope/current, DC breaking rating and polarity are unverified.
- The circuit is `F5 -> S1 (NC, push-to-lock / twist-to-release) -> K1 coil`; the other coil terminal returns to POWER_GND. S1 holds itself mechanically. There is no START button, auxiliary holding contact or safety controller. S1 must have positive-opening NC contacts rated for the actual coil DC inductive load.
- S1 pressed or a loop wire broken: K1 opens; wheels and both arms lose power. The arms drop under gravity.
- The Jetson, the hubs and the 5 V rail stay on so the computer can log the stop.
- **Twisting S1 to release immediately restores motor power. SW1 on with S1 released also energises K1. There is no restart interlock.** Clear commands before releasing; restoration of power can cause motion.
- This is a single-contactor prototype power cut, not a validated emergency-stop safety function. A welded main contact can prevent disconnection.
- D1 is a functional placeholder for manufacturer-approved coil suppression. The former 1N4007 proposal is not approved for the unknown coil. Check existing internal suppression, polarity, current and release time before fitting; diode suppression may delay contact opening.

The archived draft in `../archive/flat-v2-2026-11-12/` also contains an `ESTOP_OK` optocoupler input to the Jetson and
a warning beacon. They are not part of Rev B and can be added later.

## 7. Matek battery discharge monitor

U6 is the selected Matek I2C-INA-BM functional module. Put its **BAT+** high-current pad after SW1 and its **ESC+**
pad before the bus splits into motion, Jetson, buck and coil branches. Retain F1 upstream. Use manufacturer-approved
soldering and strain relief sized for the main cable; do not route main current through JST pins or the dead bottom pad.
The added high-current joints must be rated for F1 and mechanically supported.

- Sensing specification: 0-85 V, 150 A continuous / 204.8 A burst; shunt 0.0002 ohm. These are module specifications,
  not a change to the robot's fuse ratings. At 40 A, calculated shunt loss is 0.32 W and drop is 8 mV, excluding joints.
- Power the small **5V** pin from FB2 F23 through J5 AUX_5V. Supply range is 4-9 V, typical draw 1 mA; no raw battery
  on this pin. **G** goes to POWER_GND. Account for the supplied JST harness rating when finalising F23.
- **SDA/SCL** are I2C data to a functional Jetson GPIO/I2C interface, not USB or the DC jack. Exact header pins, bus,
  3.3 V signal compatibility, onboard pull-ups and Linux driver are pending. Do not connect until checked.
- Default address 69 decimal (0x45); alternatives 68/65 decimal (0x44/0x41). The vendor currently lists INA228/INA238;
  confirm the actual IC. ArduPilot support does not prove a working Jetson integration.
- Monitor stays powered when K1 opens. It measures discharge only in this placement; charge current bypasses it
  with SW1 open. It neither disconnects a low battery nor substitutes for a BMS or fuse.

Source: https://www.mateksys.com/?portfolio=i2c-ina-bm (checked 2026-11-26).

## 8. Charging and low voltage

- Charge only with SW1 open and with a charger made for the battery's chemistry.
- F2 protects the charge lead. The inlet connector must be keyed and different from every load connector.
- Low-voltage cut-off: a lithium pack's BMS does it. A lead-acid battery has none, so a low-voltage disconnect at
  about 10.8 V would be needed. Decide after the chemistry is known.
