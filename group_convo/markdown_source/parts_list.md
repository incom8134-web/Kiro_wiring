# Parts List – Power rewiring (Kiro / SO-101 mobile dual-arm robot)

Written 2026-10-22. Quantities are for one robot. Prices are rough 2026 estimates for budgeting only –
check the shop before ordering. Korean shops to search: 디바이스마트 (devicemart.co.kr), 엘레파츠 (eleparts.co.kr),
아이씨뱅큐 (icbanq.com); global: Pololu, Mouser/Digi-Key (Mean Well), Amazon/AliExpress for cables and connectors.

## A. Core power components

| # | Item | Spec to look for | Qty | Role | Example / search term | Approx. price |
|---|---|---|---|---|---|---|
| A1 | **AC-DC SMPS** | Mean Well **LRS-350-12** – 12 V, 29 A, 348 W, enclosed, V-ADJ trimmer, built-in fan, 215 × 115 × 30 mm | 1 | single 12 V main bus | search "LRS-350-12" (민웰 12V 29A). Alternative if weight/noise matter: **LRS-200-12** (17 A, fanless) – only typical loads, see power_calculation.md §3 | ₩45,000–70,000 |
| A2 | **Buck converter 7.2 V, two units** | synchronous step-down, in 8–40 V, out adjustable 1.2–30 V, **≥ 8 A continuous** with heatsink (10–12 A class boards), current limit | 2 | left / right follower arm rails | search "DC-DC 스텝다운 12A 300W" / "동기식 강압 컨버터 10A"; quality alternative **Pololu D36V50F7** (fixed 7.5 V, 5 A at 36 V in, more at 12 V in, protected); budget alternative **XL4016E1 8 A module** with heatsink + fan (realistic 5–6 A continuous) | ₩8,000–25,000 each |
| A3 | **Buck converter 5 V, 5 A** | sealed automotive style "12 V/24 V → 5 V 5 A 25 W" (e.g. WG-1224S0505S or HN25-1224-5 type), or **Pololu D24V50F5** (5 V, 5 A, in 6–38 V) | 1 | hub, lidar (via hub), both leader arms | search "12V to 5V 5A 컨버터 방수" | ₩6,000–20,000 |
| A4 | IEC C14 inlet module | with rocker switch and 5 × 20 mm fuse holder, 10 A rated; fit **5 A slow-blow** fuses (x3) | 1 | mains switch and fuse | search "IEC 인렛 스위치 퓨즈 일체형" | ₩3,000–6,000 |
| A5 | Mains cord | IEC C13, 1.5–2 m, 3-core with earth | 1 | – | – | ₩3,000 |
| A6 | Master switch 30 A DC | DC-rated rocker/toggle 30 A, or a 30 A DC circuit breaker (then A7 is not needed) | 1 | isolates the whole 12 V bus; also the battery connection point later | search "30A DC 차단기" / "30A 토글 스위치" | ₩5,000–15,000 |
| A7 | Main fuse 30 A | inline ATO/MAXI holder + 30 A fuse (x2) | 1 | protects the 12 AWG main run | search "인라인 퓨즈 홀더 30A" | ₩3,000 |
| A8 | **Blade fuse blocks, two groups** | automotive ATO/ATC with screw terminals and cover: **two 4-way blocks** (group A always-on: F2 F5 F6; group B relay-switched: F1 F3 F4), or one 12-way block with **two independent positive inputs**; one block with an integrated GND bus is ideal | 2 (or 1 dual-input) | branch fusing + star ground | search "4구 블레이드 퓨즈 박스" / "12구 퓨즈박스 독립 2입력" | ₩8,000–20,000 |
| A9 | Blade fuses (ATO) | 15 A ×2, 7.5 A ×4, 5 A ×4, 3 A ×2 (spares included) | 1 set | F1–F6 | assorted kit | ₩5,000 |
| A10 | GND bus bar (if A8 has none) | 6–8 screw positions, 30 A class | 1 | star ground | search "접지 버스바 6P" | ₩3,000 |

## B. E-stop and switching

| # | Item | Spec | Qty | Role | Approx. price |
|---|---|---|---|---|---|
| B1 | **Emergency stop switch** | 22 mm mushroom head, twist-to-release, **1 NC contact** (2 NC preferred), with box/enclosure | 1 | opens the relay coil circuit | ₩8,000–15,000 |
| B2 | Key switch | 22 mm or 19 mm, 2 positions, 1 NO | 1 | motors off at power-up until armed | ₩5,000 |
| B3 | **Automotive relay** | 12 V coil, **40 A SPST** (4-pin, pins 30/87/85/86), with socket/pigtail | 1 | cuts wheels + both follower rails | ₩4,000–8,000 |
| B4 | Diode 1N4007 | across the coil, cathode to pin 86 | 2 | coil spike suppression | ₩200 |
| B5 | Panel LED 12 V (optional) | "motor power on" indicator wired after pin 87 | 1 | status | ₩1,000 |

## C. Connectors and cable

