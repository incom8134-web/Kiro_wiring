# Jetson Orin Nano 배터리 모니터

[English](README.md) | [한국어](README.ko.md)

이 모니터는 Jetson Orin Nano Developer Kit 40핀 헤더 J12의 Matek I2C-INA-BM 모듈로 배터리 팩 하나를 읽는다. 션트는 모듈의 도통 경로다. Jetson이 쿨롱을 적산하고 충전 상태를 추정한 뒤 JSON 파일을 쓴다. 경로는 Matek INA, I2C, Jetson, `state.json`, HAEBOT 웹 앱이다. 핀 8과 10의 UART는 선택 사항이며 쓰지 않는다. 이 폴더에는 웹 서버가 없다.

팩은 YOLTON e-bike pack (Coupang 9101801616)이다. 검은 직사각형 팩이고, 빨강과 검정 리드, DC 배럴 커넥터, 작은 BMS 상자가 있다. 사용자가 12 V, 45 Ah를 확인했다. 볼턴 12 V 45 Ah 상품 페이지는 리튬이온, LG 셀이라고 적는다 ([voltonbattery.com 12 V 45 Ah](https://www.voltonbattery.com/12v/?idx=407), [쿠팡 9101801616](https://www.coupang.com/vp/products/9101801616?vendorItemId=93727752087)). [`software/config/battery_profile.json`](software/config/battery_profile.json)의 화학은 `li-ion`, 공칭 전압은 12.0 V, 용량은 45 Ah다.

셀 구성은 가정한 3S다. `max_voltage_v` 12.6과 `min_voltage_v` 9.0은 3S 리튬이온으로 가정한 값이다. 만충전에서 미터로 확인한다. 12.6 V는 3 × 4.2 V, 9.0 V는 3 × 3.0 V다. 이 두 전압은 볼턴 페이지에 적혀 있지 않다.

충전 전류와 방전 전류는 아직 확인되지 않았다. 프로필의 `max_charge_current_a`와 `max_discharge_current_a`는 null이다. 로더에는 자리표시 숫자를 미확인으로 남겨 두는 표시가 없어서, 전류 숫자는 만들지 않는다. 서비스는 그래도 기동한다. 과전류 경보는 꺼져 있고, SHUNT_CAL은 Matek 풀스케일을 유지한다. [`bom/BOM.csv`](bom/BOM.csv)의 전원선 행은 전류를 알기 전까지 BLOCKED다. 모듈 션트, 주소, ADC 범위는 Matek 페이지에서 채운 값이며 팩을 짐작한 것이 아니다. 예시 파일의 숫자는 권장 팩이 아니다.

충전은 12.6 V CC/CV 리튬이온 충전기(볼턴 전용 충전기)를 쓴다. 일반 12 V 전원 어댑터를 쓰지 않는다.

이 장치는 배터리 관리 장치가 아니다. 셀 밸런스를 하지 않고 접촉기를 열지 않는다.

## 연결

| 부품 | 역할 |
|---|---|
| Matek I2C-INA-BM | 배터리 양극 리드에 둔다. 팩 전류는 BAT+로 들어가 ESC+로 나간다. 도통 경로는 통상 200 µΩ이다. |
| JST-GH-4P | 로직과 I2C: 5V, SCL, SDA, G. 점퍼를 열면 주소는 0x45(십진 69)다. |
| Jetson Orin Nano Developer Kit | J12의 `/dev/i2c-7`을 읽고 상태 파일을 쓴다. 핀 2가 모듈의 4–9 V 핀을 공급한다. UART는 꺼져 있다. |

버스 범위는 0 V에서 85 V다 (Matek 페이지와 TI SLYS021). 팩이 85 V를 넘을 수 있으면 연결하지 않는다. 프로필 로더가 그 경우를 거절한다. Matek 정격은 연속 150 A, 순간 204.8 A다. 200 µΩ에서 그 순간 전류는 40.96 mV이므로 프로필은 ±40.96 mV ADC 범위를 쓴다. 풀스케일 보정은 CURRENT_LSB = 204.8 / 2^19 = 390.625 µA, SHUNT_CAL = 4096이다 (SLYS021). 배포 프로필에는 팩 전류가 없으므로 드라이버는 그 풀스케일 보정을 유지한다. 팩 전류 한계를 채운 뒤에는 드라이버가 그 전류로 SHUNT_CAL을 다시 계산한다. 저항은 200 µΩ, 범위는 ±40.96 mV 그대로다. 연속 150 A를 넘으면 경고가 난다. 이 코드는 Matek 보드에서 실행한 적이 없다.

공식 페이지는 INA228과 INA238을 함께 적는다. 드라이버는 DEVICE_ID 0x2281만 받고 다른 ID는 거절한다. 어느 칩이 실렸는지는 그 레지스터를 읽기 전에는 확인되지 않는다.

양전류는 방전, BAT+에서 ESC+로 나가는 방향이다. 음전류는 충전이다. 전력도 같은 부호다.

![Matek 모듈에서 Jetson Orin Nano J12. UART는 선택이며 사용하지 않음](wiring/battery_monitor_wiring.png)

모듈은 I2C 전용이다. UART 핀이 없다.

모듈에서 Jetson으로 가는 선은 모듈에 포함된 JST-GH-4P다. Matek 5V는 J12 핀 2(5 V), SDA는 핀 3(I2C1_SDA), SCL은 핀 5(I2C1_SCL), G는 핀 6(GND). 핀 3과 5는 I2C 버스 7, `/dev/i2c-7`이다 (Jetson Orin Nano Developer Kit Carrier Board Specification, SP-11324-001, 헤더 J12. 리눅스 장치 대응은 [JetsonHacks Orin Nano 핀아웃](https://jetsonhacks.com/nvidia-jetson-orin-nano-gpio-header-pinout/)). `sudo i2cdetect -y -r 7`에 0x45가 보여야 한다. 모듈의 5V 핀은 4–9 V 입력이고 약 1 mA를 쓴다. 핀 2(5 V)가 그 핀을 공급할 수 있다. 핀 1은 3.3 V이므로 그 핀에 연결하지 않는다. 핀 4는 쓰지 않는다. 헤더 핀에 팩 전압을 넣지 않는다.

핀 1(3.3 V)은 USB와 이더넷 포트에 가까운 헤더 끝이다. 핀 39와 40은 팬 쪽이다. JetsonHacks 사진은 핀 1을 이더넷 잭 옆에 표시하고, [NVIDIA 하드웨어 배치](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html)는 그 포트 묶음이 헤더의 한쪽, 모듈 팬이 다른 쪽에 있음을 보여 준다. 배선 전에 멀티미터로 확인한다. 핀 1은 3.3 V, 핀 2는 5 V여야 한다.

Jetson I2C는 3.3 V이며 5 V를 견디지 않는다. SP-11324-001은 J12의 모든 신호가 3.3 V 레벨이라고 적는다. Matek 모듈의 I2C 풀업 전원은 확인되지 않았다. Matek의 빨간 LED는 3.3 V 표시라고만 되어 있다. 레귤레이터가 있다는 뜻이지, 풀업이 3.3 V라는 뜻은 아니다. 5V 핀과 GND만 연결한 상태에서 SDA 아이들 전압을 잰다. 약 3.3 V이면 SDA와 SCL을 핀 3과 5에 연결한다. 약 3.6 V를 넘으면 그 핀 앞에 BSS138 레벨 시프터를 둔다.

UART 핀 8(UART1_TXD)과 핀 10(UART1_RXD)은 `/dev/ttyTHS0`이다. 이 포트는 선택 사항이며 쓰지 않는다. 배포 프로필은 `uart_enabled`를 false로 둔다. 모듈을 연결하는 선이 아니다.

전원선은 BAT+와 ESC+의 팩 도체다. 팩 전류를 모르므로 규격을 고르지 않는다. 모듈의 150 A 정격으로 전선을 고르지 않는다.

## HAEBOT 웹 앱이 값을 읽는 방법

화면은 HAEBOT 로봇 웹 앱이다. 그 소스는 이 저장소에 없다. 이 서비스는 페이지를 제공하지 않는다. 앱이 모듈을 직접 열지 않는다. 이 폴더에는 HTTP나 WebSocket 서버가 없다. 앱은 아래 JSON 파일을 읽는다. 선택적 UART CSV는 이 설계에 들어 있지 않다.

앱은 파일 하나를 읽는다.

`/var/lib/battery-monitor/state.json`

[`software/systemd/battery-monitor.service`](software/systemd/battery-monitor.service)의 경로다. `software/`에서 직접 실행하면 `--state`를 주지 않는 한 `run/state.json`에 쓴다. 파일은 원자적으로 바뀐다. 임시 파일에 쓰고, fsync하고, 이름을 바꾼다. 배포 프로필은 샘플마다 다시 쓴다 (`persist_interval_s` 0.5). `SIGTERM`이면 종료 전에 한 번 더 쓴다.

| 필드 | 의미 |
|---|---|
| `updated_unix` | 이 파일을 만든 샘플의 유닉스 초. |
| `voltage_v` | VBUS에서 본 팩 전압. 마지막 읽기가 실패하면 null. |
| `current_a` | 부호 있는 암페어. 양수는 방전. |
| `power_w` | `voltage_v * current_a`. 양수 전력은 배터리에서 나간다. |
| `soc_percent` | 충전 상태. 0–100으로 자른다. 기준점이 없으면 null. |
| `soc_unclamped_percent` | 자르지 않은 같은 값. |
| `capacity_ah` | 남은 암페어시. |
| `nominal_capacity_ah` | 프로필의 용량. |
| `energy_wh` | 적산한 와트시. 충전하면 감소한다. |
| `ampere_hours_out` | 적산한 암페어시. 재시작에 쓰는 카운터. |
| `watt_hours_out` | `energy_wh`와 같은 값. 적산을 이어 가기 위해 남긴다. |
| `soc_anchor_percent`, `ah_at_anchor` | 쿨롱 카운트 기준. 앱은 무시해도 된다. |
| `status` | `Charging`, `Discharging`, `Idle`, `Fault`. |
| `runtime_hours`, `runtime_label` | 방전 중 남은 시간, 또는 충전 중 가득 찰 때까지의 시간. `runtime_label`은 `remaining` 또는 `time_to_full`. |
| `faults` | 알람 이름 목록. 프로필 한계 안이면 빈 목록. |
| `comms_ok` | INA228 읽기에 실패하면 false. |
| `stale` | `comms_ok`가 false이면 true. |
| `simulated` | 시뮬레이션 센서이면 true. |
| `power_loss_gap` | 재시작이나 긴 공백 뒤에 true. 그 시간은 적산하지 않는다. |
| `ocv_corrected` | 휴지 개방 전압 보정을 적용한 샘플이면 true. |
| `profile_name`, `chemistry` | 프로필에서 복사한다. |

`comms_ok`가 false이면 `voltage_v`와 `current_a`는 null이다. 파일이 얼마나 오래됐는지는 `updated_unix`로 본다.

옆의 SQLite 파일(`/var/lib/battery-monitor/history.sqlite`)은 기록이다. 실시간 값은 JSON 파일이다.

서비스는 `sample_period_s`마다 샘플한다(배포 프로필은 0.5초). `persist_interval_s`마다 파일을 다시 쓴다(역시 0.5초). 전압 경보는 12.6 V와 9.0 V를 쓴다. 이 값은 3S 리튬이온으로 가정한 것이며, 만충전에서 미터로 확인한다. 충전 전류와 방전 전류는 null이므로 과전류 경보는 꺼져 있다. 로더가 강제하는 모듈 상한은 85 V이고, 팩 전류를 채운 뒤에는 션트 풀스케일이다. 150 A를 넘는 명판은 Matek 연속 정격에 대한 경고를 낸다.

UART 로그는 선택 코드이며 기본값은 꺼짐이다 (`uart_enabled` false). 켜면 같은 행을 `/dev/ttyTHS0`, 115200 baud, 3.3 V로 샘플마다 CSV 한 줄 출력한다.

```text
unix_s,voltage_v,current_a,power_w,soc_percent,capacity_ah,energy_wh,status,faults
```

그 줄의 `capacity_ah`는 남은 암페어시다. `faults`는 `|`로 잇는다. 현재 설계는 이것을 켜지 않는다.

## 상자

인쇄 상자는 Matek 모듈을 넣는다. 션트는 그 기판에 있으므로 션트 판은 없다. 몸체 **33.8 × 26.8 × 11.8 mm**. 체결 탭 둘을 넣으면 베이스는 **49.8 × 26.8 × 10.0 mm**. 안쪽 **29.4 × 22.4 × 8.2 mm**. 여기서 쓴 기판 크기는 Matek의 27 × 20 × 6 mm다. 벽 2.2 mm, 바닥 1.8 mm, 뚜껑 1.8 mm. 끼워맞춤은 면마다 1.2 mm. 뚜껑 인쇄물은 바깥 면이 베드에 있고 **33.8 × 26.8 × 4.2 mm**다.

개구는 모두 위가 열려 있다. 짧은 벽마다 전원선 슬롯(6 mm, 인쇄용 기본값이며 고른 규격이 아님), 긴 벽 한쪽에 JST-GH 슬롯 두 개(11 mm). JST 면은 치수도가 아니라 제품 사진을 따른다. 판매처의 φ3 mm PCB 구멍은 mateksys.com에 없고 쓰지 않는다. 탭은 M3 클리어런스 구멍(3.4 mm)이다. 바닥과 뚜껑의 통풍구는 기판 위 션트 쪽에 있다. Matek가 데드 패드라고 한 바닥 면은 모서리의 1.2 mm 패드로 바닥에서 띄운다.

Jetson은 상자 밖에 있다.

![Matek 모듈 상자. 베이스와 들어 올린 뚜껑](enclosure/preview.png)

`battery/enclosure`에서 `python3 enclosure.py`로 다시 만든다. 자세한 내용은 [`enclosure/README.md`](enclosure/README.md)에 있다.

## 소프트웨어

실행과 테스트: [`software/README.ko.md`](software/README.ko.md). 부품: [`bom/BOM.csv`](bom/BOM.csv).
