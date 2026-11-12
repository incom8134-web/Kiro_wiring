# KIRO Wiring V2 – Design basis (battery-powered robot)

Status: **draft 1, 2026-11-11**. This is the engineering basis for the V2 KiCad schematic.
The schematic itself is not built yet (see section 13). V1 files were only read, never changed.

Every value carries its source:

- **V1-measured** – measured on the V1 robot and recorded in `_local/project_context.md` or `docs/power_system_design.md`
- **V1-doc** – stated in V1 documents without a measurement
- **vendor** – manufacturer or seller page, checked 2026-11-11 (links in section 14)
- **assumption** – engineering allowance, to be replaced by a real number
- **TBD** – unknown; needs a label photo, a model number or a measurement from you

---

## 1. Hardware inventory

| # | Item | Model | Source | Open point |
|---|---|---|---|---|
| 1 | Battery | "12 V, 45 Ah" | your brief | chemistry, BMS, charger, connector all **TBD** |
| 2 | Computer | NVIDIA Jetson Orin Nano Super Developer Kit, 8 GB | V1-doc | – |
| 3 | Carrier board | NVIDIA reference carrier of the developer kit (P3768) | V1-doc + vendor | confirm the board is the stock devkit carrier, not a third-party one |
| 4 | Wheel servos | 4 × Feetech/Waveshare ST3215-C018, IDs FR 7, FL 8, RR 9, RL 10 | V1-measured | – |
| 5 | Wheel driver | Waveshare Bus Servo Adapter (A) type board, USB chip CH343 (USB ID 1a86:55d3) | V1-measured (USB ID); board name **V1-doc "most likely"** | photo of the board silkscreen |
| 6 | Leader arm adapter | same CH343 board type | V1-doc | photo |
| 7 | Follower arm adapter | same CH343 board type | V1-doc | photo |
| 8 | "CH…" chipset | **CH343** (USB 1a86:55d3, "USB Single Serial") | V1-measured | – |
| 9 | Leader arm servos | 6 × STS3215, torque off | V1-doc | – |
| 10 | Follower arm servos | 6 × STS3215; V1 unit is the 7.4 V type (limit 8.0 V) | V1-measured | **which servo type is on the V2 robot? (question Q2)** |
| 11 | 5 V converter | TOBSUN EA75-5V, 12/24 V → 5 V, 15 A, 75 W | V1-doc + vendor | – |
| 12 | USB hub | V1 documents disagree: "ST Lab, 4 ports" (parts list) and "VIA VL815 chipset, self-powered" (context) | V1-doc | exact model, input voltage, barrel size, polarity **TBD** |
| 13 | Head camera | Orbbec Gemini 335 | V1-measured | – |
| 14 | Wrist camera | Suyin HD webcam, USB ID 1e45:8022 | V1-measured | retail model name **TBD**; is a second wrist camera fitted? |
| 15 | LiDAR | Slamtec RPLIDAR C1 with its CP2102N USB adapter | V1-measured | – |
| 16 | E-stop | one mushroom button | your brief | model, contact blocks (1 NC? 2 NC?) **TBD** |
| 17 | Contactor | paired with the E-stop | your brief | model, coil voltage, coil current, contact rating, auxiliary contacts **TBD** |
| 18 | Red warning light | "ordinary 12 V" | your brief | current, polarity, voltage range **TBD – must be measured** |

Not in your brief but present in V1 records, so **not** drawn until you confirm:

- A USB gamepad and a keyboard dongle on the hub.
- Two head-camera servos (ST3215-C018), mentioned in the KakaoTalk log of 2026-10-13.
- A second leader/follower pair (the V1 context lists four arms; Rev F and your brief list one pair).

---

## 2. Battery

Nothing about the battery beyond "12 V, 45 Ah" is recorded anywhere in the folder.
The design depends on the chemistry, so here are the three realistic cases:

| | Lead-acid (AGM/gel) | LiFePO4 4S | Li-ion 3S |
|---|---|---|---|
| Nominal | 12.0 V | 12.8 V | 10.8–11.1 V |
| Full / on charge | 14.4–14.7 V | 14.4–14.6 V | 12.6 V |
| Minimum | about 10.5 V | about 10.0 V (BMS) | about 9.0 V (BMS) |
| Usable share of capacity | about 50 % | about 80 % | about 80 % |

