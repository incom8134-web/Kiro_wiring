# Assembly instructions: EV battery design (Rev A)

Do not build before the battery and charger are identified. See `verification_report.md`.

## Safety

A 45 Ah battery can deliver hundreds of amperes into a short circuit. Fit F1 first, within 150 mm of the positive
terminal. Disconnect the battery negative before any wiring work. Remove rings and watches. Insulate tools.

## Order of work

1. Mount the negative bus bar next to the battery. Mount F1, SW1, K1, U3, both fuse boxes and the EA75-5V buck on the
   power plate. Keep the battery to fuse box 1 path short.
2. Wire the main path with 8 AWG: battery + -> F1 -> SW1 -> battery bus -> K1 -> U3. Then U3 -> fuse box 1 with 10 AWG.
3. Wire the returns: one wire from every load and converter to the negative bus bar. Battery - to the bus bar last.
4. Wire the unswitched branches from the battery bus: F3 to the Jetson lead, F4 to the buck, F5 to the E-stop loop.
5. Wire the buck output to fuse box 2. Label fuse box 2 "5 V ONLY".
6. Wire the E-stop loop: F5 -> S1 (NC) -> START in parallel with K1 aux -> coil A1; A2 to the bus bar. Fit D1 across
   the coil with the cathode to A1.
7. Wire fuse box 1 to the three adapter screw terminals with 14 AWG and ferrules.
8. Wire the charger inlet through F2 to the battery side of SW1.
9. Leave every load fuse out and follow the bring-up order in `verification_report.md` section 3.

## Arm servo change

Follow `arm_servo_12v_notes.md`. Do not connect an arm adapter to fuse box 1 while any 7.4 V servo is still on that bus.

## Power-up and shutdown

- Power-up: SW1 on -> Jetson boots -> software starts -> release S1 -> press START.
- Shutdown: stop motion -> torque off -> press S1 -> shut down the Jetson -> SW1 off.
- Charging: SW1 off, then connect the charger.
