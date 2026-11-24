#!/usr/bin/env python3
"""Draw the pin-level wiring diagram for the Jetson Nano battery monitor.

Writes battery_monitor_wiring.svg (editable source) and
battery_monitor_wiring.png beside this file.

    python3 draw_wiring.py

Needs cairosvg or rsvg-convert for the PNG. The PNG is 2400 px wide.

Pins follow battery/README.md and the NVIDIA Jetson Nano Developer Kit User
Guide, DA_09402, connector J41:

- Interface signals are 3.3 V. The guide gives two 3.3 V pins and two 5 V pins.
- Pins 3 and 5, and pins 27 and 28, are the I2C SDA/SCL pairs.
- Pins 8 and 10 are UART TX and RX.
- Pins 3 and 5 are Linux /dev/i2c-1. The module signal name on that pair is
  I2C_2. Wire the pin number, not the I2C_2 name.
- Pins 8 and 10 are /dev/ttyTHS1.
- Pins 27 and 28 are the other pair (Linux /dev/i2c-0), shared with the
  camera. This monitor does not use them.
- Pin 1 is 3.3 V, pins 2 and 4 are 5 V, pins 6 and 9 are ground, in the J41
  numbering used by the design table and by Jetson.GPIO. Do not power pins
  2 and 4 while J25 is powered.

INA228 address 0x40 (A1 and A0 at ground) is TI SLYS021. TMP117 address
0x48 (ADD0 at ground) is TI SNOSD82. The Adafruit INA228 breakout prints
VIN for VS and ALRT for ALERT.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SVG_PATH = HERE / "battery_monitor_wiring.svg"
PNG_PATH = HERE / "battery_monitor_wiring.png"

W, H = 2400, 2900

RED = "#b03a2e"
BLACK = "#1a1a1a"
ORANGE = "#d35400"
BROWN = "#8d5524"
BLUE = "#1a5276"
YELLOW = "#9a7d0a"
GREEN = "#196f3d"
SLATE = "#566573"
VIOLET = "#6c3483"
INK = "#1c2833"
MUTED = "#34495e"
PAPER = "#ffffff"
CARD = "#f7f9fb"
EDGE = "#243140"
WARN = "#7b241c"
DASH = "#7f8c8d"

# Sense-column x positions. Shared by the shunt taps and the drops below them.
VBUS_X, KP_X, KM_X = 530, 700, 880
SPINE = 360
GND_Y = 518
RAIL = {"3v3": 1920, "sda": 2000, "scl": 2080, "gnd": 2160}
PIN9, PIN8, PIN10 = 2240, 2400, 2480
JETSON_X = 1760


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Drawing:
    def __init__(self) -> None:
        self.parts: list[str] = []
        self.boxes: list[dict] = []
        self.wires: list[dict] = []

    def add(self, fragment: str) -> None:
        self.parts.append(fragment)

    def rect(self, x, y, w, h, fill=CARD, stroke=EDGE, sw=2, rx=10, dash=None, name="", allow=()):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>'
        )
        allowed = None if allow is None else set(allow)
        self.boxes.append({"name": name, "rect": (x, y, w, h), "allow": allowed})

    def line(self, pts, color, sw=5, dash=None, name=""):
        points = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linejoin="round" stroke-linecap="round"{extra}/>'
        )
        self.wires.append({"name": name, "pts": list(pts), "color": color})

    def dot(self, x, y, color, r=7):
        self.add(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="{PAPER}" stroke-width="2"/>'
        )

    def text(self, x, y, text, size=24, fill=INK, weight="normal", anchor="start"):
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}" '
            f'font-family="DejaVu Sans, sans-serif" font-weight="{weight}" '
            f'text-anchor="{anchor}">{esc(text)}</text>'
        )

    def tag(self, x, y, text, fill, size=22, anchor="middle"):
        width = len(text) * size * 0.58 + 16
        left = {"middle": x - width / 2, "start": x, "end": x - width}[anchor]
        self.rect(left, y - size, width, size + 10, fill=PAPER, stroke="none", sw=0, rx=4, name="tag", allow=None)
        self.text(x, y, text, size=size, fill=fill, weight="bold", anchor=anchor)

    def crossings(self) -> list[str]:
        found = []
        for wire in self.wires:
            pts = wire["pts"]
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                for box in self.boxes:
                    if box["allow"] is None or wire["name"] in box["allow"]:
                        continue
                    bx, by, bw, bh = box["rect"]
                    if abs(y1 - y2) < 1:
                        y = (y1 + y2) / 2
                        xa, xb = sorted((x1, x2))
                        if by + 4 < y < by + bh - 4 and xa < bx + bw - 4 and xb > bx + 4:
                            if min(xb, bx + bw) - max(xa, bx) > 8:
                                found.append(f"{wire['name'] or wire['color']} crosses {box['name']} at y={y:.0f}")
                    elif abs(x1 - x2) < 1:
                        x = (x1 + x2) / 2
                        ya, yb = sorted((y1, y2))
                        if bx + 4 < x < bx + bw - 4 and ya < by + bh - 4 and yb > by + 4:
                            if min(yb, by + bh) - max(ya, by) > 8:
                                found.append(f"{wire['name'] or wire['color']} crosses {box['name']} at x={x:.0f}")
        return found

    def save(self, path: Path) -> None:
        body = "\n".join(self.parts)
        path.write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'<rect width="{W}" height="{H}" fill="{PAPER}"/>\n{body}\n</svg>\n'
        )


def header(d: Drawing) -> None:
    d.text(36, 50, "Jetson Nano battery monitor — pin wiring", size=42, weight="bold")
    d.text(
        36,
        90,
        "Follow the colored lines. Colors are suggested. A crossing without a dot does not connect.",
        size=24,
        fill=MUTED,
    )
    d.text(
        36,
        122,
        "Pack voltage stays on the violet wires. It never lands on a header pin. Red pack + is not orange 3.3 V.",
        size=24,
        fill=MUTED,
    )
    items = [
        (RED, "Red  pack +"),
        (BLACK, "Black  GND"),
        (ORANGE, "Orange  3.3 V"),
        (BROWN, "Brown  5 V"),
        (BLUE, "Blue  SDA"),
        (YELLOW, "Yellow  SCL"),
        (GREEN, "Green  TXD"),
        (SLATE, "Gray  RXD"),
        (VIOLET, "Violet  sense"),
    ]
    x = 36
    for color, name in items:
        d.line([(x, 162), (x + 40, 162)], color, 8, name="legend")
        d.text(x + 48, 170, name, size=22, weight="bold")
        x += 48 + int(len(name) * 22 * 0.56) + 26
    d.text(
        36,
        206,
        "Dashed gray, ending in X: USB–I2C alternate. Do not connect it and pins 3 and 5 together.",
        size=22,
        fill=DASH,
    )


def power(d: Drawing) -> None:
    """Left-to-right pack current. Violet taps leave downward and are not this current."""
    y = SPINE
    d.text(36, 248, "1    Power, left to right. Arrow is discharge current.", size=28, weight="bold")

    d.rect(36, 280, 190, 160, name="battery")
    d.text(131, 322, "Battery", size=28, weight="bold", anchor="middle")
    d.text(100, 366, "BAT+", size=26, weight="bold", fill=RED)
    d.dot(226, y, RED, 8)
    d.dot(110, 440, BLACK, 8)
    d.text(124, 436, "BAT−", size=22, weight="bold")

    d.line([(226, y), (270, y)], RED, 8, name="pack+")
    d.rect(270, 308, 150, 104, fill="#fdedec", stroke=RED, sw=3, rx=8, name="f1", allow={"pack+"})
    d.text(345, 346, "F1", size=28, weight="bold", anchor="middle", fill=RED)
    d.text(345, 384, "main fuse", size=20, anchor="middle", fill=RED)
    d.text(345, 406, "before shunt", size=18, anchor="middle", fill=MUTED)
    d.line([(420, y), (470, y)], RED, 8, name="pack+")

    d.rect(470, 276, 520, 254, name="shunt", allow={"pack+", "vbus", "k+", "k-"})
    d.text(730, 308, "Shunt — outside the box", size=24, weight="bold", anchor="middle")
    d.rect(640, 324, 180, 28, fill="#f5eef8", stroke=VIOLET, sw=2, rx=4, name="element", allow={"pack+"})
    d.text(730, 344, "element", size=18, anchor="middle", fill=VIOLET)
    d.line([(470, y), (990, y)], RED, 8, name="pack+")
    d.dot(470, y, RED, 8)
    d.dot(990, y, RED, 8)
    d.text(548, 400, "P+  power", size=22, weight="bold", fill=RED)
    d.text(548, 424, "battery side", size=20, fill=RED)
    d.text(970, 400, "P−  power", size=22, weight="bold", anchor="end", fill=RED)
    d.text(970, 424, "bus side", size=20, anchor="end", fill=RED)

    d.dot(VBUS_X, y, VIOLET, 7)
    d.line([(VBUS_X, y), (VBUS_X, 530)], VIOLET, 5, name="vbus")
    d.dot(KP_X, 490, VIOLET, 7)
    d.dot(KM_X, 490, VIOLET, 7)
    d.line([(KP_X, 490), (KP_X, 530)], VIOLET, 5, name="k+")
    d.line([(KM_X, 490), (KM_X, 530)], VIOLET, 5, name="k-")
    d.text(KP_X, 472, "K+ Kelvin", size=18, weight="bold", anchor="middle", fill=VIOLET)
    d.text(KM_X, 472, "K− Kelvin", size=18, weight="bold", anchor="middle", fill=VIOLET)

    d.line([(990, y), (1080, y)], RED, 8, name="pack+")
    d.dot(1080, y, RED, 8)
    d.text(1160, 348, "bus +    discharge →", size=22, weight="bold", fill=RED)

    d.line([(1080, y), (1080, 300), (1180, 300)], RED, 6, name="load")
    d.rect(1180, 272, 160, 56, fill="#fdedec", stroke=RED, sw=2, name="load")
    d.text(1260, 308, "Load +", size=24, weight="bold", anchor="middle", fill=RED)

    d.line([(1080, y), (1080, 448), (1180, 448)], RED, 6, name="charger")
    d.rect(1180, 420, 190, 56, fill="#fdedec", stroke=RED, sw=2, name="charger")
    d.text(1275, 456, "Charger +", size=24, weight="bold", anchor="middle", fill=RED)

    d.line([(1080, y), (1400, y)], RED, 8, name="pack+")
    d.rect(1400, 328, 100, 64, fill="#fdedec", stroke=RED, sw=3, rx=8, name="f2", allow={"pack+"})
    d.text(1450, 368, "F2", size=26, weight="bold", anchor="middle", fill=RED)
    d.line([(1500, y), (1580, y)], RED, 8, name="pack+")
    d.text(1396, 414, "buck branch", size=18, fill=MUTED)

    d.rect(1580, 292, 240, 182, name="buck")
    d.text(1700, 320, "Buck", size=26, weight="bold", anchor="middle")
    d.text(1700, 346, "5.0–5.25 V, 4 A", size=18, anchor="middle", fill=MUTED)
    d.dot(1580, y, RED, 8)
    d.text(1596, 392, "IN+", size=20, weight="bold", fill=RED)
    d.dot(1580, 430, BLACK, 7)
    d.text(1596, 454, "IN− GND", size=20, weight="bold")
    d.dot(1820, 330, BROWN, 8)
    d.text(1804, 392, "OUT+", size=20, weight="bold", anchor="end", fill=BROWN)
    d.dot(1820, 430, BLACK, 7)
    d.text(1804, 454, "OUT−", size=20, weight="bold", anchor="end")

    d.line([(1820, 330), (1900, 330)], BROWN, 8, name="5v")
    d.rect(1900, 286, 460, 150, fill="#fdf2e9", stroke=BROWN, sw=3, name="j25")
    d.text(2130, 322, "J25 barrel", size=26, weight="bold", anchor="middle")
    d.text(2130, 354, "center pin = OUT+", size=22, anchor="middle", fill=BROWN)
    d.text(2130, 382, "sleeve = OUT− / GND", size=22, anchor="middle")
    d.text(2130, 410, "J48 fitted: barrel, not Micro-USB", size=18, anchor="middle", fill=MUTED)
    d.dot(1900, 330, BROWN, 8)
    d.dot(2360, 436, BLACK, 8)

    d.line([(1580, 430), (1580, GND_Y), (2360, GND_Y), (2360, 436)], BLACK, 6, name="gnd-right")
    d.line([(1080, GND_Y), (1580, GND_Y)], BLACK, 6, name="gnd-right")
    d.tag(1610, 496, "GND:  load −, charger −, buck IN−, J25 sleeve", BLACK, size=18, anchor="start")

    d.rect(1900, 530, 460, 108, fill="#fdedec", stroke=WARN, sw=2, name="warn-5v")
    d.text(1920, 568, "Do not power pins 2 and 4.", size=22, weight="bold", fill=WARN)
    d.text(1920, 598, "J25 is the only 5 V into the Jetson.", size=20, fill=WARN)
    d.text(1920, 624, "Not both. Header 5 V is not this supply.", size=20, fill=WARN)

    d.line([(110, 440), (110, 470), (16, 470)], BLACK, 6, name="gnd-left")


def sense_and_chips(d: Drawing):
    d.text(
        36,
        590,
        "2    Sense. Violet is pack voltage. These wires are not the load current.",
        size=26,
        weight="bold",
        fill=VIOLET,
    )

    ina_top = 900
    runs = [
        (VBUS_X, "vbus", "from P+", "F3", "100Ω", "VBUS"),
        (KP_X, "k+", "from K+", "F3", "10Ω", "IN+"),
        (KM_X, "k-", "from K−", "F3", "10Ω", "IN−"),
    ]
    for x, name, src, fuse, res, dst in runs:
        d.line([(x, 530), (x, ina_top)], VIOLET, 5, name=name)
        d.rect(x - 34, 640, 68, 40, fill="#f5eef8", stroke=VIOLET, sw=2, rx=6, name=f"{fuse}-{name}", allow={name})
        d.text(x, 668, fuse, size=20, weight="bold", anchor="middle", fill=VIOLET)
        d.rect(x - 40, 720, 80, 42, fill="#f5eef8", stroke=VIOLET, sw=2, rx=6, name=f"{res}-{name}", allow={name})
        d.text(x, 750, res, size=22, weight="bold", anchor="middle", fill=VIOLET)
        d.text(x, 804, src, size=18, anchor="middle", fill=VIOLET)
        d.text(x, 878, dst, size=22, weight="bold", anchor="middle", fill=VIOLET)
        d.dot(x, ina_top, VIOLET, 7)

    d.text(1040, 668, "F3 = 100 mA, at the shunt end of each wire.", size=22, fill=VIOLET)
    d.text(1040, 700, "F3 voltage rating is still open.", size=22, fill=VIOLET)
    d.text(1040, 732, "10 Ω next to the INA. 100 Ω on VBUS only.", size=22, fill=VIOLET)
    d.text(1040, 764, "IN+ above IN− means discharge.", size=22, fill=VIOLET)
    d.text(1040, 796, "VBUS is tapped at P+, the battery side.", size=22, fill=VIOLET)
    d.text(1040, 828, "The resistors do not replace F3.", size=22, fill=VIOLET)

    chips = [
        (
            900,
            250,
            "INA228 breakout     address 0x40",
            [
                "Strap A1 and A0 to this GND pin.",
                "VIN is chip VS. ALRT (ALERT) stays open.",
                "VIN from pin 1 only. Never 5 V.",
            ],
            [("VIN = VS", ORANGE, "3v3"), ("SDA", BLUE, "sda"), ("SCL", YELLOW, "scl"), ("GND", BLACK, "gnd")],
        ),
        (
            1170,
            230,
            "TMP117 on the pack     address 0x48",
            [
                "Strap ADD0 to this GND pin.",
                "V+ from pin 1. ALERT is not used.",
                "Pack temperature, not the INA die.",
            ],
            [("V+", ORANGE, "3v3"), ("SDA", BLUE, "sda"), ("SCL", YELLOW, "scl"), ("GND", BLACK, "gnd")],
        ),
        (
            1420,
            230,
            "LCD backpack, PCF8574",
            [
                "Four pins: GND, VCC, SDA, SCL.",
                "Match the silkscreen. Address 0x27 or 0x3F.",
                "Drawn at 3.3 V from pin 1. No shifter.",
            ],
            [("VCC", ORANGE, "3v3"), ("SDA", BLUE, "sda"), ("SCL", YELLOW, "scl"), ("GND", BLACK, "gnd")],
        ),
    ]
    right = 1000
    # GND is the leftmost bus and runs the lowest, so each Jetson run
    # leaves its bus to the right and does not cross the next bus.
    buses = {"gnd": 1120, "scl": 1210, "sda": 1300, "3v3": 1390}
    colors = {"3v3": ORANGE, "sda": BLUE, "scl": YELLOW, "gnd": BLACK}
    taps: dict[str, list[float]] = {key: [] for key in buses}

    for top, height, title, lines, pins in chips:
        d.rect(36, top, right - 36, height, name=title.split()[0])
        d.text(56, top + 40, title, size=26, weight="bold")
        for i, line in enumerate(lines):
            d.text(56, top + 86 + i * 34, line, size=22, fill=MUTED)
        for i, (name, color, key) in enumerate(pins):
            py = top + 58 + i * 52
            d.dot(right, py, color, 7)
            d.text(right - 16, py + 8, name, size=22, weight="bold", anchor="end", fill=color)
            d.line([(right, py), (buses[key], py)], color, 5, name=key)
            d.dot(buses[key], py, color, 6)
            taps[key].append(py)

    d.rect(36, 1670, right - 36, 156, fill="#fef9e7", stroke="#9a7d0a", sw=2, name="lcd5")
    d.text(56, 1708, "Only if the LCD backpack is 5 V", size=24, weight="bold")
    d.text(56, 1744, "Do not tie VCC to pin 1. Power VCC from 5 V.", size=22)
    d.text(56, 1776, "BSS138 shifter on SDA and SCL only (NXP AN10441).", size=22)
    d.text(56, 1808, "Low side 3.3 V, high side 5 V. INA228 and TMP117 stay on 3.3 V.", size=22)

    for key, x in buses.items():
        d.line([(x, min(taps[key])), (x, RAIL[key])], colors[key], 6, name=key)
        d.dot(x, RAIL[key], colors[key], 7)
    return buses, colors


def jetson(d: Drawing, buses, colors) -> None:
    jx = JETSON_X
    d.line([(buses["3v3"], RAIL["3v3"]), (jx, RAIL["3v3"])], ORANGE, 6, name="3v3")
    d.line([(buses["sda"], RAIL["sda"]), (jx, RAIL["sda"])], BLUE, 6, name="sda")
    d.line([(buses["scl"], RAIL["scl"]), (jx, RAIL["scl"])], YELLOW, 6, name="scl")
    d.line([(buses["gnd"], RAIL["gnd"]), (jx, RAIL["gnd"])], BLACK, 6, name="gnd")
    d.tag(1560, RAIL["3v3"] - 16, "3.3 V   pin 1", ORANGE, size=22)
    d.tag(1560, RAIL["sda"] - 16, "SDA   pin 3   /dev/i2c-1", BLUE, size=22)
    d.tag(1560, RAIL["scl"] - 16, "SCL   pin 5   /dev/i2c-1", YELLOW, size=22)
    d.tag(1560, RAIL["gnd"] - 16, "GND   pin 6", BLACK, size=22)

    d.line([(16, 470), (16, RAIL["gnd"]), (buses["gnd"], RAIL["gnd"])], BLACK, 6, name="gnd-left")
    d.dot(buses["gnd"], RAIL["gnd"], BLACK, 7)

    d.line([(jx, PIN9), (1660, PIN9), (1660, RAIL["gnd"])], BLACK, 5, name="gnd")
    d.dot(jx, PIN9, BLACK, 7)

    d.rect(36, 2280, 1240, 270, name="logger")
    d.text(56, 2320, "UART logger     /dev/ttyTHS1     115200 8N1     3.3 V", size=26, weight="bold")
    d.text(56, 2356, "Short cable. No extra pull-up. Not a 5 V USB-serial.", size=22, fill=MUTED)
    d.text(56, PIN8 + 8, "Pin 8 TXD  →  logger RX", size=24, weight="bold", fill=GREEN)
    d.text(620, PIN10 + 8, "Pin 10 RXD  ←  logger TX, optional", size=24, weight="bold", fill=SLATE)
    d.text(56, 2532, "Logger GND to pin 6, or to pin 9 if pin 6 is already used.", size=22)
    d.dot(1276, PIN8, GREEN, 8)
    d.dot(1276, PIN10, SLATE, 8)
    d.line([(1276, PIN8), (jx, PIN8)], GREEN, 6, name="txd")
    d.line([(1276, PIN10), (jx, PIN10)], SLATE, 6, name="rxd")
    d.tag(1520, PIN8 - 16, "pin 8 TXD", GREEN, size=22)
    d.tag(1520, PIN10 - 16, "pin 10 RXD", SLATE, size=22)

    d.rect(jx, 1836, 600, 820, name="jetson")
    d.text(jx + 20, 1876, "Jetson Nano  J41", size=28, weight="bold")
    rows = [
        (RAIL["3v3"], "1", "3.3 V", ORANGE, "out only, not a supply"),
        (RAIL["sda"], "3", "SDA", BLUE, "/dev/i2c-1, module I2C_2"),
        (RAIL["scl"], "5", "SCL", YELLOW, "/dev/i2c-1"),
        (RAIL["gnd"], "6", "GND", BLACK, "common with BAT−"),
        (PIN9, "9", "GND", BLACK, "if pin 6 is busy"),
        (PIN8, "8", "TXD", GREEN, "/dev/ttyTHS1 to logger RX"),
        (PIN10, "10", "RXD", SLATE, "/dev/ttyTHS1 from logger TX"),
    ]
    for y, num, name, color, note in rows:
        d.dot(jx, y, color, 8)
        d.text(jx + 20, y + 8, f"{num}   {name}", size=24, weight="bold", fill=color)
        d.text(jx + 160, y + 8, note, size=20, fill=MUTED)
    d.text(jx + 20, 2560, "Pins 2 and 4 = 5 V. Do not feed them.", size=20, weight="bold", fill=WARN)
    d.text(jx + 20, 2592, "Pins 27 and 28: other I2C. Leave them if a camera is fitted.", size=18, fill=MUTED)
    d.text(jx + 20, 2622, "Signals are 3.3 V. Unlisted pins are unused here.", size=18, fill=MUTED)

    d.rect(36, 2588, 980, 160, fill="#f4f6f7", stroke=DASH, sw=2, dash="10 7", name="usb")
    d.text(56, 2624, "USB–I2C    ALTERNATE", size=26, weight="bold", fill=DASH)
    d.text(56, 2660, "USB cable → Jetson J32 or J33.", size=22, fill=DASH)
    d.text(56, 2692, "Adapter SDA, SCL, and GND, at 3.3 V.", size=22, fill=DASH)
    d.text(56, 2724, "Do not connect both this and pins 3 and 5.", size=22, weight="bold", fill=DASH)
    for i, label in enumerate(("SDA", "SCL", "GND")):
        yy = 2632 + i * 32
        d.line([(1016, yy), (1140, yy)], DASH, 4, dash="8 6", name="usb-stub")
        d.text(1078, yy - 6, label, size=18, fill=DASH, anchor="middle")
    d.rect(1160, 2648, 52, 52, fill=PAPER, stroke=DASH, sw=3, name="usb-x")
    d.text(1186, 2684, "X", size=30, weight="bold", anchor="middle", fill=DASH)
    d.text(1228, 2682, "not connected", size=22, weight="bold", fill=DASH)


def footer(d: Drawing) -> None:
    d.text(
        36,
        2804,
        "Sources: NVIDIA Jetson Nano Developer Kit User Guide DA_09402, connector J41. Pins 3 and 5, and 27 and 28, are I2C. Pins 8 and 10 are UART TX and RX. Signals are 3.3 V.",
        size=18,
        fill=MUTED,
    )
    d.text(
        36,
        2834,
        "Pin 1 = 3.3 V, pins 2 and 4 = 5 V, pins 6 and 9 = GND, as in battery/README.md and the J41 header map. On the module, I2C_2 is pins 3 and 5. Wire the pin numbers.",
        size=18,
        fill=MUTED,
    )
    d.text(
        36,
        2864,
        "Editable source: battery/wiring/draw_wiring.py and battery/wiring/battery_monitor_wiring.svg. Colors on this figure are suggested.",
        size=18,
        fill=MUTED,
    )


def render_png(svg: Path, png: Path) -> None:
    try:
        import cairosvg
    except ImportError:
        cairosvg = None
    if cairosvg is not None:
        cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=W, output_height=H)
        return
    rsvg = shutil.which("rsvg-convert")
    if not rsvg:
        sys.exit("Install cairosvg or rsvg-convert to write the PNG.")
    subprocess.check_call([rsvg, "-w", str(W), "-h", str(H), "-o", str(png), str(svg)])


def main() -> None:
    d = Drawing()
    header(d)
    power(d)
    buses, colors = sense_and_chips(d)
    jetson(d, buses, colors)
    footer(d)
    hits = d.crossings()
    d.save(SVG_PATH)
    render_png(SVG_PATH, PNG_PATH)
    print(f"wrote {SVG_PATH.name} and {PNG_PATH.name} ({W}x{H})")
    if hits:
        print(f"{len(hits)} wire/box crossings:")
        for hit in hits:
            print(" -", hit)
        sys.exit(1)


if __name__ == "__main__":
    main()