These are typical figures (assumption), not your battery's datasheet.

**Consequence for the wheel drive.** The ST3215 is specified for 6–12.6 V (vendor), the adapter board
for 9–12.6 V (vendor), and the V1 wheel servos reported `Max_Voltage_Limit` 14.0 V (V1-measured).
A lead-acid or LiFePO4 battery sits above 12.6 V for much of its discharge and reaches 14.4 V or
more on charge. So for those two chemistries the wheel branch needs **`REGULATED_12V`**:
a 12 V buck-boost stabiliser rated for at least 11 A continuous (four wheels stalled = 10.8 A).
Only a 3S Li-ion pack lets the wheels run from raw battery voltage.

**What I need from you:** a photo of the battery label and of the charger label. That settles
chemistry, BMS current limits, charge voltage and connector.

---

## 3. Voltage compatibility with raw battery (10.0–14.6 V worst case)

| Load | Safe input range | Source | Raw battery OK? |
|---|---|---|---|
| Jetson devkit DC jack | 9–20 V (V1-doc); 9–19 V (vendor review) | check carrier spec | yes |
| TOBSUN EA75-5V | 8–40 V | vendor | yes |
| Wheel servos ST3215-C018 | 6–12.6 V, trip at 14.0 V | vendor, V1-measured | **no** for lead-acid / LiFePO4 |
| Bus Servo Adapter (A) | 9–12.6 V nominal | vendor | follows the servo rail |
| Follower servos (7.4 V type) | trip at 8.0 V | V1-measured | never – 5 V rail only |
| USB hub | TBD | – | TBD |
| Cameras, LiDAR | 5 V from USB | V1-measured | not connected to the battery |
| Red light | TBD | – | TBD |

---

## 4. Power domains

| Net | Source | Cut by E-stop? | Loads |
|---|---|---|---|
| `BATTERY_RAW` | battery, after main fuse and disconnect | no | everything |
| `COMPUTE_POWER` | `BATTERY_RAW` via F_JETSON | **no** | Jetson DC jack |
| `USB_SENSOR_5V` | Jetson USB ports and the powered hub | **no** | cameras, LiDAR, adapter logic |
| `DRIVE_POWER` | contactor output → 12 V regulator (if needed) → F_WHEELS | **yes** | wheel adapter + 4 servos |
| `ARM_POWER` | contactor output → EA75-5V → F_LEADER / F_FOLLOWER | **yes** (follower); leader see note | arm adapters |
| `BEACON_12V` | contactor output → F_BEACON | yes | red light |
| `REGULATED_12V` | 12 V stabiliser, only if section 2 requires it | yes | wheel branch |
| `LOGIC_3V3` | Jetson 40-pin header | no | GPIO buffer |
| `LOGIC_5V` | Jetson 40-pin header | no | not used unless the light driver needs it |
| `POWER_GND` | single star point at the battery negative | – | all returns |

Notes:

- The leader arm has torque off and cannot move by itself. It may sit before or after the contactor.
  Default: after the contactor, on its own fuse, as your brief asks ("powered-arm actuator energy").
- The followers drop under gravity when power is cut (V1-doc). That is expected behaviour for this
  E-stop, but people near the robot should know it.
- The hub feed depends on its input voltage (TBD). If 5 V: a small separate 5 V converter on the
  compute side, not the arm buck, so the hub stays alive after an E-stop.
- USB cables must not carry motor return current: every adapter board's power return goes back to
  the star point by its own wire, as in V1.

---

## 5. Load and power budget

Per-device numbers are the V1 values. New V2 items are allowances until measured.

| Branch | Typical | Design continuous | Peak | Source |
|---|---|---|---|---|
| Jetson incl. USB loads on its ports | 25 W | 36 W | 45 W | V1-doc |
| Wheels (4 × ST3215-C018) | 14 W (1.2 A) | 72 W (6.0 A) | 130 W (10.8 A, all stalled) | V1-measured / vendor |
| Arms through the 5 V buck (input side, 90 % eff.) | 10 W | 31 W | 48 W | V1-doc |
| USB hub + LiDAR | 10 W | 10 W | 10 W | **assumption** |
| Contactor coil + red light | 10 W | 10 W | 10 W | **assumption** |
| **Total at the battery** | **about 70 W** | **about 160 W** | **about 245 W** | – |
| Battery current at 12.0 V | 5.8 A | 13.3 A | 20.4 A | – |
| Battery current at 10.5 V | 6.7 A | 15.2 A | 23.3 A | – |

