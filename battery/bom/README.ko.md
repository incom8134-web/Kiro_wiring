# 자재 목록

[English](README.md) | [한국어](README.ko.md)

[`BOM.csv`](BOM.csv)는 [`../README.ko.md`](../README.ko.md)의 Jetson Orin Nano 모니터 부품표입니다.

가격은 넣지 않았습니다. 이 목록에 대해 확인된 한국 판매 가격이 없어서 가격 열이 없습니다.

BT1은 YOLTON e-bike pack (Coupang 9101801616)입니다. 화학은 li-ion, 공칭 12.0 V, 용량 45 Ah이고, 볼턴 상품 페이지는 LG 셀이라고 적습니다. 3S 한계인 최대 12.6 V와 최소 9.0 V는 3S 리튬이온으로 가정한 값입니다. 만충전에서 미터로 확인합니다. 충전 전류와 방전 전류는 미확인이며 null입니다. 충전은 12.6 V CC/CV 리튬이온 충전기(볼턴 전용 충전기)를 쓰고, 일반 12 V 전원 어댑터는 쓰지 않습니다. **BLOCKED** 전원선 행은 팩 전류가 정해지기 전에는 발주할 수 없습니다. 모듈의 150 A 정격으로 규격을 고르지 말고, `software/config/examples/`의 예시 값을 대신 쓰지 않습니다. 200 µΩ 경로는 Matek 모듈의 일부이며 따로 고르는 션트가 아닙니다. Jetson의 UART 핀은 선택 사항이며 쓰지 않습니다.