| # | Item | Spec | Qty | Use | Approx. price |
|---|---|---|---|---|---|
| C1 | XT60 connector pairs | genuine Amass, with heat-shrink | 4 pairs | 12 V branches: wheel hub, buck L in, buck R in, spare | ₩6,000 |
| C2 | XT30 connector pairs | Amass | 6 pairs | 7.2 V to follower boards, 5 V to hub and leader boards | ₩5,000 |
| C3 | DC barrel plug 5.5 × 2.5 mm | with 18 AWG lead, centre positive, strain relief (or reuse the plug cut from a spare adapter) | 1 | Jetson | ₩2,000 |
| C4 | Silicone wire 12 AWG | red + black, 1 m each | 1 | SMPS → switch → fuse block, GND bar | ₩6,000 |
| C5 | Silicone wire 14 AWG | red + black, 3 m each | 1 | wheel branch | ₩8,000 |
| C6 | Silicone wire 18 AWG | red + black, 5 m each | 1 | Jetson, bucks, follower boards | ₩8,000 |
| C7 | Silicone wire 20 AWG | red + black, 3 m each | 1 | 5 V distribution, relay coil circuit | ₩5,000 |
| C8 | **Molex 5264 pre-crimped leads, 22 AWG** | kit with 5264-03 housings; e.g. Amazon B0D2W47V8V (XLeRobot BOM item, ~1.2 m leads) or Tcenofoxy 50 cm kit B0F8J2HKZF | 1 kit | wheel servo leads, replacement arm pigtails | ₩20,000–35,000 |
| C9 | Molex 5264-03 housings + 5263 terminals | devicemart goods no. 442 (housing), terminals separately; crimp tool for 2.5 mm pitch if making custom leads | 20 | spares | ₩5,000 |
| C10 | Molex 5267-03 wafers (through-hole, 2.5 mm) | for the wheel power hub board | 6 | wheel power hub | ₩3,000 |
| C11 | Ready harness 3P-3P 5264, 20 cm | devicemart NW3-5264-03 (goods no. 10895279), AWG 26 – signal-only pigtail base adapter → wheel hub | 2 | – | ₩2,000 |
| C12 | Bootlace ferrules + crimper | 12–20 AWG assortment | 1 | every screw terminal (SMPS, fuse block, board PWR terminals) | ₩15,000 |
| C13 | Heat-shrink, cable ties, spiral wrap, adhesive tie mounts | assorted | 1 | harness | ₩10,000 |
| C14 | Fork/ring terminals M4 | for SMPS and bus bar screws, 12–14 AWG | 10 | – | ₩3,000 |

## D. Decoupling, protection, cooling, mechanics

| # | Item | Spec | Qty | Use | Approx. price |
|---|---|---|---|---|---|
| D1 | Electrolytic capacitor | **2200 µF / 25 V**, low ESR, 105 °C | 2 | C1 on the wheel power hub (+1 spare) | ₩1,500 |
| D2 | Electrolytic capacitor | **2200 µF / 16 V**, low ESR | 3 | C2/C3 at the follower boards' PWR terminals | ₩1,500 |
| D3 | TVS diode (optional) | SMBJ8.0A (7.2 V rails) ×2, SMCJ15A (12 V wheel hub) ×1 | 3 | clamps spikes from back-driven servos | ₩2,000 |
| D4 | Perfboard / small PCB 5 × 7 cm | for the wheel power hub (4 × 5267 wafers + C1 + 2-pin screw terminal) | 1 | – | ₩1,000 |
| D5 | Screw terminal 2-pin 5.08 mm, 15 A | wheel power hub input | 1 | – | ₩500 |
| D6 | Heatsink + thermal pad for the two 7.2 V bucks | aluminium plate or 40 × 40 mm finned heatsinks | 2 | 4 W dissipation each | ₩4,000 |
| D7 | 12 V fan 40–60 mm (optional) | wired from F6 | 1 | power box airflow | ₩4,000 |
| D8 | Power box / mounting plate | ventilated plastic or aluminium box ~ 300 × 200 × 80 mm, or an open plate under the chassis with finger guards over the SMPS AC end | 1 | holds SMPS, fuse block, bucks, relay | ₩15,000–30,000 |
| D9 | Labels | voltage labels for every connector: 12 V, 7.2 V, 5 V. Mark the follower XT30 leads "7.2 V ONLY – never 12 V" | – | prevents the 12 V-on-follower mistake | ₩2,000 |

## E. Test equipment (have or borrow)

| # | Item | Why |
|---|---|---|
| E1 | Digital multimeter | set the SMPS and buck voltages before connecting loads |
| E2 | DC clamp meter (≥ 40 A DC) | measure branch currents and the SMPS peak during the demo |
| E3 | Dummy load (e.g. 12 V 21 W automotive bulb) | test the 7.2 V bucks under load before connecting arms |

## F. Later: battery option (not in this build)

| Option | Note |
|---|---|
| Anker SOLIX C300 DC (or similar power station with a regulated 12 V / 10 A DC output) | plugs into the master switch in place of the SMPS; used by XLeRobot |
| 3S Li-ion pack 12.6 V with 40 A BMS + low-voltage alarm | direct, sags to 9 V (Jetson minimum) when empty |
| 4S LiFePO4 | only with a 12 V regulator: full charge 14.6 V exceeds the wheel servo limit (14 V) |

## Approximate budget

Core (A) ≈ ₩110,000–170,000, E-stop (B) ≈ ₩20,000–35,000, connectors and cable (C) ≈ ₩100,000–130,000,
protection and mechanics (D) ≈ ₩35,000–55,000. **Total ≈ ₩270,000–390,000** excluding tools.