A 12 V stabiliser in the wheel branch adds roughly 8 % to that branch (assumption).

### Runtime estimate

| | Lead-acid | LiFePO4 |
|---|---|---|
| Nominal energy | 12.0 V × 45 Ah = 540 Wh | 12.8 V × 45 Ah = 576 Wh |
| Usable energy | 270 Wh (50 %) | 461 Wh (80 %) |
| Runtime at 70 W (typical) | about 3.9 h | about 6.6 h |
| Runtime at 160 W (design continuous) | about 1.7 h | about 2.9 h |

Assumptions: usable shares as in section 2; converter losses are already inside the load figures;
no allowance for battery ageing or cold; lead-acid loses further capacity at high current.

Current margins against the battery/BMS limits cannot be stated until the BMS rating is known.

---

## 6. Protection, fuses and cables (preliminary)

Fuse values below are sized from the load table and the wire. Each one becomes final only when
the item in the last column is known.

| Fuse | Location | Preliminary value | Wire | Final when |
|---|---|---|---|---|
| F_MAIN | within 150 mm of battery + | 30 A | 10 AWG | BMS continuous/peak rating known |
| F_CTRL | E-stop / coil loop | 2 A | 20 AWG | coil current known |
| F_JETSON | `COMPUTE_POWER` | 5 A | 18 AWG | – (as V1) |
| F_HUB | hub feed | TBD | TBD | hub input known |
| F_DRIVE | contactor output → regulator / wheels | 15 A | 14 AWG | regulator chosen |
| F_ARM_IN | contactor output → EA75-5V | 10 A | 14 AWG | – (buck max about 7 A in) |
| F_LEADER | 5 V → leader adapter | 2 A | 20 AWG | – (as V1) |
| F_FOLLOWER | 5 V → follower adapter | 15 A | 14 AWG | – (as V1) |
| F_BEACON | contactor output → light | **not selected** | TBD | light current measured |

Other protection items for the schematic:

- Manual battery disconnect switch directly after F_MAIN.
- Reverse-polarity protection: keyed battery connector plus an ideal-diode / P-FET stage on the
  compute branch. The high-current drive branch relies on the keyed connector and F_MAIN.
- TVS diode across `BATTERY_RAW` at the distribution point, voltage chosen after the chemistry is known.
- Flyback diode (or the suppressor the contactor datasheet specifies) across the coil.
- Pre-charge: decide after the 12 V stabiliser and its input capacitance are chosen.
- Wheel servos stay on two chains (port 1 → 7 → 9, port 2 → 8 → 10) so no Molex 5264 contact
  (about 3 A, V1-doc) carries more than two servos.
- Adapter boards are fed through the screw terminal, not the 5.5 × 2.1 mm jack.
- Jetson plug: 5.5 × 2.5 mm, centre positive (V1-doc).

---

## 7. E-stop and contactor circuit

Self-holding circuit. No software is involved.

```text
BATTERY_RAW ── F_CTRL ── ESTOP (NC) ──┬── START pushbutton (NO) ──┬── K1 coil A1
                                      └── K1 auxiliary (NO) ──────┘
                                                          K1 coil A2 ── POWER_GND
                              D1 across the coil, cathode to A1

BATTERY_RAW ── K1 main contact ── 12V_AFTER_CONTACTOR ── F_DRIVE / F_ARM_IN / F_BEACON
```

| Requirement | How the circuit meets it |
|---|---|
| Works without the Jetson | the loop is only battery, switch, contacts and coil |
| Opens at once when pressed | the NC contact breaks the coil current |
| Drops out on a broken wire | any open in the loop removes coil current |
| No automatic restart | releasing the mushroom does not re-close K1; the auxiliary contact is open |
| Deliberate restart | START must be pressed after the mushroom is released |
| Jetson keeps running | `COMPUTE_POWER` branches off before K1 |

