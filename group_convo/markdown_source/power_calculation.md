# Power Calculation and Rail Design – Kiro / SO-101 mobile dual-arm robot

Written 2026-10-22. Companion to `context.md`. Numbers marked **measured** come from this robot,
**spec** from manufacturer data, **estimate** from engineering judgement (stated how).

---

## 1. Architecture decision: one 12 V main bus

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **12 V SMPS main bus** (chosen) | Wheels (largest load) and the Jetson (accepts 9–20 V) run **directly** with no converter. Only two 7.2 V rails and one 5 V rail need bucks. Drop-in compatible with a 12 V battery / power station later. Cheap, common parts | Higher bus current → thicker wire (12–14 AWG main run). Wheel stall transients appear on the same bus as the Jetson, so distribution must be star-wired and the SMPS must be stiff | **Recommended** |
| 24 V SMPS main bus | Half the bus current | Every load needs a converter (19 V or 12 V for Jetson, 12 V 11 A for wheels, 7.2 V, 5 V); more parts, more loss, no direct battery path | Not needed |
| Keep separate adapters | Nothing to build | 4–5 mains adapters, no fusing, no E-stop, wheels under-powered (6 A) | Current state, to be replaced |

Rails after rewiring:

| Rail | Voltage | Source | Loads | Cut by E-stop? |
|---|---|---|---|---|
| R1 wheels | 12 V | SMPS direct | 4 × ST3215-C018 | **yes** |
| R2 Jetson | 12 V | SMPS direct | Jetson Orin Nano + its USB loads (Gemini, wrist cam, dongles) | no |
| R3 follower L | 7.2 V | buck L | left follower, 6 × STS3215 | **yes** |
| R4 follower R | 7.2 V | buck R | right follower, 6 × STS3215 | **yes** |
| R5 logic 5 V | 5 V | buck 5 V | VL815 hub (if it is a 5 V hub), lidar via hub, both leader arms' servo power | no |

Why 7.2 V and not 7.4 V for the followers: the follower servos trip a voltage alarm above **8.0 V**
(`Max_Voltage_Limit`, measured). A 7.2 V set point leaves 0.8 V for converter tolerance, ripple and
back-EMF when an arm is pushed by hand. 7.2 V is the usual "7.4 V class" operating level (2S Li-ion nominal).

Why the leaders stay on 5 V: torque is off, they only report positions, and 5 V operation is already
proven on this robot. One fewer 7.2 V converter.

---

## 2. Load budget

### 2.1 Per device

| Device | V | Typical | Design continuous | Peak | Basis |
|---|---|---|---|---|---|
| ST3215-C018 wheel servo (each) | 12 | 0.3 A | 1.5 A | 2.7 A stall | **measured** no-load 0.05–0.18 A, floor driving a few hundred mA; stall **spec** |
| STS3215 follower servo (each, 7.2 V) | 7.2 | 0.25 A | 0.8 A | ~2.5 A stall | **spec** no-load 0.15 A, stall ≈ 2 A @ 6 V (scaled to 7.2 V); holding under gravity **estimate** 0.2–0.5 A |
| STS3215 leader servo (each, torque off) | 5 | 0.04 A | 0.05 A | 0.1 A | **estimate** (logic + encoder only) |
| Jetson Orin Nano Super dev kit, MAXN SUPER | 12 | 20 W | 30 W | 36 W | **spec**: module up to 25 W + carrier/NVMe/fan |
| Orbbec Gemini 335 | 5 (USB) | 3 W | 3 W | 6.5 W | **spec** avg < 3 W, peak < 6.5 W; bMaxPower 896 mA **measured** |
| Suyin wrist webcam | 5 (USB) | 1.5 W | 2.5 W | 2.5 W | **measured** 500 mA descriptor |
| Dongles / mouse / keyboard | 5 (USB) | 0.3 W | 0.5 W | 0.5 W | estimate |
| VIA VL815 hub (own logic) | 5 | 0.5 W | 0.5 W | 1 W | estimate |
| CH343 servo adapter logic (each × 5, via hub) | 5 (USB) | 0.03 A | 0.05 A | 0.05 A | estimate |
| RPLIDAR C1 (via hub) | 5 (USB) | 0.23 A | 0.3 A | 0.5 A start | **spec** 230 mA / 1.15 W; start-up estimate |
| Gamepad (via hub) | 5 (USB) | 0.05 A | 0.1 A | 0.1 A | estimate |

