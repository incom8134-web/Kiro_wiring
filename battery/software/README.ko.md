# 배터리 모니터 소프트웨어

[English](README.md) | [한국어](README.ko.md)

[`../README.ko.md`](../README.ko.md)의 Jetson Orin Nano Developer Kit 설계를 구동하는 Python 3.9 이상 서비스입니다.
그 키트의 JetPack 6는 Ubuntu 22.04이고 Python 3.10을 포함합니다. JetPack 5는 Ubuntu 20.04이고 Python 3.8이라 이 패키지보다 낮습니다. 그 이미지에서는 Python 3.9 이상으로 만든 가상환경을 씁니다.

Matek I2C-INA-BM은 `/dev/i2c-7`(J12 핀 3과 5, I2C1), 주소 0x45로 읽습니다. I2C 전용입니다. `sudo i2cdetect -y -r 7`에 0x45가 보여야 합니다. UART `/dev/ttyTHS0`(핀 8과 10)은 선택 사항이며 쓰지 않습니다. 배포 프로필은 `uart_enabled`를 false로 둡니다. 코드는 나중에 켤 수 있게 남아 있습니다.

배포 프로필의 모듈 값은 [Matek](https://www.mateksys.com/?portfolio=i2c-ina-bm)와 TI SLYS021에서 왔습니다. 션트 0.0002 Ω, `adc_range_mv` 40.96, 풀스케일 204.8 A. 그 풀스케일에서 SHUNT_CAL은 4096, CURRENT_LSB는 390.625 µA입니다. 팩 전류 한계가 있으면 `configure()`가 그 전류로 SHUNT_CAL을 다시 계산합니다. 드라이버는 DEVICE_ID 0x2281만 받습니다. 이 경로는 Matek 보드에서 실행한 적이 없습니다.

팩은 확인된 YOLTON 12 V 45 Ah li-ion입니다. `max_voltage_v` 12.6과 `min_voltage_v` 9.0은 3S 리튬이온으로 가정한 값입니다. 만충전에서 미터로 확인합니다. `max_charge_current_a`와 `max_discharge_current_a`는 null이므로 하드웨어 모드는 기동하고 과전류 경보는 꺼져 있습니다. 그 전류를 채우기 전까지 SHUNT_CAL은 Matek 풀스케일을 유지합니다.

이 패키지에는 웹 서버가 없습니다. HAEBOT 로봇 웹 앱이 `/var/lib/battery-monitor/state.json`을 읽습니다. 경로는 Matek INA, I2C, Jetson, 상태 파일, 웹 앱입니다. 필드 목록은 [`../README.ko.md`](../README.ko.md)에 있습니다. 앱 소스는 이 저장소에 없습니다.

```bash
cd battery/software
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pytest
python -m battery_monitor --simulate --duration 2
python -m battery_monitor --check-profile --config config/battery_profile.json
```

`--simulate`는 센서와 실제 배터리 프로필 없이 동작합니다.

실기 기동. 배포 프로필을 쓸 수 있다. 충전 전류와 방전 전류는 아직 null이다:

```bash
python -m battery_monitor --config config/battery_profile.json \
  --state /var/lib/battery-monitor/state.json \
  --history /var/lib/battery-monitor/history.sqlite
```

프로세스는 `i2c` 그룹에 있어야 합니다. `dialout`은 나중에 `uart_enabled`를 true로 둘 때만 필요합니다. systemd 유닛은 `systemd/battery-monitor.service`입니다. `SIGTERM`이면 종료 전에 상태 파일을 기록합니다.

| 모듈 | 역할 |
|---|---|
| `battery_monitor/ina228.py` | INA228 레지스터 계산과 smbus2 드라이버 |
| `battery_monitor/sensors.py` | 헤더 I2C, 스크립트 센서, 시뮬레이션 파형 |
| `battery_monitor/accounting.py` | 부호 있는 전력, Ah, Wh |
| `battery_monitor/soc.py` | 쿨롱 카운트 SOC와 휴지 OCV 보정 |
| `battery_monitor/faults.py` | 전압, 전류, 포화, 통신 |
| `battery_monitor/storage.py` | 원자적 JSON 상태, SQLite 이력 |
| `battery_monitor/uart_out.py` | `/dev/ttyTHS0`의 선택적 CSV. 기본값은 꺼짐 |
| `battery_monitor/service.py` | 루프, 시그널, CLI |

`config/battery_profile.json`은 YOLTON 12 V 45 Ah 프로필입니다. 그 파일의 충전 전류와 방전 전류는 null입니다. `config/examples/example_DO_NOT_USE.json`은 형식 예시이며 실기에서 거절됩니다.
