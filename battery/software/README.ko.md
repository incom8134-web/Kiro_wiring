# 배터리 모니터 소프트웨어

[English](README.md) | [한국어](README.ko.md)

[`../README.ko.md`](../README.ko.md)의 Jetson Nano 설계를 구동하는 Python 3.9 이상 서비스입니다.
Nano의 JetPack 4.6 기본 Python은 3.6입니다. Python 3.9 이상으로 만든 가상환경을 사용합니다.

```bash
cd battery/software
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pytest
python -m battery_monitor --simulate --duration 2 --no-web
python -m battery_monitor --check-profile --config config/battery_profile.json
```

`--simulate`는 센서와 실제 배터리 프로필 없이 동작합니다. `--no-web`을 빼면 대시보드는 `http://<host>:8080` 입니다. 로컬 페이지이며 클라우드로 전송하지 않습니다.

팩 데이터시트로 `config/battery_profile.json`을 채운 뒤의 실기 기동:

```bash
python -m battery_monitor --config config/battery_profile.json \
  --state /var/lib/battery-monitor/state.json \
  --history /var/lib/battery-monitor/history.sqlite
```

프로세스는 `i2c`와 `dialout` 그룹에 있어야 합니다. systemd 유닛은 `systemd/battery-monitor.service`입니다. `SIGTERM`이면 종료 전에 상태 파일을 기록합니다.

| 모듈 | 역할 |
|---|---|
| `battery_monitor/ina228.py` | INA228 레지스터 계산과 smbus2 드라이버 |
| `battery_monitor/tmp117.py` | 팩 온도 |
| `battery_monitor/sensors.py` | 하드웨어 버스, 스크립트 센서, 시뮬레이션 파형 |
| `battery_monitor/accounting.py` | 부호 있는 전력, Ah, Wh |
| `battery_monitor/soc.py` | 쿨롱 카운트 SOC와 휴지 OCV 보정 |
| `battery_monitor/faults.py` | 전압, 전류, 온도, 포화, 통신 |
| `battery_monitor/storage.py` | 원자적 JSON 상태, SQLite 이력 |
| `battery_monitor/lcd.py` | 20×4 PCF8574 LCD |
| `battery_monitor/uart_out.py` | `/dev/ttyTHS1` CSV 출력 |
| `battery_monitor/dashboard.py` | FastAPI 페이지와 SSE |
| `battery_monitor/service.py` | 루프, 시그널, CLI |

`config/battery_profile.json`의 명판 항목은 null입니다. `config/examples/example_DO_NOT_USE.json`은 형식 예시이며 실기에서 거부됩니다.