### 2.2 Per rail

| Rail | Typical | Design continuous | Coincident peak | Notes |
|---|---|---|---|---|
| R1 wheels 12 V | 4 × 0.3 = **1.2 A** (14 W) | 4 × 1.5 = **6 A** (72 W) | 4 × 2.7 = **10.8 A** (130 W) | peak = all four wheels stalled, e.g. pushing against an obstacle |
| R2 Jetson 12 V | 20 W + 5 W USB = 25 W → **2.1 A** | 30 W + 6 W = 36 W → **3.0 A** | 36 W + 9.5 W = 45 W → **3.8 A** | Jetson dev kit jack rated **9–20 V, 4.2 A max** (spec) → 50 W ceiling at 12 V, so 45 W peak fits |
| R3 follower L 7.2 V | 6 × 0.25 = **1.5 A** (11 W) | **5 A** (36 W) | **8 A** burst (58 W) | design = 3 joints loaded + 3 holding; six simultaneous stalls (15 A) is not a design case, the buck's current limit handles it |
| R4 follower R 7.2 V | **1.5 A** | **5 A** | **8 A** | same |
| R5 logic 5 V | hub 0.1 + boards 0.15 + lidar 0.23 + pad 0.05 + leaders 12 × 0.04 = **1.0 A** (5 W) | **3 A** (15 W) | **4 A** (20 W) | pick a 5 A converter |

Totals at the loads: typical ≈ 60 W, design continuous ≈ 195 W, coincident peak ≈ 300 W.

### 2.3 Referred to the 12 V bus (converter efficiency 90 %)

| Branch | Typical | Design continuous | Peak |
|---|---|---|---|
| Wheels (direct) | 1.2 A | 6.0 A | 10.8 A |
| Jetson (direct) | 2.1 A | 3.0 A | 3.8 A |
| Buck L input (36 W / 0.9 / 12 V) | 1.0 A | 3.3 A | 5.4 A |
| Buck R input | 1.0 A | 3.3 A | 5.4 A |
| Buck 5 V input (15 W / 0.9 / 12 V) | 0.5 A | 1.4 A | 1.9 A |
| **Total 12 V bus** | **5.8 A (70 W)** | **17 A (204 W)** | **27 A (326 W)** |

---

## 3. SMPS selection

Requirement: 12 V, ≥ 17 A continuous, able to ride through ~27 A for a second or two, trimmable, mains 220 V.

| Candidate | Rating | Fits? | Comment |
|---|---|---|---|
| **Mean Well LRS-350-12** (chosen) | 12 V, 29 A, 348 W, 215 × 115 × 30 mm, 0.76 kg, built-in fan | continuous 59 %, worst-case peak 93 % | Headroom for every coincidence case, so no hiccup shutdowns. Fan noise only under heavy load. Adjustable 10.2–13.8 V |
| Mean Well LRS-200-12 | 12 V, 17 A, 204 W, fanless, 0.66 kg | continuous 100 %, peak 160 % | Works for typical operation but enters overload protection (hiccup) if wheels stall while the arms are working. Acceptable only if weight/noise matter more than margin |
| Mean Well LRS-150-12 (in the old shopping list) | 12 V, 12.5 A | no | Enough for the wheels alone, not for the whole robot |
| 12 V 10 A barrel adapter (old plan) | 120 W | no | Wheels only; barrel jack is a 5 A class connector |