`ESTOP_OK` to the Jetson: an optocoupler whose LED is fed from `12V_AFTER_CONTACTOR` through a
resistor, with the transistor side on the Jetson's 3.3 V. The Jetson reads "drive power present".
No copper connection carries 12 V to the header.

Depends on TBD items: whether the contactor has an auxiliary NO contact (if not, a small relay in
parallel with the coil does the holding), and the coil voltage and current.

---

## 8. Jetson GPIO

The computer is the Orin Nano Super developer kit, so the header is the 40-pin expansion header of
the reference carrier, with 3.3 V signals. I have **not** assigned physical pins, because the
carrier specification still has to be read for three things your brief requires: the drive limit
of the chosen pin, its state at boot and its state after GPIO cleanup.

Point to check in that specification: as far as I know, the header pins on this carrier pass
through bidirectional level shifters that can source only a very small current. If that is
confirmed, a header pin cannot drive an optocoupler LED or a transistor base directly, and every
output needs a high-impedance buffer (a 3.3 V logic buffer or a logic-level MOSFET gate).
The light driver below is drawn with that buffer for this reason.

| Signal | Direction | Purpose | Pin |
|---|---|---|---|
| `ESTOP_OK` | in | drive power present (optocoupler) | TBD |
| `MOTION_WARNING_REQUEST` | out | light request | TBD |
| `JETSON_HEARTBEAT` | out | optional watchdog stage for the light | TBD |
| `BEACON_STATE` | in | optional feedback of the light output | TBD |

---

## 9. Red motion-warning light

### Circuit

```text
12V_AFTER_CONTACTOR ── F_BEACON ── LIGHT + … LIGHT − ── Q1 drain
                                                        Q1 source ── POWER_GND

Jetson GPIO ── series R ── 3.3 V buffer ── driver stage ── gate R ── Q1 gate
                                                    gate-source pull resistor
Test points: TP_BEACON_ENABLE (gate drive), TP_BEACON_OUT (light −)
```

Low-side N-channel MOSFET, as your brief prefers. Q1, the fuse and the connector are **not
selected** until the light current is measured. Selection rules: V_DS at least 30 V, R_DS(on)
specified at the real gate voltage, fuse one standard step above the measured current and below
the wire and connector rating.

### Fail-to-warning behaviour

Your brief asks that a frozen Jetson with the drive still armed leaves the light on.
The driver stage is therefore arranged so that the light is **on by default whenever the contactor
is closed**, and the Jetson has to hold it off actively:

- Jetson off, booting or pin floating → light on while armed.
- Jetson running, robot stationary → Jetson holds the light off.
- Jetson frozen with the pin stuck in the "off" state → not covered by this alone. Covering it
  needs the heartbeat stage (the light turns on when the pulses stop). This adds a few parts;
  it is your decision (question Q4).

### Control sequence

```text
state STOPPED:
    wheels commanded to zero, light off
    on non-zero wheel command:
        light on
        wait until BEACON_STATE confirms, or 0.2 s timeout -> log error, refuse motion
        wait 0.5 s
        -> MOVING

state MOVING:
    forward wheel commands, light on
    when all wheel commands are zero:
        command zero velocity
        -> STOPPING

state STOPPING:
    light on, start 1.0 s timer
    on non-zero wheel command -> MOVING (no new 0.5 s wait, light never went off)
    on timer end -> STOPPED

always:
    if ESTOP_OK is false -> command zero, refuse motion, log
    toggle JETSON_HEARTBEAT every cycle (if the watchdog stage is fitted)
    at start-up: configure the pin first; no wheel command is accepted before that
    at shutdown or crash handler: zero velocity, torque off, leave the pin in the "light on" state
```

V1 software already has two matching pieces (V1-doc): `mecanum_base_node` sends zero velocity
0.5 s after the last `/cmd_vel`, and the servos report speed over the bus. The reported servo speed
can serve as the `ROBOT_MOVING` confirmation; no extra encoder is needed or invented.

---

## 10. USB, cameras and LiDAR

