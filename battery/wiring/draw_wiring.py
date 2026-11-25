#!/usr/bin/env python3
"""Draw the wiring diagram: shunt, INA228, Jetson I2C, Jetson UART.

    python3 draw_wiring.py

Writes battery_monitor_wiring.svg and battery_monitor_wiring.png beside
this file. The PNG is 2400 px wide.

Pins follow the NVIDIA Jetson Nano Developer Kit User Guide, DA_09402,
connector J41. Interface signals are 3.3 V. Pins 3 and 5 are /dev/i2c-1
(module name I2C_2; wire the pin numbers). Pins 8 and 10 are /dev/ttyTHS1.
Pin 1 is 3.3 V. Pin 6 is ground. Do not power pins 2 and 4.

The INA228 address 0x40 with A1 and A0 at ground is TI SLYS021. The chip
has an I2C interface and no UART pins.
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
        "INA228 is I2C only. The sensor cable is J41 pins 1, 3, 5, and 6. UART pins 8 and 10 are the data output.",
        size=24,
        fill=MUTED,
    )

    # Cards first so the crossing check knows their bounds. Wires stop at the edges.
    d.rect(40, 180, 460, 760)
    d.rect(860, 180, 500, 760)
    d.rect(1760, 150, 590, 620)
    d.rect(1760, 820, 590, 360)

    d.text(64, 230, "External shunt", size=32, weight="bold")
    d.text(64, 274, "on the north plate of the case", size=24, fill=MUTED)
    d.text(64, 330, "4-terminal, high side", size=26)
    d.text(64, 374, "Battery lugs bolt to the shunt.", size=24, fill=MUTED)
    d.text(64, 470, "Battery side", size=26, weight="bold")
    d.text(64, 560, "Load side", size=26, weight="bold")
    d.text(64, 820, "Short leads into the sense slot.", size=24, fill=MUTED)
    d.text(64, 860, "Sense leads are unfused.", size=24, fill=MUTED)

    wire(d, 500, 860, 430, VIOLET, "IN+")
    wire(d, 500, 860, 560, VIOLET, "VBUS")
    wire(d, 500, 860, 700, VIOLET, "IN−")
    d.text(680, 790, "sense cable", size=24, fill=VIOLET, weight="bold", anchor="middle")

    d.text(884, 230, "INA228 breakout", size=32, weight="bold")
    d.text(884, 274, "address 0x40", size=24, fill=MUTED)
    d.text(884, 330, "A1 and A0 to GND", size=24)
    d.text(884, 372, "VS from pin 1, 3.3 V", size=24)
    d.text(884, 430, "IN+", size=26, weight="bold", fill=VIOLET)
    d.text(884, 560, "VBUS", size=26, weight="bold", fill=VIOLET)
    d.text(884, 700, "IN−", size=26, weight="bold", fill=VIOLET)
    d.text(884, 900, "Positive current = discharge", size=22, fill=MUTED)
    d.text(1180, 430, "SDA", size=26, weight="bold", fill=BLUE, anchor="end")
    d.text(1180, 560, "SCL", size=26, weight="bold", fill=YELLOW, anchor="end")
    d.text(1180, 680, "3.3 V", size=26, weight="bold", fill=ORANGE, anchor="end")
    d.text(1180, 800, "GND", size=26, weight="bold", fill=BLACK, anchor="end")

    wire(d, 1360, 1760, 430, BLUE, "SDA")
    wire(d, 1360, 1760, 560, YELLOW, "SCL")
    wire(d, 1360, 1760, 680, ORANGE, "3.3 V")
    wire(d, 1360, 1760, 800, BLACK, "GND")
    d.text(1560, 880, "sensor cable", size=24, fill=INK, weight="bold", anchor="middle")

    d.text(1784, 200, "Jetson Nano J41", size=32, weight="bold")
    d.text(1784, 250, "I2C  /dev/i2c-1", size=26, fill=MUTED)
    d.text(1784, 330, "pin 3    SDA", size=28, fill=BLUE, weight="bold")
    d.text(1784, 390, "pin 5    SCL", size=28, fill=YELLOW, weight="bold")
    d.text(1784, 450, "pin 1    3.3 V", size=28, fill=ORANGE, weight="bold")
    d.text(1784, 510, "pin 6    GND", size=28, weight="bold")
    d.text(1784, 580, "Do not use pins 2 or 4.", size=24, fill=MUTED)
    d.text(1784, 630, "Do not put pack voltage", size=24, fill=MUTED)
    d.text(1784, 668, "on a header pin.", size=24, fill=MUTED)

    d.text(1784, 870, "UART output", size=32, weight="bold")
    d.text(1784, 920, "/dev/ttyTHS1, 3.3 V", size=26, fill=MUTED)
    d.text(1784, 990, "pin 8    TX", size=28, fill=GREEN, weight="bold")
    d.text(1784, 1050, "pin 10   RX", size=28, fill=SLATE, weight="bold")
    d.text(1784, 1120, "Serial log. Not the INA228.", size=24, fill=MUTED)

    d.text(48, 1220, "TI INA228 datasheet SLYS021. NVIDIA Jetson Nano Developer Kit User Guide DA_09402, connector J41.", size=22, fill=MUTED)
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
