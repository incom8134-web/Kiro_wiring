# Assembly instructions: Anker design (Rev A)

Do not start before the bench checks in `verification_report.md` section 4 are done. Work with every station output
switched off.

## Tools

Multimeter, USB-C power meter, ferrule crimper, small screwdrivers, heat-shrink, labels.

## Order of work

1. **Jetson branch (E).** Check the polarity of the car-plug lead (centre positive). Fit F5 (5 A). Plug into the car
   socket, switch the socket on, measure 10.8-14 V at the barrel plug, then connect the Jetson and boot it.
2. **Hub branch (A).** Only after the hub label confirms a 5 V input. Connect hub 1 to USB-A1 with the USB-A to DC lead.
   Connect the hub's upstream cable to Jetson USB port 3. Check `lsusb -t`.
3. **Arm 1 branch (B).** Connect the USB-C 5 V lead to USB-C4 and measure 5 V at its screw terminal. Fit F4 (3 A). Wire
   to the arm 1 adapter screw terminal. Servo tester: leader servos read about 5 V.
4. **Arm 2 branch (C).** PD1 on USB-C1: measure 20 V. Wire PD1 to the EA75-5V input. Measure 5.0-5.2 V at its output
   **before** connecting anything else. Then F2 (15 A), K1 pole 2, arm 2 adapter. Label this rail "5 V ONLY".
5. **Wheel branch (D).** PD2 on USB-C2 with a 5 A e-marked cable: measure 20 V. Set the buck U3 to 12.0 V with no load.
   Then F1 (15 A), K1 pole 1, wheel adapter, bulk capacitor at the adapter terminal (observe polarity).
6. **E-stop loop.** Wire F3, S1, START, K1 aux and coil, D1 across the coil with the cathode to A1. Test the loop with
   the load fuses F1 and F2 removed.
7. Fit F1 and F2. Press START. Run the servo tester on the wheels (12.0-12.4 V) and on arm 2 (about 5 V).
8. Drive on blocks first. Watch the station display for port power.

## Power-up and shutdown

- Power-up: all leads connected -> station outputs on -> Jetson boots -> software starts -> release S1 -> press START.
- Shutdown: stop motion -> torque off -> press S1 -> shut down the Jetson -> station outputs off.
- Do not plug or unplug a port while the robot is armed. The station may renegotiate the other outputs.

## Cable care

- Strain relief on both ends of every lead. No lead may hang on a USB-C plug.
- Keep the 12 V wheel pair away from the lidar and USB data cables.
- Mount the station so the output buttons and the display stay reachable.