| Device | Supply | Current | Interface | Connects to | Source |
|---|---|---|---|---|---|
| Orbbec Gemini 335 | USB bus | 896 mA max, under 6.5 W peak | USB 3.2 Gen 1 | Jetson port directly, bundled cable, never via hub | V1-measured |
| Suyin wrist webcam | USB bus | needs 500 mA | USB 2 | Jetson port directly | V1-measured |
| RPLIDAR C1 + CP2102N | 5 V USB | 230 mA typical | UART 460800 inside, USB outside | powered hub | V1-measured |
| 3 × CH343 adapter (logic) | USB bus | small | USB 2, 1 Mbps half-duplex servo bus | powered hub | V1-measured |
| USB hub | own DC input | TBD | USB 3 | Jetson port | TBD |

LiDAR start-up rule from V1: connect the sensor cable only with USB unplugged; keep it away from 12 V wiring.

---

## 11. Sequences

**Start-up:** battery disconnect on → Jetson boots (contactor still open, no actuator power) →
software starts and configures GPIO → release mushroom if pressed → press START → K1 closes,
light comes on until the Jetson holds it off → software sees `ESTOP_OK` → motion allowed.

**Shutdown:** stop motion → torque off → press the mushroom (K1 opens) → shut down the Jetson →
battery disconnect off.

**Emergency stop:** press mushroom → K1 opens → wheels, arms and light lose power; followers drop
→ Jetson stays up, logs `ESTOP_OK` false, refuses motion → clear the hazard → release mushroom →
press START.

**Bring-up order:** as V1 section 8, with these additions at the front: check battery polarity at
the connector with a meter; fit only F_MAIN and F_CTRL; test the E-stop loop (latch, drop-out,
no restart on release, drop-out with a wire pulled) before any load fuse is fitted.

---

## 12. Open items (TBD list)

| # | Item | What settles it |
|---|---|---|
| 1 | Battery chemistry, BMS limits, connector | label photo |
| 2 | Charger model and voltage | label photo |
| 3 | Contactor model, coil, contacts, auxiliary | label photo |
| 4 | Mushroom button contact blocks | photo of the rear |
| 5 | Red light current and polarity | meter reading at 12 V and at charge voltage |
| 6 | Follower servo type on the V2 robot (7.4 V or 12 V) | your answer |
| 7 | USB hub model, input voltage, barrel size, polarity | label photo of hub and its adapter |
| 8 | Adapter board silkscreen | photo |
| 9 | Wrist camera retail model; number of wrist cameras | your answer |
| 10 | Head-camera servos, gamepad, second arm pair: on V2 or not | your answer |
| 11 | 12 V stabiliser model (if required) | follows item 1 |
| 12 | Jetson header pins, drive limits, boot states | carrier specification, then a bench check |
| 13 | Cable lengths | measured on the robot |

---

## 13. Schematic status

- `kiro_wiring_v2/kiro_wiring_v2/kiro_wiring_v2.kicad_sch` is still the empty file KiCad created
  (230 bytes, A4, no symbols). The project has not been renamed to "KIRO Wiring V2".
- A stale lock file `~kiro_wiring_v2.kicad_pro.lck` is in that folder from the interrupted session.
- The interrupted session left `konnect_plan.json` and `konnect_mcp_client.mjs` in the folder root.
  The only planned call was the project rename.
- `research_notes/KIRO hardware verification/` exists and is empty.

---

## 14. Sources

- Waveshare ST3215 servo wiki: https://waveshare.com/wiki/ST3215_Servo
- Waveshare Bus Servo Adapter (A) wiki: https://waveshare.com/wiki/Bus_Servo_Adapter_(A)
- Waveshare Bus Servo Adapter (A) docs: https://docs.waveshare.com/Bus_Servo_Adapter_A
- TOBSUN 12/24 V → 5 V 15 A listing (8–40 V input): https://www.newegg.com/p/2VH-02NC-002K1
- NVIDIA Jetson Orin Nano devkit hardware layout: https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html
- Jetson Orin Nano Developer Kit Carrier Board Specification (copy): https://uelectronics.com/wp-content/uploads/2023/05/Jetson-Orin-Nano-DevKit-Carrier-Board-Specification.pdf
- JetsonHacks devkit review (DC jack 9–19 V): https://jetsonhacks.com/2023/03/22/nvidia-jetson-orin-nano-developer-kit-the-perfect-solution-for-makers-and-developers-a-review/
- V1 records in this repository: `docs/power_system_design.md`, `docs/parts_list.md`, `_local/project_context.md`
