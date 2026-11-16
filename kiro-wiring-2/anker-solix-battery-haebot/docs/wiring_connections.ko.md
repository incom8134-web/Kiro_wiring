# 배선 연결표: 앤커 설계 (Rev C)

[English](wiring_connections.md) | [한국어](wiring_connections.ko.md)

`kicad/HAEBOT_ANKER.kicad_sch` 및 2026-11-16에 kicad-cli 7.0.11로 내보낸 `exports/HAEBOT_ANKER_NETLIST.net`과 일치합니다.
번호는 회로도의 참조 번호입니다. 전원 선과 USB 데이터 선은 따로입니다. USB 데이터 케이블은 서보 전원이 아닙니다.

**실제 제작 상태(AS BUILT), 제작자 보고 기준. 별도 실측 검증 전.** 제작자 보고에 선 굵기는 없습니다. 아래 굵기는 같은 전류에 쓰던 V1 굵기이며, 나중에 고칠 때 같은 등급의 선을 쓰라는 뜻입니다.

| ID | 에서 | 으로 | 넷 / 신호 | 전압 | 전류 | 케이블과 커넥터 | 상태 |
|---|---|---|---|---|---|---|---|
| W-D1 | PS1 USB-C2 | P02 VBUS / GND | USB-C | 실측 12 V | 미측정 | 장착된 USB-C 케이블. E-mark 미보고 | AS BUILT |
| W-D2 | P02 OUT+ | FB1 입력, 이어서 F1과 F5 | DRIVE_12V | 12 V | 전력 예산 참고 | 귀로는 P02 OUT-. 굵기 미보고 | AS BUILT |
| W-D3 | F1 | K1 1극(핀 1-2) -> U30 VIN+ | WHEEL_F / WHEEL_SW | 12 V | 설계 6 A, 스톨 10.8 A | 14 AWG 등급(V1), 페룰, U30 나사 단자 | 경로는 AS BUILT. 굵기는 V1 |
| W-D4 | U30 VIN- | P02 OUT- | GND_C2 | 0 V | W-D3과 같음 | 귀로 한 쌍. FB1에는 마이너스 버스가 없음 | AS BUILT |
| W-D5 | U30 포트 1 | M31 (FR ID7) -> M33 (RR ID9) | 서보 버스 | 12 V | 포트당 서보 2개 이하 | Molex 5264 3핀, GND / VCC / SIG | Verified (V1) |
| W-D6 | U30 포트 2 | M32 (FL ID8) -> M34 (RL ID10) | 서보 버스 | 12 V | 포트당 서보 2개 이하 | Molex 5264 3핀 | Verified (V1) |
| W-E1 | F5 | U20 DC 잭, K1 앞 | JETSON_12V | 12 V | 설계 3.0 A, 최대 3.8 A | 18 AWG 등급(V1), 5.5 x 2.5 mm, 센터 +. 비상정지 후에도 켜짐 | 경로는 AS BUILT. 잭은 V1에서 확인 |
| W-E2 | U20 DC- | P02 OUT- | GND_C2 | 0 V | W-E1과 같음 | P02 OUT-로 귀로 | AS BUILT |
| W-C1 | PS1 USB-C1 | P01 VBUS / GND | USB-C | 5 V | 최대 3 A | USB-C 케이블 | AS BUILT |
| W-C2 | P01 OUT+ | K1 2극(핀 3-4) -> U42 VIN+ | ARM2_5V / ARM2_SW | 5 V | 공급 3 A. 설계 5 A, 순간 8 A | U42 나사 단자. 벅 없음, 추가 퓨즈 없음 | AS BUILT. 설계 부하에서 포트 초과 |
| W-C3 | U42 VIN- | P01 OUT- | GND_C1 | 0 V | W-C2와 같음 | 자기 귀로 | AS BUILT |
| W-C4 | U42 포트 1 | M42 암 2 체인 | 서보 버스 | 5 V | 암 전류 | Molex 5264 3핀 | Verified (V1) |
| W-K1 | DRIVE_12V | F3 -> S1 (NC) -> SW2 \|\| K1 보조 13-14 -> K1 A1 | 제어 회로 | 12 V | 0.5 A 미만 | 20 AWG 등급(V1). F3는 도면상 1 A. 제작자는 용량을 말하지 않음 | AS BUILT |
| W-K2 | K1 A2와 D1 애노드 | GND_C2 | 제어 귀로 | 0 V | 0.5 A 미만 | D1 캐소드는 A1. D1 장착을 확인할 것 | Rev C 회로도에 표시 |
| W-B1 | PS1 USB-A1 | W3 -> U41 DC 잭 | ARM1_5V | 5 V | 설계 0.3 A, 최대 0.6 A | USB-A-DC 잭 케이블. 퓨즈 없음. K1로 차단되지 않음 | AS BUILT |
| W-B2 | U41 VIN- | W3 귀로 | GND_A1 | 0 V | W-B1과 같음 | 케이블 귀로 | AS BUILT |
| W-B3 | U41 포트 1 | M41 암 1 체인 | 서보 버스 | 5 V | 최대 0.6 A | Molex 5264 3핀 | Verified (V1) |
| W-A1 | PS1 USB-A2 | W1 -> U50 DC 입력 | HUB1_5V | 5 V | 2.4 A 이하 | USB-A-DC 배럴. 크기와 극성 미기록 | BLOCKED |
| W-A2 | - | U54 DC 입력 | 없음 | - | - | 전원 포트 미지정 | BLOCKED |
| U-1 | U20 USB-A1 | U51 Orbbec Gemini 335 | USB 3 데이터 + 버스 전원 | 5 V | 최대 0.9 A | 기본 케이블, 허브 경유 금지 | Verified (V1) |
| U-2 | U20 USB-A2 | U52 손목 웹캠 | USB 2 데이터 + 버스 전원 | 5 V | 0.5 A | 직접 | Verified (V1) |
| U-3 | U20 USB-A3 | U50 허브 1 업스트림 | USB_JET_HUB1 | - | - | USB 3 케이블 | Verified (V1) |
| U-4 | U20 USB-A4 | U54 허브 2 업스트림 | USB_JET_HUB2 | - | - | USB 케이블 | 데이터는 AS BUILT. 전원은 BLOCKED |
| U-5 | U50 DS1, DS2, DS3 | U30, U41, U42 USB | USB 데이터 | 5 V | 로직만 | USB-A-USB-C. 서보 전원이 아님 | Verified (V1) |
| U-6 | U50 DS4 | U53 RPLIDAR C1 어댑터 | USB 데이터 + 5 V | 5 V | 평균 0.23 A | 차폐 USB, 12 V 쌍에서 떨어뜨릴 것 | Verified (V1) |

일부러 연결하지 않음: PS1 USB-C3, USB-C4, CAR12V+, CAR12V-.

V1에서 이어진 규칙. 실제 제작에서 다른 점은 따로 적습니다.

- 바퀴 어댑터와 암 2 어댑터는 나사 단자로 공급합니다. 암 1만 예외입니다. 제작자가 USB-A-DC 잭 케이블을 어댑터 DC 잭에 꽂았습니다. 리더 전류는 약 0.3 A입니다.
- 바퀴 서보는 두 체인으로 두어 Molex 5264 접점이 서보 둘보다 많이 싣지 않게 합니다.
- 나사 단자에는 페룰. 모든 케이블 양끝에 스트레인 릴리프.
- 암 2 레일에 "5 V ONLY"라고 표시합니다. 팔로워 서보는 8.0 V를 넘으면 트립합니다. 이 소스는 그 레일을 5 V보다 올릴 수 없습니다.
- USB-C2의 플러스를 다른 포트의 플러스와 잇지 않습니다.
