#!/usr/bin/env python3
"""Draw the wiring diagram: Matek I2C-INA-BM, Jetson I2C, Jetson UART.

    python3 draw_wiring.py

Writes battery_monitor_wiring.svg and battery_monitor_wiring.png beside
this file. The PNG is 2400 px wide.

The module is the Matek I2C-INA-BM:
https://www.mateksys.com/?portfolio=i2c-ina-bm
Pack current goes in BAT+ and out ESC+. The JST-GH-4P carries 5V, SCL,
SDA, and G. Default address is decimal 69, which is 0x45 (SLYS021, A1=VS
and A0=VS, jumpers open). The 5V pin is a 4-9 V logic supply.

Pins follow the NVIDIA Jetson Nano Developer Kit User Guide, DA_09402,
connector J41. Pins 3 and 5 are /dev/i2c-1. Pins 8 and 10 are /dev/ttyTHS1.
Pin 2 is 5 V and feeds the module logic pin (about 1 mA). Pin 6 is ground.
Pin 1 is 3.3 V and must not feed the module. Do not use pin 4. Do not put
pack voltage on the header. The I2C pull-up rail on the module is unverified.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SVG_PATH = HERE / "battery_monitor_wiring.svg"
PNG_PATH = HERE / "battery_monitor_wiring.png"

W, H = 2400, 1280

INK = "#1c2833"
MUTED = "#34495e"
PAPER = "#ffffff"
CARD = "#f7f9fb"
EDGE = "#243140"
VIOLET = "#6c3483"
ORANGE = "#d35400"
BLUE = "#1a5276"
YELLOW = "#9a7d0a"
BLACK = "#1a1a1a"
GREEN = "#196f3d"
SLATE = "#566573"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Drawing:
    def __init__(self) -> None:
        self.parts: list[str] = []
        self.boxes: list[tuple[float, float, float, float]] = []
        self.wires: list[list[tuple[float, float]]] = []

    def add(self, fragment: str) -> None:
        self.parts.append(fragment)

    def rect(self, x, y, w, h, fill=CARD, stroke=EDGE, sw=2.5, rx=12):
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )
        self.boxes.append((x, y, w, h))

    def line(self, pts, color, sw=6):
        points = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.add(
            f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
        )
        self.wires.append(list(pts))

    def text(self, x, y, text, size=28, fill=INK, weight="normal", anchor="start"):
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}" '
            f'font-family="DejaVu Sans, sans-serif" font-weight="{weight}" '
            f'text-anchor="{anchor}">{esc(text)}</text>'
        )

    def svg(self) -> str:
        body = "\n".join(self.parts)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}">\n'
            f'<rect width="100%" height="100%" fill="{PAPER}"/>\n{body}\n</svg>\n'
        )

    def crossings(self) -> list[str]:
        found = []
        for pts in self.wires:
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
                for bx, by, bw, bh in self.boxes:
                    if bx + 4 < mx < bx + bw - 4 and by + 4 < my < by + bh - 4:
                        found.append(f"wire through box at {mx:.0f},{my:.0f}")
        return found


def wire(d: Drawing, x0, x1, y, color, label):
    d.line([(x0, y), (x1, y)], color)
    d.text((x0 + x1) / 2, y - 14, label, size=24, fill=color, weight="bold", anchor="middle")


def draw() -> Drawing:
    d = Drawing()
    d.text(48, 64, "Battery monitor wiring", size=40, weight="bold")
    d.text(
        48,
        108,
        "Matek I2C-INA-BM. Pack current is BAT+ to ESC+. JST-GH-4P is 5V, SCL, SDA, G. UART pins 8 and 10 are the data output.",
        size=24,
        fill=MUTED,
    )

    # Cards first so the crossing check knows their bounds. Wires stop at the edges.
    d.rect(40, 180, 460, 760)
    d.rect(860, 180, 500, 760)
    d.rect(1760, 150, 590, 620)
    d.rect(1760, 820, 590, 360)

    d.text(64, 230, "Pack current", size=32, weight="bold")
    d.text(64, 274, "through the module", size=24, fill=MUTED)
    d.text(64, 340, "BAT+  battery side", size=28, weight="bold")
    d.text(64, 400, "ESC+  load side", size=28, weight="bold")
    d.text(64, 470, "200 µΩ path, on the board", size=24, fill=MUTED)
    d.text(64, 520, "0–85 V, 150 A continuous", size=24, fill=MUTED)
    d.text(64, 570, "204.8 A burst", size=24, fill=MUTED)
    d.text(64, 660, "Power leads do not go to", size=24, fill=MUTED)
    d.text(64, 700, "the Jetson header.", size=24, fill=MUTED)
    d.text(64, 780, "Wire gauge is not chosen.", size=24, fill=MUTED)
    d.text(64, 820, "Pack current is unknown.", size=24, fill=MUTED)
    d.text(64, 880, "Positive current = discharge", size=22, fill=MUTED)

    wire(d, 500, 860, 360, VIOLET, "BAT+  →  ESC+")

    d.text(884, 230, "Matek I2C-INA-BM", size=32, weight="bold")
    d.text(884, 274, "address 0x45 (dec 69)", size=24, fill=MUTED)
    d.text(884, 318, "jumpers open. Also 0x44, 0x41", size=22, fill=MUTED)
    d.text(884, 390, "JST-GH-4P", size=26, weight="bold")
    d.text(1180, 450, "SDA", size=26, weight="bold", fill=BLUE, anchor="end")
    d.text(1180, 560, "SCL", size=26, weight="bold", fill=YELLOW, anchor="end")
    d.text(1180, 680, "5V  4–9 V", size=26, weight="bold", fill=ORANGE, anchor="end")
    d.text(1180, 800, "G", size=26, weight="bold", fill=BLACK, anchor="end")
    d.text(884, 880, "Shunt is on the module.", size=22, fill=MUTED)

    wire(d, 1360, 1760, 450, BLUE, "SDA")
    wire(d, 1360, 1760, 560, YELLOW, "SCL")
    wire(d, 1360, 1760, 680, ORANGE, "5 V")
    wire(d, 1360, 1760, 800, BLACK, "GND")
    d.text(1560, 880, "JST-GH-4P to J41", size=24, fill=INK, weight="bold", anchor="middle")

    d.text(1784, 200, "Jetson Nano J41", size=32, weight="bold")
    d.text(1784, 246, "I2C  /dev/i2c-1", size=26, fill=MUTED)
    d.text(1784, 310, "pin 3    SDA", size=28, fill=BLUE, weight="bold")
    d.text(1784, 365, "pin 5    SCL", size=28, fill=YELLOW, weight="bold")
    d.text(1784, 420, "pin 2    5 V logic", size=28, fill=ORANGE, weight="bold")
    d.text(1784, 475, "pin 6    GND", size=28, weight="bold")
    d.text(1784, 540, "Do not use pin 1 or pin 4.", size=24, fill=MUTED)
    d.text(1784, 580, "Measure SDA idle first.", size=24, fill=MUTED)
    d.text(1784, 630, "Do not put pack voltage", size=24, fill=MUTED)
    d.text(1784, 668, "on a header pin.", size=24, fill=MUTED)

    d.text(1784, 870, "UART output", size=32, weight="bold")
    d.text(1784, 920, "/dev/ttyTHS1, 3.3 V", size=26, fill=MUTED)
    d.text(1784, 990, "pin 8    TX", size=28, fill=GREEN, weight="bold")
    d.text(1784, 1050, "pin 10   RX", size=28, fill=SLATE, weight="bold")
    d.text(1784, 1120, "Serial log. Not the module.", size=24, fill=MUTED)

    d.text(
        48,
        1220,
        "Matek I2C-INA-BM (mateksys.com). TI INA228 SLYS021. NVIDIA Jetson Nano Developer Kit User Guide DA_09402, J41.",
        size=22,
        fill=MUTED,
    )
    return d


def write_png(svg_path: Path, png_path: Path) -> None:
    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-o", str(png_path), str(svg_path)], check=True)
        return
    try:
        import cairosvg
    except ImportError:
        print("need cairosvg or rsvg-convert", file=sys.stderr)
        raise SystemExit(1)
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=W, output_height=H)


def main() -> int:
    drawing = draw()
    hits = drawing.crossings()
    if hits:
        print("\n".join(hits), file=sys.stderr)
        return 1
    SVG_PATH.write_text(drawing.svg(), encoding="utf-8")
    write_png(SVG_PATH, PNG_PATH)
    print(f"wrote {SVG_PATH.name} and {PNG_PATH.name} ({W} x {H})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
