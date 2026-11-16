# 부품표: 앤커 설계 (Rev C)

[English](README.md) | [한국어](README.ko.md)

전체 표: [`HAEBOT_ANKER_BOM.csv`](HAEBOT_ANKER_BOM.csv).

**2026-11-16, 실제 제작 상태(AS BUILT), 제작자 보고 기준. 별도 실측 검증 전.** "part number not recorded"는 제작자가 부품을 달았으나 제조사 형번을 남기지 않았다는 뜻입니다. 이 파일의 형번은 지어내지 않았습니다.

Rev B 제안에서 빠져 장착되지 않은 것: 12 V 벅, TOBSUN EA75-5V 암 벅, 시거 플러그 케이블, 암 1용 USB-C 5 V 케이블, 두 번째 허브 전원 케이블, 퓨즈 F2와 F4, K1의 세 번째 전력 접점.

| 번호 | 부품 | 기능 | 제조사 / 모델 | 전압 | 정격 전류 | 최대 | 수량 | 상태 | 검증 |
|---|---|---|---|---|---|---|---|---|---|
| PS1 | 앤커 솔릭스 C300 DC | 전원 | Anker A1726 | USB-C, USB-A. 시거잭 미사용 | 포트 표 | 300 W | 1 | AS BUILT | 모델은 설명서로 확인 |
| P02 | USB-C PD 트리거, 12 V | 바퀴와 젯슨 | 형번 미기록 | 12 V 출력, 제작자 실측 | 전류 미측정 | - | 1 | AS BUILT | 설명서 프로파일이 아님 |
| P01 | USB-C PD 트리거, 5 V | 암 2 | 형번 미기록 | 5 V 출력 | 최대 3 A | - | 1 | AS BUILT | 암 부하 5 A / 8 A보다 작음 |
| FB1 | Dorhea 4구 퓨즈 박스 | 12 V 분배 | Dorhea (V1) | 12 V | F1, F5 사용 | - | 1 | AS BUILT | V1 부품. 빈 슬롯 2개 |
| F1 | 날 퓨즈 15 A | 바퀴, 그 다음 K1 | ATO | 32 V | 15 A | - | 1 | AS BUILT | V1 값 |
| F5 | 퓨즈 5 A | 젯슨, K1 앞 | ATO | 32 V | 5 A | - | 1 | AS BUILT | V1 값 |
| F3 | 퓨즈 1 A 속단 날 | 비상정지 회로 | 권장값 | 32 V | 1 A | - | 1 | RECOMMENDED | 퓨즈는 장착됨. 용량은 미상. 1 A는 유지 0.25 A의 약 네 배. Dorhea 빈 슬롯 |
| K1 | 접촉기, NO 전력 2극 + 보조 NO | 비상정지 | 형번 미기록 | 코일 12 V | 바퀴, 암 2 | - | 1 | AS BUILT | 세 번째 극 없음 |
| S1 | 비상정지, NC | 비상정지 | 형번 미기록 | 12 V | 1 A 미만 | - | 1 | AS BUILT | AS BUILT |
| SW2 | START, 순간 NO | 재투입 | 형번 미기록 | 12 V | 1 A 미만 | - | 1 | AS BUILT | AS BUILT |
| D1 | 플라이백 다이오드 | 코일 억제 | 1N4007 | 12 V | 1 A | - | 1 | Rev C 회로도에 표시 | 장착 여부 확인. 캐소드는 A1 |
| W3 | USB-A-DC 잭 케이블 | 암 1 | 기성 케이블 | 5 V | 2.4 A | - | 1 | AS BUILT | 퓨즈 없음, 비상정지 밖 |
| W1 | USB-A-DC 배럴 케이블 | 허브 1 | 미기록 | 5 V | 2.4 A | - | 1 | RECOMMENDED | 5 V 허브 전용. 연결 전 센터 플러스 확인 |
| U20 | Jetson Orin Nano Super 8 GB | 컴퓨터 | NVIDIA | 9-20 V | 설계 3.0 A | 3.8 A | 1 | AS BUILT | V1 기록. 비상정지 후에도 켜짐 |
| U30 | 버스 서보 어댑터 (A) | 바퀴 | Waveshare, V1 기준 | 12 V | 설계 6 A | - | 1 | AS BUILT | V1 |
| U42 | 버스 서보 어댑터 (A) | 암 2 | Waveshare, V1 기준 | 5 V | 포트 3 A | - | 1 | AS BUILT | V1 |
| U41 | 버스 서보 어댑터 (A) | 암 1 | Waveshare, V1 기준 | 5 V | 최대 0.6 A | - | 1 | AS BUILT | DC 잭, 실제 제작 |
| M31-M34 | ST3215-C018 | 바퀴 | Feetech / Waveshare | 12 V, 최대 12.6 V | 각 1.5 A | 2.7 A | 4 | AS BUILT | V1 실측 |
| M41 | 리더 암, STS3215 6개 | 암 1 | Feetech | 5 V | 0.3 A | 0.6 A | 1 | AS BUILT | 토크 꺼짐 |
| M42 | 팔로워 암, STS3215 6개 | 암 2 | Feetech | 5 V, 8.0 V에서 트립 | 설계 5 A | 8 A | 1 | AS BUILT | 소스는 3 A |
| U50 | USB 3 허브, 7포트 | 허브 1 | 일반 사양, 브랜드 없음 | 5 V DC | 2 A 미만 | - | 1 | RECOMMENDED | 5 V 배럴, USB 3.x, USB-A2에 허브 하나 |
| U54 | USB 허브 2 | 장착하지 않음 | 없음 | - | - | - | 0 | RECOMMENDED | 달지 않음. 여유 포트는 허브 1 |
| U51 | Orbbec Gemini 335 | 머리 카메라 | Orbbec | USB 5 V | 0.9 A | - | 1 | AS BUILT | V1 실측 |
| U52 | 손목 웹캠 | 손목 카메라 | 소매 모델 미상 | USB 5 V | 0.5 A | - | 1 | AS BUILT | V1 실측 |
| U53 | RPLIDAR C1 + CP2102N | 라이다 | Slamtec | USB 5 V | 0.23 A | - | 1 | AS BUILT | V1 실측 |
