# Power distribution and protection: EV battery design (Rev A)

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
BT1 -> F1 main -> SW1 disconnect -> battery bus
   battery bus -> K1 (E-stop) -> U3 12.0 V regulator -> FUSE BOX 1 (12 V): F11 wheels, F12 arm 1, F13 arm 2
   battery bus -> F3 -> Jetson DC jack                       (stays on after E-stop)
   battery bus -> F4 -> EA75-5V -> FUSE BOX 2 (5 V ONLY): F21 hub 1, F22 hub 2, F23 5 V electronics
   battery bus -> F5 -> S1 (NC) -> START || K1 aux -> K1 coil
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
| F5 | 2 A inline | 20 AWG | E-stop loop and coil | coil allowance | K1 selected |
| F11 | 15 A blade (FB1) | 14 AWG | wheel adapter | V1 F2 | - |
| F12, F13 | 10 A blade (FB1) | 14 AWG | arm 1, arm 2 adapters | estimate: 3 A design, 8 A peak | 12 V arm current measured |
| F21, F22 | 3 A blade (FB2) | 18 AWG | hub 1, hub 2 | placeholder | hub input known |
| F23 | 2 A blade (FB2) | 20 AWG | 5 V electronics | placeholder | load defined |
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
- K1 is held by a hardware loop: `F5 -> S1 (NC) -> START || K1 aux -> coil`. No software is involved.
- S1 pressed or a loop wire broken: K1 opens; wheels and both arms lose power. The arms drop under gravity.
- The Jetson, the hubs and the 5 V rail stay on so the computer can log the stop.
- Releasing S1 does not restart. START must be pressed.
- D1 (1N4007, cathode to A1) suppresses the coil.

The archived draft in `../archive/flat-v2-2026-11-12/` also contains an `ESTOP_OK` optocoupler input to the Jetson and
a warning beacon. They are not part of Rev A and can be added later.

## 7. Charging and low voltage

- Charge only with SW1 open and with a charger made for the battery's chemistry.
- F2 protects the charge lead. The inlet connector must be keyed and different from every load connector.
- Low-voltage cut-off: a lithium pack's BMS does it. A lead-acid battery has none, so a low-voltage disconnect at
  about 10.8 V would be needed. Decide after the chemistry is known.
