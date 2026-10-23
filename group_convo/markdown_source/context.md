# Kiro Robot Project – Context

Written 2026-10-22 from the project records on this Jetson (`~/so101` repository, its `CLAUDE.md`,
`docs/`, the company handover package of 2026-10-15, and the Claude Code session history).
Purpose of this folder: plan the **rewiring of the robot's power system** (one SMPS + buck converters
instead of a pile of wall adapters) and give the company/students a clear picture of the machine.

Naming note: in the records "Kiro" (키로) is the company-side group for which the robot and the
student curriculum are being prepared. The robot itself is called **SO-101 mobile dual-arm robot**
in the repository and the handover documents. Both names refer to the same project.

---

## 1. What the project is

An **XLeRobot-style mobile manipulator** built around one NVIDIA Jetson Orin Nano 8 GB:

- two **SO-101 leader arms** (moved by hand) and two **SO-101 follower arms** (copy the leaders),
- a **mecanum-wheel base** driven by four Feetech ST3215-C018 bus servos,
- an **Orbbec Gemini 335** RGB-D camera (top view) and a **Suyin USB webcam** on the right wrist,
- a **Slamtec RPLIDAR C1** 2D lidar (tested, not yet mounted),
- a USB gamepad for driving the base.

Use cases: leader-follower teleoperation, recording imitation-learning datasets (LeRobot 0.6.1, ACT policy),
driving the base (ROS 2 Jazzy), and later autonomous navigation (SLAM / Nav2).
The robot is also the platform for a **student curriculum (교안)** requested by the company; the
students are meant to modify the data-collection and training parts of the code.

### People and milestones

| Date | Event |
|---|---|
| 2026-09-07 | Dual-arm teleoperation working (one process per arm), udev fixed names, GUI control panel |
| 2026-09-15 | AMR extension reviewed: mecanum + Gemini 335 + RPLIDAR C1 + ST3215-C018, LeRobot upgraded to 0.6.1 |
| 2026-09-16 | Wheel servos ID 7–10 assigned, wheel board registered as `/dev/so101_base`, 12 V 6 A bench adapter |
| 2026-09-19 | Base mounted on chassis, 2-chain wiring, floor driving verified (forward, strafe, rotate), gamepad teleop |
| 2026-10-12 | Progress report to the company, USB hub replaced by VIA VL815, arms confirmed running on 5 V |
| 2026-10-15 | Technical handover package `SO101_기술자료_2026-10-15.zip` delivered (system, code, training, interfaces, Q&A) |
| 2026-10-21 | Live demo for the company at 16:00, zero-base install of a spare Jetson, hardware test wizard, right-arm data collection prepared |
| 2026-10-22 | **This folder: power rewiring plan (SMPS + buck converters)** |

Owner/developer: 이상원 (Donghwa University, student researcher). Company side: Kiro (client group) and
Indi Solution (curriculum coordinator). Standing project rules from the records: keep `CLAUDE.md` updated,
commit helpful changes, never push (no remote), the user runs `sudo` steps themselves.

---

## 2. Hardware inventory (as of 2026-10-21)

