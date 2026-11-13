# Power distribution and protection: Anker design (Rev B)

## 1. Verified Anker SOLIX C300 DC limits

Model: **Anker SOLIX C300 DC, A1726**, 288 Wh (90,000 mAh), LiFePO4, 300 W total DC output. Source: Anker user manual
A1726 and the Anker product page (links in `verification_report.md`).

| Port | Output | Max |
|---|---|---|
| USB-C1 | 5 V 3 A / 9 V 3 A / 15 V 3 A / 20 V 5 A | 100 W |
| USB-C2, USB-C3 (also inputs) | 5 V 3 A / 9 V 3 A / 15 V 3 A / 20 V 5 A / 28 V 5 A | 140 W each |
| USB-C4 | 5 V 3 A | 15 W |
| USB-A1, USB-A2 | 5 V 2.4 A | 12 W each |
| USB-A1 + USB-A2 + USB-C4 together | 5 V 4 A | 20 W |
| Car socket | 12 V 10 A (10.8-14 V on the C300X DC datasheet) | 120 W |
| All outputs |  | 300 W |

The manual lists **no 12 V USB-C profile and no PPS**. A 12 V PD trigger on this station will not deliver 12 V.

Power sharing when several ports are in use (manual, "USB Power Distribution Table"):

| Ports in use | Power per port |
|---|---|
| USB-C2/C3 + car socket | 140 W + 120 W |
| USB-C1/C2/C3 + USB group + car socket | 100 or 140 W + 20 W + 120 W |
| USB-C1 + USB-C2/C3 + car socket | 100 W + 100 W + 120 W |
| **USB-C1 + USB-C2/C3 + USB group + car socket (this design)** | **30 W + 100 W + 20 W + 120 W** |
| USB-C1 + USB-C2 + USB-C3 + USB group + car socket | 30 W + 60 W + 60 W + 20 W + 120 W |

"USB group" = USB-A1, USB-A2 and USB-C4. Some rows of the manual's table look inconsistent with the per-port ratings.
Confirm the 4-port row on the bench before relying on it.

## 2. Branch assignment

| Branch | Requested | Drawn in Rev B | Why it differs | Status |
|---|---|---|---|---|
| A hubs | 2 x USB 5 V -> hub 1, hub 2 | USB-A1 -> hub 1, USB-A2 -> hub 2 through USB-A to DC leads | same | Blocked: hub input voltage and plug not recorded; hub 2 is not in the records |
| B arm 1 | USB-C -> 5 V -> arm 1 | USB-C4 (5 V 3 A) -> USB-C 5 V lead -> F4 3 A -> K1 -> adapter | limited to a leader / torque-off arm | Proposed |
| C arm 2 | USB-C PD -> 5 V trigger -> arm 2 | USB-C1 -> **20 V** trigger -> EA75-5V buck -> F2 15 A -> K1 -> adapter | 5 V over USB-C is 3 A max; a follower needs 5 A design, 8 A burst | Proposed |
| D wheels | USB-C PD -> 12 V trigger -> driver | USB-C2 -> **20 V** trigger -> 12.0 V buck -> F1 15 A -> K1 -> adapter | the station has no 12 V profile | Proposed |
| E Jetson | car socket -> Jetson | car socket -> fused plug lead -> F5 5 A -> DC jack | same; no boost needed | Proposed lead, verified voltage range |

### Why the Jetson needs no boost converter

The brief names 19 V. That is the voltage of the bundled adapter. The V1 records give the developer-kit DC jack as
**9-20 V** and V1 Rev F runs the same Jetson from its 12 V rail through a 5 A fuse. The car socket (10.8-14 V) is inside
that range. Confirm that the installed carrier is the stock developer-kit carrier (P3768) before first power-up.

## 3. Protection

| Ref | Value | Protects | Basis |
|---|---|---|---|
| Station ports | internal | each output | Anker over-current protection (verified to exist; trip values not published) |
| F1 | 15 A blade | 12 V wheel branch, 14 AWG | V1 F2 |
| F2 | 15 A blade | 5 V follower branch, 14 AWG | V1 F5 |
| F3 | 1 A | E-stop loop, 20 AWG | calculated from a 3 W coil allowance |
| F4 | 3 A blade | 5 V leader branch | port limit 3 A; V1 used 2 A |
| F5 | 5 A | Jetson lead, 18 AWG | V1 F1 |
| Car plug fuse | <= 10 A | plug lead | socket limit |
| D1 | 1N4007 | K1 coil switch-off spike | V1 parts list |

Motor transients: the ST3215 servos brake into their supply rail. A PD source cannot absorb reverse current, so the
buck output (U3) needs a bulk capacitor of 1000-2200 uF / 25 V at the wheel adapter. V1 lists the same part for the arm
rail. Rating and position are **Proposed**.

## 4. Emergency stop

- Hardware only: `DRIVE_12V -> F3 -> S1 (NC) -> START || K1 aux -> K1 coil -> GND_C2`.
- K1 has three power poles: pole 1 opens the 12 V wheel branch, pole 2 opens the 5 V arm 2 branch, pole 3 opens the
  5 V arm 1 branch. One press of the mushroom button removes power from the wheels and both arms at the same time.
- The Jetson and the hubs stay powered.
- Releasing S1 does not restart anything. START must be pressed.
- The follower arm drops under gravity when K1 opens (V1 record). People near the robot must know this.
- If USB-C2 is off, K1 cannot close, so neither arm can be powered without the wheel rail. This is intended.
- Rev B change (2026-11-13): arm 1 was added to the E-stop. Rev A switched only the wheels and arm 2.

## 5. Grounds and cross-connections

- Never join the positive wires of two ports. Each branch is a separate two-wire circuit.
- The negatives of all ports become common anyway, through the USB shields of the servo adapters and hubs. Whether the
  station ties its port negatives together internally is **not verified**.
- Motor current must return on its own pair to its own source, never through a USB cable.
- Plugging or unplugging any port can make the station renegotiate USB-PD on the others. Expect a short dropout on the
  trigger outputs. Connect everything first, then switch the outputs on, then arm K1.

## 6. Recommended alternative (not drawn)

Feed the EA75-5V arm buck from the **car socket** next to the Jetson (through a fused 2-way splitter) and drop PD1.
Then only USB-C2, the USB group and the car socket are in use, and the manual's 3-port row gives USB-C2 the full
**140 W**. Car socket load: Jetson 45 W peak + arm buck 49 W peak = 94 W of 120 W. This gives the wheels 40 % more
power and the follower its full burst current, with one PD trigger less. It moves arm 2 off USB-C, so it is listed here
for your decision and the requested port layout stays on the drawing.
