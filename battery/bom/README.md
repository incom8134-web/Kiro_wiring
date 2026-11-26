# Bill of materials

[English](README.md) | [한국어](README.ko.md)

[`BOM.csv`](BOM.csv) is the parts list for the Jetson Orin Nano monitor in [`../README.md`](../README.md).

Prices are omitted. No Korean-supplier price was verified for this list, so the file has no price column.

BT1 is the YOLTON e-bike pack (Coupang 9101801616). Its chemistry, voltage, capacity, cell configuration, and current are TODO. Do not fill them from the listing title. The **BLOCKED** power-lead row cannot be ordered until the pack current is known. Do not size it from the module's 150 A rating, and do not substitute an example value from `software/config/examples/`. The 200 µΩ path is part of the Matek module, not a separate shunt to select. UART pins on the Jetson are optional and unused.