| Item | Model | Qty | Key facts | Identification |
|---|---|---|---|---|
| Main computer | NVIDIA Jetson Orin Nano Super Developer Kit, 8 GB | 1 | JetPack 7.2.1, Ubuntu 24.04, CUDA 13.2, power mode **MAXN SUPER**, Samsung 990 1 TB NVMe boot | bundled 19 V barrel adapter |
| Spare computer | Jetson Orin Nano dev kit (unopened) + 1 TB NVMe | 1 | zero-base install done 2026-10-21 via Jetson ISO | – |
| Follower arms | SO-101 Follower | 2 | 6 × STS3215 each (ID 1–6). **7.4 V type: Max_Voltage_Limit 8.0 V** (register read). Run on 5 V so far (5.2–5.3 V measured) | `/dev/so101_left_follower` S/N 5B3D048978, `/dev/so101_right_follower` S/N 5B14111917 |
| Leader arms | SO-101 Leader | 2 | 6 × STS3215 each, torque off, position read only. Mixed limits (ID 2 = 8.0 V, others 12.0 V) | `/dev/so101_left_leader` S/N 5B14029523, `/dev/so101_right_leader` S/N 5B14113246 |
| Wheel servos | Feetech ST3215-C018 (12 V, 30 kg·cm, 1:345) | 4 | input 7.4–12.6 V nominal, Max_Voltage_Limit 14.0 V, stall 2.7 A each, velocity mode | IDs FR 7, FL 8, RR 9, RL 10 on `/dev/so101_base` S/N 5B3E091473 |
| Servo bus adapters | CH343 USB-UART boards (USB 1a86:55d3, "USB Single Serial") – most likely Waveshare Bus Servo Adapter (A): 2 servo ports, DC jack 5.5×2.1 mm, screw power terminal | 5 | one adapter = one TTL half-duplex bus at 1 Mbps. Logic is USB powered; the power terminal only feeds the servo VCC pins | serial-number based udev links above |
| RGB-D camera | Orbbec Gemini 335 | 1 | USB 3.2 Gen1, bus powered, bMaxPower 896 mA, peak < 6.5 W, colour 1280×720 + depth 848×480 @ 30 fps | S/N CP0F46300035, fw 1.4.60, body port 1 |
| Wrist camera | Suyin HD webcam (1e45:8022) | 1 (+1 planned left) | needs 500 mA; **unpowered hubs reject it**, body port works | body port 2 |
| 2D lidar | Slamtec RPLIDAR C1 + CP2102N adapter | 1 | 5 V, 230 mA / 1.15 W typical, UART 460800, `/scan` 10 Hz 720 pts | `/dev/rplidar`, on the hub |
| USB hub | VIA VL815 USB 3.0, self-powered (own adapter) | 1 | replaced a Genesys 05e3:0608 hub that failed to enumerate the serial boards | body port 3 |
| Gamepad | cheap USB pad in Xbox 360 XInput mode (045e:028e) | 1 | `/dev/input/js0`; currently on the hub (worked after the VL815 swap) | – |
| Power (today) | 19 V Jetson adapter, 5 V adapter(s) for the arm boards, 12 V 6 A adapter for the wheel board, hub adapter | – | see section 3 | – |

Servo joint order on every arm bus: 1 shoulder_pan, 2 shoulder_lift, 3 elbow_flex, 4 wrist_flex, 5 wrist_roll, 6 gripper.
All servos are model 777 (STS3215 family), firmware 3.10, 4096 steps per turn, protocol 0 (little-endian).

---

## 3. Current power architecture (as-is, before rewiring)

Power is split into **three buses plus the hub**, each with its own wall adapter:

| Bus | Current source | Load and measured values | Rules learned |
|---|---|---|---|
| Arm servos (4 arms, 24 servos) | 5 V adapter(s) into the arm boards' DC jacks | teleop works at 5 V, Present_Voltage 5.2–5.3 V | **Followers must never see 12 V** (limit 8.0 V). A 7.4 V supply gives more torque but was not required |
| Wheel servos (4) | 12 V 6 A adapter (bench use only) | no-load 46–176 mA per wheel, floor driving a few hundred mA per wheel, servo voltage 12.2–12.4 V, 27–30 °C | 4-wheel stall ≈ 10.8 A exceeds 6 A; a 12 V 10 A class supply or battery was already planned |
| Jetson | bundled 19 V adapter | MAXN SUPER mode | if the Jetson reboots when the camera is plugged, suspect the adapter first |
| USB hub | own adapter (voltage not recorded – check the label) | powers 5 serial boards' logic, lidar, gamepad, dongle | power the hub before plugging devices |

Other electrical facts already established:

- All grounds are already common because every servo board and sensor is connected to the Jetson by USB.
- The servo connector is **Molex 5264 (2.5 mm pitch) 3-pin**, pin order **GND / VCC / SIGNAL**, contacts rated about **3 A** with 22 AWG.
  Four wheel servos in one daisy chain would overload the first connector, so the base is wired as **two chains**:
  board port 1 → ID 7 (FR) → ID 9 (RR), board port 2 → ID 8 (FL) → ID 10 (RL).
- The adapter board's barrel jack is a 5 A class part; **10 A must go through the screw terminal**, not the jack.
- A paper that ran XLeRobot on the same Orin Nano reported a **brown-out (12.2 V collapsing to 0.3 V)** when wheels, arms and Jetson shared one line, and fixed it by separating the buses.
- The lidar is 5 V only: never near 12 V wiring, sensor cable connected only with USB unplugged.
- Gemini 335 goes straight into a Jetson USB 3 port with the bundled cable; never through a hub or a charging cable.
- Software voltage guards: `arm_tuck.py` and the mode tester treat a servo voltage below 4.5 V as "power off" and refuse to move.
- No hardware emergency stop exists yet (listed as "planned" in the handover package).

### USB layout (2026-10-21)

| Jetson body port | Device |
|---|---|
| 1 | Orbbec Gemini 335 (USB 3, 5 Gbps) – top view camera |
| 2 | Suyin wrist webcam (right arm) |
| 3 | VIA VL815 hub → 5 × CH343 servo boards, RPLIDAR C1 adapter, gamepad, keyboard dongle |
| 4 | free |

