# Power distribution and protection: Anker design (Rev C)

**AS BUILT per builder report, 2026-11-16. Not independently measured.**

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

The manual lists **no 12 V USB-C profile and no PPS**. Rev C still uses a PD trigger set to 12 V on USB-C2, because the builder measured 12 V there. That measurement is not a manual rating, and it does not say how much current the port will hold. Treat a usual USB-C 12 V contract as 3 A / 36 W until a meter says otherwise.

Power sharing when several ports are in use (manual, "USB Power Distribution Table"):

| Ports in use | Power per port |
|---|---|
| USB-C2/C3 + car socket | 140 W + 120 W |
| USB-C1/C2/C3 + USB group + car socket | 100 or 140 W + 20 W + 120 W |
| USB-C1 + USB-C2/C3 + car socket | 100 W + 100 W + 120 W |
| USB-C1 + USB-C2/C3 + USB group + car socket | 30 W + 100 W + 20 W + 120 W |
| USB-C1 + USB-C2 + USB-C3 + USB group + car socket | 30 W + 60 W + 60 W + 20 W + 120 W |

"USB group" = USB-A1, USB-A2 and USB-C4. This robot uses USB-C1, USB-C2, USB-A1 and USB-A2. It does not use USB-C3, USB-C4 or the car socket, so none of the rows is an exact match. The 100 W and 140 W figures are for 20 V and 28 V contracts. They are not a licence to draw 9 A at 12 V from USB-C2.

## 2. Branch assignment

| Branch | Rev B proposal | As built, Rev C | Status |
|---|---|---|---|
| A hub 1 | USB-A1 -> DC lead | USB-A2 -> USB-A to DC lead -> hub 1 | BLOCKED: hub input voltage unknown |
| A hub 2 | USB-A2 -> DC lead | no power port assigned | BLOCKED |
| B arm 1 | USB-C4 -> fuse -> K1 -> screw terminal | USB-A1 -> USB-A to DC jack lead -> adapter DC jack. No fuse. Not on K1 | AS BUILT |
| C arm 2 | USB-C1 -> 20 V trigger -> EA75-5V -> F2 -> K1 | USB-C1 -> 5 V PD trigger -> K1 -> adapter. No buck | AS BUILT. 3 A source vs 5 A design / 8 A burst |
| D wheels | USB-C2 -> 20 V trigger -> 12 V buck -> F1 -> K1 | USB-C2 -> 12 V PD trigger -> FB1 -> F1 15 A -> K1 -> adapter | AS BUILT. 12 V is a builder measurement |
| E Jetson | car socket -> fused plug -> DC jack | FB1 F5 5 A, taken before K1, -> Jetson DC jack | AS BUILT. Stays on after E-stop |
| spare | USB-C3 free for recharge | USB-C3, USB-C4 and the car socket unused | AS BUILT |

### Why the Jetson has no boost converter

The V1 records give the developer-kit DC jack as **9-20 V**, and V1 Rev F runs the same Jetson from 12 V through a 5 A fuse. The as-built 12 V trigger is inside that range. Confirm the installed carrier is the stock developer-kit carrier (P3768) if it has not already been confirmed on this robot.

## 3. Protection

| Ref | Value | Protects | Basis |
|---|---|---|---|
| Station ports | internal | each output | Anker over-current protection (it exists; trip values are not published) |
| FB1 | Dorhea 4-way, V1 | 12 V from P02. Slots: F1, F5, two spare | V1 hardware. No negative bus. Returns go to P02 OUT- |
| F1 | 15 A blade | 12 V wheel branch | V1 wheel fuse |
| F5 | 5 A | Jetson, ahead of K1 | V1 Jetson fuse |
| F3 | 1 A drawn | E-stop loop | Calculated from a 3 W coil allowance. The builder reported a fuse and did not state the rating |
| D1 | 1N4007 | K1 coil switch-off spike | On the Rev C schematic, cathode to A1. Confirm it is on the coil |

There is no fuse on arm 1 and no fuse on arm 2 beyond the station port. Arm 1 current is about 0.3 A on a 2.4 A port. Arm 2 is already limited by the 3 A PD contract, which is below the wire and the servo design current.

The Rev B bulk capacitor on the wheel buck is not fitted. The PD trigger cannot absorb servo braking current. No capacitor was reported. Wheel-rail sag under hard braking is unmeasured.

## 4. Emergency stop

- Hardware only: `DRIVE_12V -> F3 -> S1 (NC) -> START || K1 aux -> K1 coil -> GND_C2`.
- K1 has two power poles. Pole 1 opens the 12 V wheel branch. Pole 2 opens the 5 V arm 2 branch. The third pole from Rev B is not fitted.
- One press cuts the wheels and arm 2. The Jetson, the hubs and arm 1 stay powered. Arm 1 stays live on USB-A1 through an E-stop.
- Releasing S1 does not restart anything. START must be pressed.
- Arm 2 drops under gravity when K1 opens (V1 record). People near the robot must know this.
- If USB-C2 is off, K1 cannot close, so the wheels and arm 2 stay off together. Arm 1 can still be powered from USB-A1. The Jetson is also off, because it shares USB-C2.
- Rev B (2026-11-13) switched wheels, arm 2 and arm 1 together. Rev C does not switch arm 1. That is the as-built circuit, and it is a warning, not a proposal to add the third pole back.

## 5. Grounds and cross-connections

- Never join the positive wires of two ports. Each branch is its own pair.
- The negatives of all ports become common through the USB shields of the servo adapters and the hubs. Whether the station ties its port negatives together internally is not verified.
- Motor current returns on its own pair to its own source, not through a USB cable. The wheel and Jetson returns land on P02 OUT-, because FB1 has no negative bus.
- Plugging or unplugging a port can make the station renegotiate USB-PD on the others. Connect everything, then switch the outputs on, then arm K1.

## 6. What Rev B no longer is

Rev B put a 20 V trigger and a 12 V buck on the wheels, a 20 V trigger and the EA75-5V buck on arm 2, the Jetson on the car socket, and arm 1 on USB-C4 through the third K1 pole. None of that is fitted. Do not put those parts back onto this robot to "match the old drawing." The as-built limits in sections 2 and 4 are the ones to design around.
