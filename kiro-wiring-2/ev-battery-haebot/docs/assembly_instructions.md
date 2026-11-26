# Assembly instructions: EV battery design (Rev B, 2026-11-26)

Wiring is proposed. Identify the battery/charger and verify K1 continuous coil duty, coil current/voltage envelope,
polarity, main contact breaking rating and approved suppression before connecting battery power.

## Installation

1. Mount F1 within 150 mm of battery positive, SW1, U6 Matek monitor, K1, U3, both fuse boxes, EA75-5V and the
   negative star bus on the power plate. Disconnect the battery while assembling; insulate studs.
2. Main positive: BT1 -> F1 -> SW1 -> U6 BAT+ -> U6 ESC+ -> battery distribution. Use 8 AWG as the preliminary
   main cable choice. Support and insulate the Matek high-current solder joints; its JST is not the main-current path.
3. Motion positive: battery distribution -> K1 large main studs -> U3 input; U3 regulated 12.0 V output -> FB1.
   Preserve 8 AWG to U3 and 10 AWG after U3 provisionally. All three motor branches must be downstream of K1.
4. Wire each load return separately to the negative star bus, with feed-matched cable. Connect battery negative last.
5. Keep F3 -> Jetson and F4 -> EA75-5V on the distribution before K1. Buck output goes to FB2, labelled 5 V ONLY.
6. Use one positive-opening **NC, mechanically latching, push-to-lock / twist-to-release E-stop S1**. Fit it on an
   accessible external panel clear of the arm sweep. Wire battery distribution -> F5 -> S1 NC -> K1 coil positive;
   K1 coil negative -> POWER_GND. Identify polarity from the actual device. No START, auxiliary holding contact,
   reset controller or software is in the coil circuit. The 2 A F5 value and 20 AWG cable remain preliminary.
7. Fit only suppression approved for the actual coil; D1 is a placeholder pending that check. Do not assume the
   old 1N4007 fits or duplicate internal suppression. Check opening time as well as transient voltage.
8. FB1 branches: F11 -> wheel adapter, F12 -> arm 1 adapter, F13 -> arm 2 adapter, using their screw-terminal inputs.
   Both arms use new 12 V servos. Keep the existing 7.4 V servos off this rail.
9. FB2 F23 -> J5 AUX_5V -> U6 5V; U6 G -> POWER_GND. Measure regulated 5 V first. Check the JST cable rating
   against F23 before fitting it. Preserve the hub branches pending their voltage/plug identification.
10. U6 SDA/SCL -> Jetson GPIO/I2C interface only after header pins, bus, signal voltage/pull-ups and the actual
    INA228/INA238 variant/driver are confirmed. There is no validated Jetson pin-to-pin hookup yet.
11. Keep J2 charger -> F2 -> battery side of SW1. Charge only with SW1 open; this charge path bypasses U6.
12. Leave load fuses out and perform the bring-up checks in `verification_report.md`.

## Operation

| Condition | Effect |
|---|---|
| SW1 off | Robot distribution off; charger inlet remains on the battery side |
| SW1 on, S1 pressed/locked | Jetson, 5 V rail and monitor on; motion contactor off |
| S1 released | K1 coil continuously powered and motion rail enabled |
| Push S1 | NC opens; K1 opens; wheels and both arms lose motor power |
| Let go of pressed S1 | Mechanical latch keeps motor power off indefinitely |
| Twist S1 to release | NC closes; motor power returns immediately, without a START button |

Power-up: press/lock S1 -> SW1 on -> boot Jetson -> clear commands and establish a safe state -> deliberately twist S1
to enable motion power. Shutdown: stop motion -> support arms -> press S1 -> shut down Jetson -> SW1 off.

There is **no restart interlock**: SW1 on with S1 released, or release after a stop, restores motor power. Power
restoration can cause movement. Torque disappears when power is cut, so arms can fall. This single-contactor
prototype does not detect welded main contacts and is not a validated functional-safety system.
