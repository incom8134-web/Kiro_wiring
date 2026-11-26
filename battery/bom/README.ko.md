# 자재 목록

[English](README.md) | [한국어](README.ko.md)

[`BOM.csv`](BOM.csv)는 [`../README.ko.md`](../README.ko.md)의 Jetson Orin Nano 모니터 부품표입니다.

가격은 넣지 않았습니다. 이 목록에 대해 확인된 한국 판매 가격이 없어서 가격 열이 없습니다.

BT1은 YOLTON e-bike pack (Coupang 9101801616)입니다. 화학, 전압, 용량, 셀 구성, 전류는 TODO입니다. 상품 제목으로 채우지 않습니다. **BLOCKED** 전원선 행은 팩 전류가 정해지기 전에는 발주할 수 없습니다. 모듈의 150 A 정격으로 규격을 고르지 말고, `software/config/examples/`의 예시 값을 대신 쓰지 않습니다. 200 µΩ 경로는 Matek 모듈의 일부이며 따로 고르는 션트가 아닙니다. Jetson의 UART 핀은 선택 사항이며 쓰지 않습니다.