Set the SMPS output to **12.0–12.3 V** with the V-ADJ trimmer and a meter before connecting loads
(the wheel servos tolerate up to 14 V, the Jetson up to 20 V, so 12.x V is safe on both direct rails).

Mains side: IEC C14 inlet module with switch and 5 A fuse, earth (FG) wired to the SMPS FG terminal,
AC terminals covered. The LRS-350 draws a cold-start inrush of tens of amps for one cycle; a normal
wall outlet handles it.

---

## 4. Converter selection

### 4.1 Follower rails (12 V → 7.2 V, two identical units)

Needs: 5 A continuous, 8 A short bursts, adjustable (or fixed 7.2–7.5 V), input 12 V, current limit.
Output power 36 W design; at 90 % efficiency each buck dissipates ≈ 4 W → needs a heatsink or airflow.

| Choice | Spec | Comment |
|---|---|---|
| **Synchronous buck module, 8–12 A class, adjustable** (e.g. "DC-DC 12 A / 300 W step-down" boards with a real heatsink, CC/CV versions are fine) | in 6–40 V, out 1.2–36 V, 8–12 A continuous with heatsink | Budget choice from Korean shops. Verify the output with a meter at no load and under load. Prefer a model with an output voltage lock (trimmer with glue or a fixed-resistor divider) |
| **Pololu D36V50F7** (fixed 7.5 V) | in 8.3–50 V, 5 A at 36 V in, more at 12 V in, thermal and current protection | Compact, reliable, no trimmer to drift. 7.5 V is still 0.5 V below the 8.0 V limit. Good "quality" choice |
| XL4016-based "8 A" module | in 8–40 V, out 1.25–36 V, realistic 5–6 A with heatsink and fan, non-synchronous ~85 % | Cheapest; needs a fan for 5 A continuous. Acceptable fallback |
| LM2596 "3 A" modules | realistic 1.5–2 A | **Too small** |

### 4.2 Logic rail (12 V → 5 V)

Needs: 5 A rated (3 A design). Choice: a sealed automotive-style **12 V → 5 V 5 A** step-down module,
or **Pololu D24V50F5** (5 V, 5 A, in 6–38 V). Feed the hub's DC input and both leader boards' screw terminals.
If the hub turns out to be a 12 V-input hub, feed it from a spare 12 V fuse instead and the 5 V rail only
serves the leaders.

### 4.3 Not needed

- No converter for the Jetson: 12 V is inside its 9–20 V window. Optional upgrade if resets are ever seen:
  a 12 V → 15 V buck-boost (5 A) in front of the Jetson isolates it from bus sag.
- No converter for the wheels: 12 V direct.

---

## 5. Fuses, switch, E-stop

The 12 V bus is split into **two blade (ATO) fuse groups** right after the 30 A master switch (or 30 A DC breaker):

- **Group A – always on** (F2, F5, F6): Jetson, 5 V buck, spare / relay-coil feed.
- **Group B – relay switched** (F1, F3, F4): wheels and the two follower bucks. Its common bus is fed from the
  E-stop relay contact (pin 87).

Use two small fuse blocks, or one 12-way block with two independent positive inputs. Never join fused branches
together after the fuses (that parallels the fuses and removes the per-branch protection).

| Pos | Group | Branch | Fuse | Reason |
|---|---|---|---|---|
| F1 | B | Wheels 12 V | **15 A** | 10.8 A worst case; 15 A allows a short all-wheel stall, still protects 14 AWG wire |
| F2 | A | Jetson 12 V | **5 A** | 3.8 A peak, jack limit 4.2 A |
| F3 | B | Buck L input | **7.5 A** | 5.4 A peak input |
| F4 | B | Buck R input | **7.5 A** | 5.4 A peak input |
| F5 | A | Buck 5 V input | **5 A** | 1.9 A peak; 5 A avoids nuisance trips on converter inrush |
| F6 | A | Spare (relay coil feed, 12 V hub or fan) | 3 A | coil draws 0.15 A |
| Main | – | SMPS → master switch → group A bus and relay pin 30 | **30 A** | protects the 12 AWG main run; mandatory once a battery is used |

