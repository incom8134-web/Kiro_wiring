# Power System Design – Kiro / SO-101 mobile robot (Rev F)

Updated 2026-10-26. This replaces the RevA design of 2026-10-22. It matches the hardware that is
actually on hand and the wiring diagram [`images/wiring_diagram.png`](../images/wiring_diagram.png).
Numbers marked **measured** come from this robot, **spec** from manufacturer data, **estimate** from
engineering judgement.

Scope of this build: one leader arm (6 servos), one follower arm (6 servos),
the mecanum base (4 wheel servos), the Jetson, cameras, lidar and one USB hub.

---

## 1. Architecture

One 12 V SMPS feeds everything. The Jetson and the wheel servos run directly from 12 V; one buck
converter makes 5 V for the two arm adapters.

| Rail | Voltage | Source | Fuse | Loads |
|---|---|---|---|---|
| R1 Jetson | 12 V | SMPS direct | F1 5 A (FB1) | Jetson Orin Nano Super (DC jack 9–20 V) + its USB loads |
| R2 Wheels | 12 V | SMPS direct | F2 15 A (FB1) | base adapter A1 + 4 × ST3215-C018 |
| R3 Buck input | 12 V | SMPS direct | F3 15 A (FB1) | U1 buck 12 V → 5 V |
| R4 Leader arm | 5 V | U1 buck | F4 2 A (FB2) | leader adapter A2 + 6 × STS3215 (torque off) |
| R5 Follower arm | 5 V | U1 buck | F5 15 A (FB2) | follower adapter A3 + 6 × STS3215 (5 V test) |

Why the arms stay on 5 V: they already run on 5 V (5.2–5.3 V **measured**), and the follower servos trip
above 8.0 V (`Max_Voltage_Limit`, **measured**), so a 5 V rail can never over-volt them. Moving the
follower to 7.2 V for more torque is a planned upgrade (section 9).

---

## 2. Load budget

### 2.1 Per device

| Device | V | Typical | Design continuous | Peak | Basis |
|---|---|---|---|---|---|
| ST3215-C018 wheel servo (each) | 12 | 0.3 A | 1.5 A | 2.7 A stall | **measured** no-load 0.05–0.18 A; stall **spec** |
| STS3215 follower servo (each, 5 V) | 5 | 0.25 A | 0.8 A | ~2 A stall | **spec** stall ≈ 2 A @ 6 V; holding **estimate** |
| STS3215 leader servo (each, torque off) | 5 | 0.04 A | 0.05 A | 0.1 A | **estimate** (logic + encoder only) |
| Jetson Orin Nano Super, MAXN SUPER | 12 | 20 W | 30 W | 36 W | **spec**: module up to 25 W + carrier/NVMe/fan |
| USB loads on the Jetson (Gemini 335, wrist cam, hub logic, dongles) | 5 (USB) | 5 W | 6 W | 9.5 W | **spec/measured** |

### 2.2 Per rail

| Rail | Typical | Design continuous | Peak |
|---|---|---|---|
| R1 Jetson 12 V | 2.1 A (25 W) | 3.0 A (36 W) | 3.8 A (45 W) – jack limit 4.2 A |
| R2 Wheels 12 V | 1.2 A | 6.0 A | 10.8 A (all four stalled) |
| R5 Follower 5 V | 1.5 A | 5.0 A | 8 A burst |
| R4 Leader 5 V | 0.25 A | 0.3 A | 0.6 A |
| R3 Buck input 12 V (90 % eff.) | 0.8 A | 2.6 A | 4.0 A (buck max 75 W ≈ 7 A) |
| **Total 12 V bus** | **4.1 A (50 W)** | **11.6 A (140 W)** | **18.6 A (225 W)**; 21.6 A with the buck at its 75 W limit |

---

## 3. SMPS

**HS-350-12** (on hand): 12 V, ~29 A, 350 W class, fan-cooled with temperature-controlled fan, 110/220 V
selector switch, 193 × 100 × 45 mm, four bolt-on mounting ears.

- Peak demand 18.6–21.6 A is 64–75 % of rating, so no overload hiccups.
- Check the **110/220 V switch is on 220 V** before first power-up.
- Set the output to **12.0–12.3 V** with the ADJ trimmer before connecting loads
  (wheel servos tolerate up to 14 V, the Jetson up to 20 V).
- Mount flat with the fan facing up and keep **≥ 20 mm of free air above the fan**.
- Mains: IEC C14 inlet with switch and **5 A slow-blow** fuse, PE wired to the SMPS FG terminal,
  AC terminals covered.

---

## 4. Buck converter

**TOBSUN EA75-5V** (on hand): 12/24 V in, 5 V out, 15 A max, 75 W, potted.

- 5 V design load ≈ 5.5 A (27 W), 8.6 A burst – comfortably inside 15 A.
- Feed it from F3. Its output feeds **FB2 only**.
- Measure the output (expect 5.0–5.2 V) before connecting the arm adapters.

---

## 5. Fuses and distribution

