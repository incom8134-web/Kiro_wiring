# As-built wiring and power-up: Anker design (Rev C)

[English](assembly_instructions.md) | [한국어](assembly_instructions.ko.md)

**AS BUILT per builder report, 2026-11-16. Not independently measured.**
This is how the robot is wired. It is not a procedure for fitting the Rev B bucks or the car-socket lead. Those parts are not on the robot.

Work with every station output switched off until the step says otherwise. The open measurements are in `verification_report.md` section 4. Hub 1 stays unpowered until its label is read.

## Tools

Multimeter, USB-C power meter, ferrule crimper, small screwdrivers, heat-shrink, labels.

## What is fitted

1. **Wheels and Jetson (USB-C2).** USB-C cable into the PD trigger. The builder measured 12 V at the trigger output. The manual lists no 12 V USB-C profile, so confirm 12 V with a meter and do not trim the trigger upward (wheel servos max 12.6 V). OUT+ into the Dorhea 4-way box. F1 15 A then K1 pole 1 (pins 1-2) to the wheel adapter screw terminal. F5 5 A, taken before K1, to the Jetson DC jack, 5.5 x 2.5 mm, centre positive. Both returns go to the trigger OUT-. Two fuse slots stay empty. There is no negative bus and no bulk capacitor.
2. **Arm 2 (USB-C1).** 5 V PD trigger, then K1 pole 2 (pins 3-4), then the arm 2 adapter screw terminal. No buck and no extra fuse. Label the rail "5 V ONLY". The port gives 3 A. The follower design load is 5 A and the burst is 8 A, so the arm will current-limit before the servos reach design torque.
3. **Arm 1 (USB-A1).** USB-A to DC jack lead, straight into the arm 1 adapter DC jack. No fuse. This lead is not on K1, so arm 1 stays powered through an E-stop. Leader current is about 0.3 A.
4. **Hub 1 (USB-A2).** A USB-A to DC lead is the intended feed. **BLOCKED** until the hub input is known to be 5 V. Do not plug it in on the strength of this drawing.
5. **Hub 2.** No power port is assigned. **BLOCKED.** Its USB upstream cable may still go to Jetson USB-A4.
6. **E-stop.** DRIVE_12V, from the trigger output ahead of K1, through a fuse (drawn as F3, 1 A; the builder did not state the rating), through S1 normally closed, then START in parallel with the K1 auxiliary contact, to the coil. Flyback diode cathode on A1, anode on A2, if D1 is fitted. Confirm that diode before relying on the coil.
7. **Left unused.** USB-C3 (keep it free for recharging), USB-C4, and the car socket.

USB data is separate. Orbbec on Jetson USB-A1, wrist webcam on USB-A2, hub 1 upstream on USB-A3, hub 2 upstream on USB-A4. Servo-adapter USB cables go to hub 1 and are not the servo power feed.

## Power-up and shutdown

- Power-up: all leads connected and the hub lead left off if the label is still unread -> station outputs on -> confirm about 12 V at the wheel trigger and 5 V at the arm 2 trigger -> Jetson boots -> software starts -> release S1 -> press START. K1 cannot close if USB-C2 is off, so arm 2 comes up only with the wheel rail. Arm 1 can be live from USB-A1 before START.
- Shutdown: stop motion -> torque off -> press S1 (wheels and arm 2 drop; arm 2 can fall under gravity) -> shut down the Jetson, which is still powered -> station outputs off.
- Do not plug or unplug a port while the robot is armed. The station may renegotiate the other outputs.
- Do not join a positive of one port to a positive of another.

## Cable care

- Strain relief on both ends of every lead. No lead may hang on a USB-C plug.
- Ferrules on the wheel and arm 2 screw terminals.
- Keep the 12 V pair away from the lidar and the USB data cables.
- Mount the station so the output buttons, the display and the E-stop stay reachable.
- One USB-C port feeds the wheels and the Jetson. A usual 12 V USB-C contract is 3 A (36 W). The two loads together are about 3.5 A typical and 9.3 A design, including the coil. Expect the 12 V rail to sag or cut out, and expect a Jetson brown-out when it does.