**E-stop**: a mushroom head NC switch drives the coil of a **12 V automotive relay, 40 A** (SPST, pins 30/87 power,
85/86 coil). Pin 30 comes from the master switch, pin 87 feeds the group B bus. The contact carries at most
10.8 + 5.4 + 5.4 ≈ 22 A, well inside 40 A. Pressing the E-stop drops the relay → wheels and both follower arms lose
power. The Jetson, the hub, the lidar and the leaders (group A) stay on, so software keeps running and no file
system is hurt.
Coil circuit (0.15 A): F6 → **motor key switch** → E-stop NC contact → relay 86; relay 85 → GND bus. With the key
off the motors are dead at power-up until the operator arms them.
Note: cutting follower power makes the arms go limp; lower them or hold them before pressing in a non-emergency.
A 1N4007 diode across the relay coil (cathode to 86) suppresses the coil spike.

---

## 6. Wire gauges and voltage drop

Copper resistance used: 12 AWG 5.2 mΩ/m, 14 AWG 8.3 mΩ/m, 18 AWG 21 mΩ/m, 20 AWG 33 mΩ/m, 22 AWG 53 mΩ/m.
Drop is for the round trip (out and back).

| Run | Current | Wire | Length (one way) | Drop |
|---|---|---|---|---|
| SMPS → master switch → group A bus / relay pin 30 | 27 A peak | **12 AWG** (or 2 × 14 AWG on the SMPS' double terminals) | 0.3 m | 0.08 V |
| Relay pin 87 → group B bus | 22 A peak | **12 AWG** | 0.2 m | 0.05 V |
| F1 → wheel power hub | 10.8 A peak | **14 AWG** | 1.0 m | 0.18 V |
| Wheel power hub → each wheel servo | 2.7 A | **22 AWG** (Molex 5264 limit) | ≤ 0.3 m | 0.09 V |
| F2 → Jetson barrel plug (5.5 × 2.5 mm, centre +) | 3.8 A | **18 AWG** | 1.0 m | 0.16 V |
| F3/F4 → buck inputs | 5.4 A | **18 AWG** | 0.5 m | 0.11 V |
| Buck output → follower board screw terminal | 8 A burst | **18 AWG** | 0.5 m | 0.17 V |
| Follower board → servo chain | up to 8 A at the first link | 22 AWG pigtails, keep ≤ 0.3 m, **two chains of 3** if the board has two ports | 0.3 m | 0.25 V |
| F5 → buck 5 V → hub / leader boards | 3 A | **20 AWG** | 1.0 m | 0.20 V |

All drops are below 0.3 V, i.e. invisible to the servos (they regulate their own motor drive) and to the Jetson.

**Star grounding**: bring every −V return to one bus bar next to the fuse block (the SMPS −V terminals). Do not
daisy-chain grounds from board to board; the USB cables must not become the return path for motor current.

---

## 7. Connector plan

| Where | Connector | Why |
|---|---|---|
| 12 V branches (wheels, buck inputs) | **XT60** | 60 A class, polarised, cheap |
| 7.2 V and 5 V outputs to boards | **XT30** | polarised, 30 A class, small |
| Jetson | 5.5 × 2.5 mm barrel plug, centre positive, strain relieved | matches the dev kit jack |
| Servo adapter boards | existing screw power terminal (not the barrel jack) | jack is a 5 A part |
| Servos | Molex 5264 3-pin, 22 AWG pre-crimped leads, pin order GND / VCC / SIG | reverse polarity damages servos; keep the factory orientation |
| Wheel power hub (recommended) | small board with 4 × Molex 5264 wafers in parallel on an 18 AWG bus, one signal-only pigtail (GND + SIG, VCC pin removed) to the servo board | gives each wheel its own power lead, so no 5264 contact carries more than one servo; the board carries only signal |

If the wheel power hub is skipped, keep today's **two chains** (port 1 → 7 → 9, port 2 → 8 → 10). The first
connector of each chain then sees up to 5.4 A at stall for a short time; acceptable but not ideal.

---

## 8. Protections and decoupling

- **Bulk capacitor at the wheel power hub**: 2200 µF / 25 V low-ESR electrolytic across 12 V / GND. Absorbs stall
  transients and regenerative energy when the robot is pushed.
- **Bulk capacitor at each follower board**: 1000–2200 µF / 16 V across the 7.2 V terminal. A pushed follower arm
  back-drives its servos and pumps the rail up; a buck cannot sink current, so the capacitor plus the 0.8 V margin
  keep the rail under 8.0 V. Optional extra: a 9.1 V 5 W zener or SMBJ8.0A TVS as a clamp.
- **Reverse polarity**: XT30/XT60 are keyed; still mark + leads red, − black everywhere.
- **SMPS**: built-in overload (hiccup), over-voltage and over-temperature protection.
- **Thermal**: mount both 7.2 V bucks and the 5 V buck on a metal plate or heatsink with airflow; the SMPS fan needs
  2 cm of free air at both ends. Keep the power box away from the lidar head.
- **Power-up order**: mains on → SMPS 12 V → Jetson boots, 5 V rail up (hub, lidar, leaders) → wait for the desktop →
  motor key switch on, E-stop released → run software. Shutdown: stop software (torque off) → motor key off →
  shut down the Jetson → mains off.

---

## 9. Battery path (later)

The 12 V bus is chosen so a battery can replace the SMPS at the master switch:

| Option | Fit | Caveat |
|---|---|---|
| Regulated 12 V portable power station (e.g. Anker SOLIX C300 as used by XLeRobot, 12 V / 10 A DC out) | easy, regulated, built-in BMS and charger | 10 A limit → wheels and arms cannot peak together; fine for demos |
| 3S Li-ion / LiPo pack (12.6 V full, 9.0 V empty) with a 40 A BMS | direct | sags to 9 V near empty (Jetson minimum 9 V); add a low-voltage alarm |
| 4S LiFePO4 (14.6 V full, 12.8 V nominal) | best energy, flat curve | **14.6 V exceeds the wheel servo 14.0 V limit** right after charging → needs a 12 V regulator or a lower charge cut-off |

Energy estimate for a 30 min demo at the typical 70 W: 35 Wh; at the design 200 W continuous: 100 Wh.
A 300 Wh power station gives 1.5–4 h.

---

## 10. Bring-up checklist

1. Wire the AC side, SMPS, master switch, fuse block and bus bar. No loads yet. Power on, set 12.0–12.3 V.
2. Connect the bucks with no load. Set buck L and buck R to **7.20 V**, buck 5 V to 5.0–5.1 V. Lock the trimmers.
3. Fit fuses F2 and F5 only. Connect the Jetson and the hub. Boot, check `nvidia-smi`/desktop, check hub devices (`lsusb -t`).
4. Fit F3/F4. Connect the follower boards. Open the servo tester: each follower servo should read 7.1–7.3 V, no alarms.
   Run the left/right teleop for a minute, watch temperatures.
5. Fit F1. Connect the wheel board / wheel hub. Servo tester: wheels 12.0–12.4 V. Run `mecanum_test.py` with the
   robot on blocks, then on the floor. Measure wheel currents in the tester during a push-stall (expect ≤ 2.7 A each).
6. Press the E-stop while driving: wheels and followers must stop, Jetson and lidar must stay up. Release, re-arm with the key.
7. Clamp-meter the SMPS output during the full demo sequence; note the peak for the record.
8. Update `~/so101/CLAUDE.md` power section with the final set points and measurements.
