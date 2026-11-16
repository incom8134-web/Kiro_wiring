# HAEBOT V2-A: 앤커 솔릭스 C300 DC 전원

[English](README.md) | [한국어](README.ko.md)

HAEBOT / KIRO 로봇을 **앤커 솔릭스 C300 DC (A1726)** 파워 스테이션 한 대로 구동하는 전원입니다.
이 개정은 제작자가 실제로 연결한 배선을 기록합니다.

**상태: Rev C, 2026-11-16. 실제 제작 상태(AS BUILT), 제작자 보고 기준. 별도 실측 검증 전.**

| | |
|---|---|
| 회로도 (KiCad) | [`kicad/HAEBOT_ANKER.kicad_pro`](kicad/HAEBOT_ANKER.kicad_pro) |
| 회로도 PDF | [`exports/HAEBOT_ANKER_SCHEMATIC.pdf`](exports/HAEBOT_ANKER_SCHEMATIC.pdf) |
| 블록 다이어그램 | [한국어](exports/HAEBOT_ANKER_BLOCK_DIAGRAM_KO.pdf), [English](exports/HAEBOT_ANKER_BLOCK_DIAGRAM.pdf), 원본 [`block-diagrams/`](block-diagrams) |
| 부품표 | [`bom/README.ko.md`](bom/README.ko.md) |
| 전력과 사용 시간 | [`docs/power_budget.ko.md`](docs/power_budget.ko.md) |
| 배선표 | [`docs/wiring_connections.ko.md`](docs/wiring_connections.ko.md) |
| 분배와 보호 | [`docs/power_distribution_and_protection.ko.md`](docs/power_distribution_and_protection.ko.md) |
| 검증 보고서 | [`docs/verification_report.ko.md`](docs/verification_report.ko.md) |
| 조립과 전원 투입 | [`docs/assembly_instructions.ko.md`](docs/assembly_instructions.ko.md) |
| 에이전트 지침 | [`AGENTS.md`](AGENTS.md) |

## 실제 배선

| 분기 | 스테이션 포트 | 경로 | 부하 |
|---|---|---|---|
| D + E | USB-C2 | USB-C 케이블, 12 V로 맞춘 PD 트리거(제작자 실측), Dorhea 4구 퓨즈 박스 | 바퀴는 F1 15 A와 K1을 거침. 젯슨은 F5 5 A, K1 앞 |
| C | USB-C1 | 5 V PD 트리거, K1 접점 | 암 2(팔로워), STS3215 6개, 5 V. 소스는 최대 3 A |
| B | USB-A1 (5 V 2.4 A) | USB-A-DC 잭 케이블, 퓨즈 없음 | 암 1(리더). 어댑터 DC 잭에 직접. 비상정지로 차단되지 않음 |
| A | USB-A2 (5 V 2.4 A) | USB-A-DC 케이블 | USB 3 허브 7포트 하나, 5 V 입력, 부하 2 A 미만. **RECOMMENDED**, 장착 확인 전 |
| - | 없음 | 달지 않음 | USB 허브 2. **RECOMMENDED**: 두지 않음. USB-C3은 충전용으로 비움 |
| - | USB-C3, USB-C4, 시거잭 | 연결 안 함 | 사용하지 않음. USB-C3은 충전용으로 비워 둠 |

비상정지가 장착되어 있습니다. `DRIVE_12V -> 퓨즈 -> 비상정지(NC) -> START || K1 보조접점 -> K1 코일`.
버튼 하나로 바퀴와 암 2가 꺼집니다. 젯슨, 허브, 암 1은 켜진 채로 남습니다.

포트가 버틴다는 가정의 계산 사용 시간은 평균 61 W에서 약 4.0시간입니다.
평균 주행만으로도 USB-C2에 약 3.5 A가 필요하고, 12 V USB-C 계약은 보통 3 A(36 W)라서 12 V 레일이 떨어질 수 있습니다.
전력 예산을 보십시오.

## Rev B에서 바뀐 점

Rev B는 제안이었습니다. Rev C는 제작자의 배선입니다.

1. 시거잭, 시거 플러그 케이블, 12 V 벅, EA75-5V 암 벅은 장착되지 않았습니다.
2. 바퀴와 젯슨이 USB-C2의 12 V를 같이 씁니다. 제작자가 12 V를 측정했습니다. 앤커 A1726 설명서에는 USB-C 12 V 출력이 없으므로, 이 전압은 설명서 정격이 아니라 제작자 실측입니다.
3. K1 전력 접점은 세 개가 아니라 두 개입니다. 암 1은 비상정지에 물려 있지 않습니다.
4. 암 2는 5 V PD 트리거로 공급됩니다. 포트는 3 A입니다. 팔로워 설계 부하는 5 A, 순간 부하는 8 A입니다.

## 아직 확인할 것

허브 사양과 1 A 코일 퓨즈는 권장입니다. 제작자에게 허브 라벨이 없고 퓨즈 용량도 모릅니다.
USB-C2가 12 V에서 실제로 얼마나 전류를 버티는지는 측정되지 않았습니다. 자세한 내용은 검증 보고서입니다.

## 편집

KiCad 7 이상에서 `kicad/HAEBOT_ANKER.kicad_pro`를 엽니다. 내보내기 명령은 `AGENTS.md`에 있습니다.
`exports/`의 블록 다이어그램 PDF는 SVG에서 다시 그렸습니다. 허브 줄은 위의 권장입니다.
