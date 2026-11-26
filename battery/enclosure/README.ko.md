# Matek I2C-INA-BM 상자

[English](README.md) | [한국어](README.ko.md)

Matek I2C-INA-BM용 베이스와 뚜껑이다. 션트는 모듈의 도통 경로이므로 션트 판은 없다. Jetson은 원래 자리에 둔다.

몸체 **33.8 × 26.8 × 11.8 mm**. 체결 탭 둘을 넣으면 베이스는 **49.8 × 26.8 × 10.0 mm**. 안쪽 **29.4 × 22.4 × 8.2 mm**. 벽 2.2 mm, 바닥 1.8 mm, 뚜껑 1.8 mm. 끼워맞춤은 면마다 1.2 mm. 뚜껑 STL은 바깥 면이 베드에 있고 **33.8 × 26.8 × 4.2 mm**다.

기판 크기는 Matek가 공개한 27 × 20 × 6 mm다 ([제품 페이지](https://www.mateksys.com/?portfolio=i2c-ina-bm)). 1.2 mm 모서리 패드 위에 두어, Matek가 데드 패드라고 한 바닥 면이 바닥에 눌리지 않게 한다. 모서리 리브가 기판을 자리 잡는다. PCB를 관통하는 나사는 없다. 판매처가 말한 φ3 mm 구멍은 Matek 페이지에 없고, 여기서 쓰지 않는다.

개구는 모두 위가 열려 있어 서포트가 필요 없다.

| 개구 | 위치 | 크기 |
|---|---|---|
| 전원선 | 짧은 벽 양쪽, BAT+와 ESC+ | 폭 6 mm. 인쇄용 기본값이며 고른 전선 규격이 아니다. 팩 전류는 모른다. |
| JST-GH | 긴 벽 한쪽에 두 개 | 폭 11 mm |

JST 면은 치수도가 아니라 제품 사진을 따른다. 도면이 다르면 `enclosure.py`의 `JST_W`, `WIRE_W`, 위치를 바꾼다.

탭마다 M3 클리어런스 구멍 하나, 3.4 mm (ISO 273 중간). 뚜껑은 스커트가 있는 끼움 덮개다. 나사로 잠그지 않는다.

베이스는 바닥을 베드에 둔다. 뚜껑 STL은 이미 바깥 면이 베드에 있다. PLA 또는 PETG, 레이어 0.2 mm, 노즐 0.4 mm, Anycubic Kossel Linear Plus. 바닥과 뚜껑의 통풍구는 기판 위 션트 쪽에 있다.

| 매개변수 | 기본값 | 확인되지 않은 이유 |
|---|---|---|
| `BOARD_X`, `BOARD_Y`, `BOARD_Z` | 27, 20, 6 mm | Matek가 공개한 모듈 크기. 6 mm는 측정한 납땜면 높이가 아니다. |
| `STANDOFF` | 1.2 mm | 데드 패드 아래 간격. Matek 치수가 아니다. |
| `AIR` | 1.0 mm | 모듈 위에서 뚜껑까지. |
| `WIRE_W` | 6.0 mm | 개구이지 전선이 아니다. 팩 전류는 모른다. |
| `JST_W` | 11.0 mm | JST-GH-4P 플러그의 사진 추정과 여유. |
| `FIT` | 1.2 mm | 면마다, 기판이 들어가게. |
| `TAB_LEN`, `TAB_W` | 8 mm, 10 mm | 로봇 도면에서 온 값이 아니다. |

```bash
python3 enclosure.py
```

출력: `export/base.step`, `export/base.stl`, `export/lid.step`, `export/lid.stl`, `export/assembly.step`, `export/dimensions.json`, `export/manifold.txt`, `preview.png`.

마지막 확인: 베이스와 뚜껑은 닫힌 메쉬이고 와인딩이 맞다. 간섭 0 mm³. 베이스 부피 3537.653 mm³, 크기 49.8 × 26.8 × 10.0 mm. 뚜껑 부피 1808.772 mm³, 크기 33.8 × 26.8 × 4.2 mm.

출처: [Matek I2C-INA-BM](https://www.mateksys.com/?portfolio=i2c-ina-bm), ISO 273.