The four body ports share one on-board Realtek hub (USB 3 and USB 2 bandwidth shared).

---

## 4. Software that touches power or safety

- **LeRobot 0.6.1** (venv `~/lerobot-venv`): `lerobot-teleoperate` 60 Hz, `lerobot-record` 30 Hz; followers torque on, position mode, P16/I0/D32; gripper torque limited to 50 %. Torque is released on disconnect, so **followers fall under gravity when stopped**.
- **ROS 2 Jazzy** (`~/ros2_ws`, package `so101_base`): `mecanum_base_node` at 20 Hz; velocity limits 0.3 m/s and 1.5 rad/s; watchdog sends zero velocity 0.5 s after the last `/cmd_vel`; torque off on SIGINT; refuses to start if any wheel servo does not answer a ping.
- GUIs: control panel, servo tester (shows voltage, current, temperature live), mode tester (mode A record / mode B drive with pre-checks), hardware test wizard, camera test, record GUI.
- udev rules bind every serial board to its USB serial number, so USB ports can be moved freely.

---

## 5. Goal of the rewiring

1. Replace the separate wall adapters with **one mains SMPS** and derive the other rails with **buck converters**.
2. Give every rail a **fuse**, proper **wire gauge** and connectors, and a **hardware E-stop** for the motion rails.
3. Supply the followers at their proper **7.4 V class voltage** (set to 7.2 V) instead of 5 V, giving more torque while staying below the 8.0 V servo limit.
4. Keep the Jetson, the hub, the lidar and the leaders on a rail that is **not** cut by the E-stop, so the computer survives a stop.
5. Keep the design **battery-ready**: a 12 V main bus lets a regulated 12 V power station (XLeRobot uses an Anker SOLIX C300) replace the SMPS later without any other change.

The result of this task is in the companion files (all in this folder):

- `Kiro_SO101_Power_System_Design_RevA.docx` – the complete design package: context, calculations, schematics (5 sheets), designator and net lists, cable schedule, parts list, image sources
- `context.docx`, `power_calculation.docx`, `parts_list.docx`, `README.docx` – the individual documents as Word files
- `diagrams/schematic_sheet1..5.png|svg` – electrical schematics (sheet 1 AC input and distribution, 2 Jetson and follower rails, 3 logic rail, 4 wheel rail, 5 connector pinouts); source `schematic.py` (schemdraw)
- `diagrams/block_diagram.png`, `power_diagram.png`, `power_diagram_tb.png`, `wiring_diagram.png` – Graphviz overview diagrams with `.dot` sources
- `images/web/` – downloaded reference photos with `sources.json` (origin and licence of every image)
- `markdown_source/` – the original Markdown text of the documents

---

## 6. Things to confirm on the bench before building

- The exact model printed on the five servo adapter boards (assumed Waveshare Bus Servo Adapter (A)).
- The hub adapter's voltage and current (5 V or 12 V input?), to decide which rail feeds the hub.
- How many 5 V adapters are in use today for the arm boards, and their connector types (to reuse plugs).
- The bundled Jetson adapter rating (expected 19 V, about 45 W) for comparison with the 12 V feed.
- Cable lengths from the planned power box to each arm board, the wheel board and the Jetson.
- Robot mass with arms, to refine the wheel current estimate under load.
- Whether the left wrist camera will be added (one more 500 mA USB load on a body port).

---

## 7. Source documents (on the Jetson)

- `~/so101/CLAUDE.md` – living project log (hardware table, AMR section, power notes, USB hub history)
- `~/so101/docs/handover/01_시스템_구성_및_운영_프로토콜.md` – system configuration, power structure (2.3), USB (2.4), servo IDs and wiring (2.5), start/stop procedures (6.x)
- `~/so101/docs/handover/04_통신_인터페이스_및_포팅_규격.md` – USB and servo bus protocol specifications
- `~/so101/docs/handover/05_기술_확인_QnA.md` – answers to the company (camera path, "no STM32 board")
- `~/so101/docs/mecanum_base_assembly_refs.md` – mecanum coupling references, **connector ratings, 12 V supply and cable shopping list (2026-09-16)**
- `~/so101/docs/wheel_servo_id_guide.md`, `docs/lidar_c1_test_guide.md`, `docs/gemini335_connection_guide.md` – device-level power and safety notes
- `~/so101/docs/hw_test_guide_2026-10-21.md`, `docs/demo_runbook_2026-10-21.md` – test and demo procedures
- Handover package on the Desktop: `SO101_기술자료_2026-10-15.zip`