Two **Dorhea 4-way blade fuse boxes**. Each box has one live input stud feeding all four slots and
**no negative bus**.

| Box | Input | Slot 1 | Slot 2 | Slot 3 | Slot 4 |
|---|---|---|---|---|---|
| FB1 12 V | SMPS +V (12 AWG) | F1 5 A Jetson | F2 15 A wheels | F3 15 A buck input | spare |
| FB2 5 V | U1 OUT+ (14 AWG) | F4 2 A leader | F5 15 A follower | spare | spare |

- **Never feed FB2 from 12 V** – the arm servos would be destroyed. Label FB2 "5 V ONLY".
- F3 may be reduced to 10 A: the buck draws at most ~7 A.
- The fuse kit on hand has 5/10/15/20 A; **buy 2 A (or 3 A) blade fuses for F4**.

---

## 6. Wiring, returns and wire sizes

No ground bus bar. Every return goes back to the source of its rail, one wire per screw terminal:

| Return | Lands on |
|---|---|
| Jetson −, base adapter A1 0 V, buck IN− | **SMPS COM** terminals (two COM screws) |
| Leader adapter A2 0 V, follower adapter A3 0 V | **buck OUT−** |

| Run | Peak current | Wire |
|---|---|---|
| SMPS +V → FB1 input | 21.6 A | **12 AWG** |
| F1 → Jetson barrel plug (5.5 × 2.5 mm, centre +) and return | 3.8 A | 18 AWG |
| F2 → base adapter A1 screw terminal and return | 10.8 A | 14 AWG |
| F3 → buck IN+ and buck IN− → SMPS COM | 7 A | 14 AWG |
| buck OUT+ → FB2 input | 8.6 A | 14 AWG |
| F5 → follower adapter A3 and return | 8 A | 14 AWG |
| F4 → leader adapter A2 and return | 0.6 A | 20 AWG |
| AC inlet → SMPS (L, N, PE) | – | 0.75 mm² (18 AWG) |
| Servo leads (Molex 5264, GND / VCC / SIG) | 2.7 A | 22 AWG |

Rules:

- Do not daisy-chain grounds from board to board. USB cables must never become the return path for motor current.
- Feed the servo adapter boards through their **screw power terminal**, not the barrel jack (5 A class part).
- Keep the wheel servos on **two chains** (port 1 → 7 → 9, port 2 → 8 → 10) so no Molex 5264 contact carries more than two servos.
- Keep AC wiring away from servo and USB harnesses; insulate every spade terminal with heat-shrink.

---

## 7. Mechanical packaging

- **Lower basket:** one 3D-printed base plate (`3d_models/print_files/base_plate_*.3mf`) holds the SMPS (flat, fan up, on slotted
  ear pads), Jetson (10 mm standoffs), FB1, FB2, the buck and the AC inlet tower (inlet lower edge 67 mm
  above the plate so the cord clears the basket rim). Honeycomb cut-outs give airflow from the basket's mesh floor.
- **Middle floor:** the ST Lab USB hub sits in its own printed tray (`3d_models/print_files/usb_hub_tray.3mf`), next to the devices it serves.
- Riser cables (12 V wheels, 5 V arms, USB) leave the plate at the left rear corner towards the upper floors.

---

## 8. Bring-up checklist

1. AC side only: inlet, SMPS. Check the 220 V switch. Power on, set the SMPS to 12.0–12.3 V. Power off.
2. Wire FB1 with **no fuses fitted**. Wire the buck and FB2. Fit F3, power on, check the buck output 5.0–5.2 V on FB2's input.
3. Fit F1. Connect the Jetson. Boot and check the desktop and `lsusb -t`.
4. Fit F4. Connect the leader adapter. Servo tester: leader servos read 5.0–5.2 V.
5. Fit F5. Connect the follower adapter. Run teleop for a minute and watch servo temperatures.
6. Fit F2. Connect the wheel board. Servo tester: wheels 12.0–12.4 V. Run `mecanum_test.py` with the robot on blocks, then on the floor.
7. Clamp-meter the SMPS output during the full demo and record the peak and the final set points.

Power-up order: mains on → Jetson boots → wait for the desktop → start software.
Shutdown: stop software (torque off) → shut down the Jetson → mains off.

---

## 9. Planned upgrades (not in this build)

| Upgrade | What it adds | Notes |
|---|---|---|
| Hardware E-stop | mushroom NC switch + 12 V 40 A automotive relay cutting the wheel and follower rails | Jetson, hub and leader stay powered; add a key switch to arm the motors |
| 7.2 V follower rail | more follower torque | separate 8–12 A buck set to 7.2 V, bulk capacitor 1000–2200 µF at the adapter; must stay below the 8.0 V servo limit |
| Second leader / follower pair | full dual-arm teleop | each extra arm adds one adapter and one fuse; re-check the 5 V budget (the 15 A buck covers two followers at design load only) |
| Battery | untethered operation | regulated 12 V power station or 3S Li-ion with BMS; 4S LiFePO4 only with a regulator (14.6 V exceeds the wheel servo limit) |
