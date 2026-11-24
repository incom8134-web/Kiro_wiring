#!/usr/bin/env python3
"""Display and sense pod for the hover-robot head.

The Jetson Nano, the buck, and the main fuse are not in this box. The shunt
stays at the battery. This shell holds the LCD, the INA228, and the USB-I2C
adapter, and it bolts to the robot on two rear flanges.

Run from this directory:

    python3 enclosure.py

Writes STEP and STL for the base and the lid, an assembly STEP, a preview
PNG, and export/dimensions.json. Dimensions are millimetres.

Printed parts are the base and the lid only. The assembly STEP also contains
reference envelopes (names start with REF_). Envelopes are not for printing.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import cadquery as cq
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = Path(__file__).resolve().parent
EXPORT = HERE / "export"

# ---------------------------------------------------------------------------
# Verified geometry
# ---------------------------------------------------------------------------

# Winstar WH2004A contour drawing (WH2004A-YYH-JT / WH2004A-TMI-JT Rev K).
# Module 98.0 x 60.0 x 13.6 mm MAX. View area 77.0 x 25.2. Four Ø2.5 PTH.
# Hole pitch 93.0 mm (X) and 55.0 mm (Y), inset 2.5 mm from the edges.
# Drawing margins (98.0-77.0)/2 = 10.5 and (60.0-25.2)/2 = 17.4 match the
# 10.5 and 17.4 figures on that drawing, so the view area is centered.
# https://www.winstar.com.tw/uploads/files/6e5109c5ba979085d164c6b48a5bb66d.pdf
LCD_X = 98.0
LCD_Y = 60.0
LCD_Z_MAX = 13.6
LCD_VIEW_X = 77.0
LCD_VIEW_Y = 25.2
LCD_HOLE_D = 2.5
LCD_HOLE_INSET = 2.5
LCD_HOLE_PITCH_X = 93.0
LCD_HOLE_PITCH_Y = 55.0

# Adafruit INA228 breakout, product 5832.
# PCB outline and holes measured from Adafruit's Eagle board
# (adafruit/Adafruit-INA228-PCB, "Adafruit INA228 I2C Power Monitor.brd"):
# outline 25.4 x 20.32 mm with 2.54 mm corner chamfers, two 2.5 mm
# mounting holes at (2.54, 17.78) and (22.86, 17.78) mm.
# Assembled product size from the Adafruit product page: 25.8 x 20.2 x 10.1 mm.
# https://www.adafruit.com/product/5832
INA_PCB_X = 25.4
INA_PCB_Y = 20.32
INA_HOLES = ((2.54, 17.78), (22.86, 17.78))
INA_HOLE_D = 2.5
INA_PRODUCT_X = 25.8
INA_PRODUCT_Y = 20.4  # page says 20.2; 20.4 covers the 20.32 PCB
INA_PRODUCT_Z = 10.1

# ISO 273 medium clearance holes. ISO 4032 hex nut, across flats and thickness.
M2_CLEAR = 2.4
M3_CLEAR = 3.4
M2_NUT_AF = 4.0
M2_NUT_T = 1.6

# ---------------------------------------------------------------------------
# UNVERIFIED parameters. Not from a datasheet. Change these; do not treat
# the defaults as measured parts.
# ---------------------------------------------------------------------------

# How far the lid standoff holds the LCD PCB back from the lid inner face.
# Default is the WH2004A maximum module thickness, which is right if the PCB
# is the back face of that stack. The contour drawing also shows 9.0 mm and
# 1.6 mm (LED backlight).
LCD_STANDOFF = 13.6  # UNVERIFIED interpretation of which face 13.6 MAX is

# PCF8574 backpack depth behind the LCD PCB. Not in the Winstar drawing.
# This number sets the pod depth. Shorten it if the real backpack is thinner.
LCD_BACKPACK_DEPTH = 16.0  # UNVERIFIED

# USB-I2C adapter envelope. No adapter is selected. The board is the alternate
# bus and is mounted in the pod; the three cable slots do not include USB.
ADAPTER_L, ADAPTER_W, ADAPTER_H = 54.0, 22.0, 14.0  # UNVERIFIED

# Jacket diameters for the three wall slots. Not a chosen cable.
# The UART slot carries six conductors (3.3 V, GND, SDA, SCL, TX, RX).
# Each shunt slot carries a small pair.
UART_CABLE_OD = 6.0  # UNVERIFIED
SENSE_CABLE_OD = 4.0  # UNVERIFIED

# Straight length inside the pod before the conductor may bend.
BEND_CLEAR = 12.0  # UNVERIFIED

# M3 heat-set insert for the lid screws.
INSERT_HOLE_D = 4.0  # UNVERIFIED
INSERT_DEPTH = 6.0  # UNVERIFIED

# Rear mounting tabs. Floor thickness, sticking out of the east and west walls.
# Hole is ISO 273 medium M3. The tab length is how far the flange sticks out.
TAB_LEN = 14.0  # UNVERIFIED, robot-head bracket
TAB_W = 18.0  # UNVERIFIED
# Cable-tie hole in the north tie-down tab. Not a standard gland.
TIE_HOLE = 4.0  # UNVERIFIED

# ---------------------------------------------------------------------------
# Design choices
# ---------------------------------------------------------------------------

WALL = 2.5
FLOOR = 3.0
LID_T = 2.5
FIT = 0.25  # clearance per side
# Boss strip beside the LCD. Boss radius is 4.5, so the strip must be wider
# than the boss or the boss lands on the module.
SIDE_MARGIN = 11.0
SOUTH_MARGIN = 11.0
BOSS_R = 4.5
SKIRT_H = 4.0
SKIRT_T = 1.6
WINDOW_MARGIN = 1.0
INA_STANDOFF = 4.0
BOARD_GAP = 3.0  # air between the boards and the backpack
LID_SEAT_GAP = 0.05
SLOT_DEPTH = 8.0  # U-slot depth from the top of the north wall
TIE_DEPTH = 12.0  # north tab that the cable ties land on


def _r3(value: float) -> float:
    return round(value, 3)


def compute() -> dict:
    """Every placement the solids and the drawing share."""
    p: dict = {
        "wall": WALL,
        "floor": FLOOR,
        "lid_t": LID_T,
        "fit": FIT,
        "bend_clear": BEND_CLEAR,
    }

    board_top = max(INA_STANDOFF + INA_PRODUCT_Z, 2.0 + ADAPTER_H)
    internal_h = board_top + BOARD_GAP + LCD_BACKPACK_DEPTH + LCD_STANDOFF
    p["board_top"] = board_top
    p["internal_h"] = internal_h
    p["base_h"] = FLOOR + internal_h
    p["outer_z"] = p["base_h"] + LID_T

    inner_w = LCD_X + 2.0 * SIDE_MARGIN
    inner_d = SOUTH_MARGIN + LCD_Y + BEND_CLEAR
    outer_x = inner_w + 2.0 * WALL
    outer_y = inner_d + 2.0 * WALL
    p.update(
        {
            "outer_x": outer_x,
            "outer_y": outer_y,
            "inner_x0": WALL,
            "inner_y0": WALL,
            "inner_x1": outer_x - WALL,
            "inner_y1": outer_y - WALL,
        }
    )

    lcd_x = WALL + SIDE_MARGIN
    lcd_y = WALL + SOUTH_MARGIN
    p["lcd_x"] = lcd_x
    p["lcd_y"] = lcd_y
    p["window_x"] = lcd_x + (LCD_X - LCD_VIEW_X) / 2.0 + WINDOW_MARGIN
    p["window_y"] = lcd_y + (LCD_Y - LCD_VIEW_Y) / 2.0 + WINDOW_MARGIN
    p["window_w"] = LCD_VIEW_X - 2.0 * WINDOW_MARGIN
    p["window_h"] = LCD_VIEW_Y - 2.0 * WINDOW_MARGIN

    holes = []
    for ix in (0.0, 1.0):
        for iy in (0.0, 1.0):
            holes.append(
                (
                    lcd_x + LCD_HOLE_INSET + ix * LCD_HOLE_PITCH_X,
                    lcd_y + LCD_HOLE_INSET + iy * LCD_HOLE_PITCH_Y,
                )
            )
    p["lcd_holes"] = holes

    # INA228 and the adapter sit side by side on the floor, under the LCD,
    # south of the cable alley. Stacked in Z with the backpack above them.
    gap = 4.0
    pair = INA_PRODUCT_X + gap + ADAPTER_L
    if pair + 2.0 > LCD_X:
        raise SystemExit(f"INA228 plus adapter need {pair:.1f} mm under a {LCD_X:.1f} mm LCD")
    pair_x = lcd_x + (LCD_X - pair) / 2.0
    p["ina_x"] = pair_x
    p["ina_y"] = lcd_y + 2.0
    p["adapter_x"] = pair_x + INA_PRODUCT_X + gap
    p["adapter_y"] = lcd_y + 2.0

    # Three U-slots in the north wall. West to east.
    p["uart_slot_w"] = UART_CABLE_OD + 2.0 * FIT
    p["sense_slot_w"] = SENSE_CABLE_OD + 2.0 * FIT
    slots = [
        ("shunt_battery", p["sense_slot_w"], "IN+ and VBUS"),
        ("shunt_bus", p["sense_slot_w"], "IN-"),
        ("uart_multicore", p["uart_slot_w"], "3.3V GND SDA SCL TX RX"),
    ]
    span = sum(s[1] for s in slots)
    margin = 16.0
    usable = outer_x - 2.0 * margin - span
    if usable < 8.0:
        raise SystemExit("north wall is too short for the three cable slots")
    gap_s = usable / (len(slots) - 1)
    x = margin
    placed = []
    for name, width, carries in slots:
        placed.append({"name": name, "x": x, "w": width, "carries": carries})
        x += width + gap_s
    p["slots"] = placed

    # North boss sits in the gap between the first two slots, not under a cable.
    gap_left = placed[0]["x"] + placed[0]["w"]
    gap_right = placed[1]["x"]
    north_x = (gap_left + gap_right) / 2.0
    bosses = [
        ("south", outer_x / 2.0, WALL + BOSS_R + 1.0),
        ("north", north_x, p["inner_y1"] - BOSS_R - 1.0),
        ("west", WALL + BOSS_R + 1.0, lcd_y + LCD_Y / 2.0),
        ("east", p["inner_x1"] - BOSS_R - 1.0, lcd_y + LCD_Y / 2.0),
    ]
    p["bosses"] = bosses

    _assert_clear(p)
    return p


def _hits(x: float, y: float, r: float, rx: float, ry: float, rw: float, rh: float) -> bool:
    cx = min(max(x, rx), rx + rw)
    cy = min(max(y, ry), ry + rh)
    return math.hypot(x - cx, y - cy) < r


def _assert_clear(p: dict) -> None:
    lcd = (p["lcd_x"] - 0.4, p["lcd_y"] - 0.4, LCD_X + 0.8, LCD_Y + 0.8)
    for name, x, y in p["bosses"]:
        if _hits(x, y, BOSS_R + 0.4, *lcd):
            raise SystemExit(f"boss {name} hits the LCD at ({x:.1f}, {y:.1f})")
        for hx, hy in p["lcd_holes"]:
            if math.hypot(x - hx, y - hy) < BOSS_R + 4.0:
                raise SystemExit(f"boss {name} is too close to an LCD hole")
        if not (p["inner_x0"] + BOSS_R < x < p["inner_x1"] - BOSS_R):
            raise SystemExit(f"boss {name} is outside the cavity in X")
        if not (p["inner_y0"] + BOSS_R < y < p["inner_y1"] - BOSS_R):
            raise SystemExit(f"boss {name} is outside the cavity in Y")
    # The north boss must not sit under a cable slot.
    _bn, nx, ny = p["bosses"][1]
    for slot in p["slots"]:
        if slot["x"] - 2.0 < nx < slot["x"] + slot["w"] + 2.0:
            raise SystemExit(f"north boss is under slot {slot['name']}")
        if abs(ny - p["inner_y1"]) + BOSS_R > BEND_CLEAR and slot["x"] < nx < slot["x"] + slot["w"]:
            raise SystemExit(f"north boss blocks the alley at {slot['name']}")


def _box(x: float, y: float, z: float, lx: float, ly: float, lz: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(lx, ly, lz, centered=(False, False, False))
        .translate((x, y, z))
    )


def _cyl(x: float, y: float, z: float, r: float, h: float) -> cq.Workplane:
    return cq.Workplane("XY").center(x, y).workplane(offset=z).circle(r).extrude(h)


def _hex(x: float, y: float, z: float, across_flats: float, h: float) -> cq.Workplane:
    circum = across_flats / math.cos(math.radians(30.0))
    return (
        cq.Workplane("XY")
        .center(x, y)
        .workplane(offset=z)
        .polygon(6, circum)
        .extrude(h)
    )


def _fuse(parts: list[cq.Workplane]) -> cq.Workplane:
    acc = parts[0]
    for part in parts[1:]:
        acc = acc.union(part)
    return acc


def _cut_all(solid: cq.Workplane, cutters: list[cq.Workplane]) -> cq.Workplane:
    acc = solid
    for cutter in cutters:
        acc = acc.cut(cutter)
    return acc


def _uslot(x: float, width: float, y0: float, length: float, base_h: float) -> cq.Workplane:
    """Notch open at the top of the wall, round at the bottom, along +Y."""
    radius = width / 2.0
    z_round = base_h - SLOT_DEPTH
    rect = _box(x, y0, z_round, width, length, SLOT_DEPTH + 1.0)
    # The cylinder is centered on the bottom of the notch so the seat is round.
    seat = (
        cq.Workplane("XZ")
        .center(x + radius, z_round)
        .circle(radius)
        .extrude(-length)
        .translate((0, y0, 0))
    )
    return rect.union(seat)


def build_base(p: dict) -> cq.Workplane:
    ox, oy, bh = p["outer_x"], p["outer_y"], p["base_h"]
    shell = _box(0, 0, 0, ox, oy, bh)
    cavity = _box(
        p["inner_x0"],
        p["inner_y0"],
        FLOOR,
        p["inner_x1"] - p["inner_x0"],
        p["inner_y1"] - p["inner_y0"],
        bh - FLOOR + 1.0,
    )
    solid = shell.cut(cavity)

    features: list[cq.Workplane] = []

    # Rear mounting flanges. They are the floor, extended east and west,
    # so the pod bolts flat to a plate on the robot head. The LCD faces out.
    tab_y = (oy - TAB_W) / 2.0
    features.append(_box(-TAB_LEN, tab_y, 0, TAB_LEN + 0.4, TAB_W, FLOOR))
    features.append(_box(ox - 0.4, tab_y, 0, TAB_LEN + 0.4, TAB_W, FLOOR))

    # North tie-down tab, in the floor plane, outside the cable wall.
    features.append(_box(0, oy - 0.4, 0, ox, TIE_DEPTH + 0.4, FLOOR))

    for _name, x, y in p["bosses"]:
        features.append(_cyl(x, y, FLOOR - 0.2, BOSS_R, bh - FLOOR + 0.2))

    for hx, hy in INA_HOLES:
        features.append(
            _cyl(p["ina_x"] + hx, p["ina_y"] + hy, FLOOR - 0.2, 3.0, INA_STANDOFF + 0.2)
        )

    # Adapter cleats. Its holes are unknown, so rails locate the envelope.
    ax, ay = p["adapter_x"], p["adapter_y"]
    cleat_h = 3.2
    features.append(
        _box(ax - FIT - 1.6, ay - FIT - 1.6, FLOOR - 0.2, ADAPTER_L + 2 * FIT + 3.2, 1.6, cleat_h)
    )
    features.append(
        _box(ax - FIT - 1.6, ay + ADAPTER_W + FIT, FLOOR - 0.2, ADAPTER_L + 2 * FIT + 3.2, 1.6, cleat_h)
    )
    features.append(_box(ax - FIT - 1.6, ay - FIT, FLOOR - 0.2, 1.6, ADAPTER_W + 2 * FIT, cleat_h))

    solid = solid.union(_fuse(features))

    cutters: list[cq.Workplane] = []
    for _name, x, y in p["bosses"]:
        cutters.append(_cyl(x, y, bh - INSERT_DEPTH, INSERT_HOLE_D / 2.0, INSERT_DEPTH + 1.0))

    nut_af = M2_NUT_AF + 2.0 * FIT
    for hx, hy in INA_HOLES:
        x = p["ina_x"] + hx
        y = p["ina_y"] + hy
        cutters.append(_cyl(x, y, -0.5, M2_CLEAR / 2.0, INA_STANDOFF + FLOOR + 1.0))
        cutters.append(_hex(x, y, -0.2, nut_af, M2_NUT_T + 0.4))

    # M3 holes in the side flanges. Centered in the tab, in from the tip.
    hole_r = M3_CLEAR / 2.0
    for sign, x_body in ((-1.0, 0.0), (1.0, ox)):
        hx = x_body + sign * (TAB_LEN - 7.0)
        cutters.append(_cyl(hx, oy / 2.0, -0.5, hole_r, FLOOR + 1.0))

    # Cable-tie holes, one in front of each slot.
    for slot in p["slots"]:
        cutters.append(
            _cyl(slot["x"] + slot["w"] / 2.0, oy + TIE_DEPTH / 2.0, -0.5, TIE_HOLE / 2.0, FLOOR + 1.0)
        )

    # U-slots. Open at the top so they print without support. The lid closes them.
    for slot in p["slots"]:
        cutters.append(_uslot(slot["x"], slot["w"], oy - WALL - 1.0, WALL + 2.0, bh))

    # Two short vents in each long wall. Vertical slots, no overhang.
    for x0 in (-1.0, ox - WALL - 1.0):
        for y in (p["lcd_y"] + 6.0, p["lcd_y"] + LCD_Y - 18.0):
            cutters.append(_box(x0, y, FLOOR + 18.0, WALL + 2.0, 3.0, 12.0))

    return _cut_all(solid, cutters)


def build_lid(p: dict) -> cq.Workplane:
    """Lid in assembly orientation, sitting on the base."""
    ox, oy = p["outer_x"], p["outer_y"]
    z_plate = p["base_h"] + LID_SEAT_GAP
    plate = _box(0, 0, z_plate, ox, oy, LID_T)
    features: list[cq.Workplane] = []

    x0 = p["inner_x0"] + FIT
    y0 = p["inner_y0"] + FIT
    x1 = p["inner_x1"] - FIT
    y1 = p["inner_y1"] - FIT
    skirt_z = z_plate - SKIRT_H
    # South, west, east run the full side. North is broken around the slots.
    features.append(_box(x0 + 8.0, y0, skirt_z, (x1 - x0) - 16.0, SKIRT_T, SKIRT_H + 0.2))
    features.append(_box(x0, y0 + 8.0, skirt_z, SKIRT_T, (y1 - y0) - 16.0, SKIRT_H + 0.2))
    features.append(_box(x1 - SKIRT_T, y0 + 8.0, skirt_z, SKIRT_T, (y1 - y0) - 16.0, SKIRT_H + 0.2))

    # North skirt segments between the cable slots.
    edges = [x0] + [s["x"] for s in p["slots"]] + [s["x"] + s["w"] for s in p["slots"]] + [x1]
    # Build intervals that are not inside a slot.
    blocked = [(s["x"] - 1.0, s["x"] + s["w"] + 1.0) for s in p["slots"]]
    cursor = x0
    north_bits = []
    while cursor < x1 - 1.0:
        hit = None
        for a, b in blocked:
            if a <= cursor < b:
                hit = b
                break
        if hit is not None:
            cursor = hit
            continue
        nxt = x1
        for a, _b in blocked:
            if cursor < a < nxt:
                nxt = a
        if nxt - cursor > 3.0:
            north_bits.append((cursor, nxt - cursor))
        cursor = nxt
    for sx, sw in north_bits:
        features.append(_box(sx, y1 - SKIRT_T, skirt_z, sw, SKIRT_T, SKIRT_H + 0.2))

    for hx, hy in p["lcd_holes"]:
        features.append(_cyl(hx, hy, z_plate - LCD_STANDOFF, 3.5, LCD_STANDOFF + 0.2))

    solid = plate.union(_fuse(features))

    cutters: list[cq.Workplane] = []
    cutters.append(
        _box(
            p["window_x"],
            p["window_y"],
            z_plate - 0.5,
            p["window_w"],
            p["window_h"],
            LID_T + 1.0,
        )
    )
    for _name, x, y in p["bosses"]:
        cutters.append(_cyl(x, y, z_plate - 0.5, M3_CLEAR / 2.0, LID_T + 1.0))
        cutters.append(_cyl(x, y, skirt_z - 0.5, BOSS_R + 1.5, SKIRT_H + 2.0))

    nut_af = M2_NUT_AF + 2.0 * FIT
    for hx, hy in p["lcd_holes"]:
        cutters.append(
            _cyl(hx, hy, z_plate - LCD_STANDOFF - 0.5, M2_CLEAR / 2.0, LCD_STANDOFF + LID_T + 1.0)
        )
        cutters.append(_hex(hx, hy, z_plate - LCD_STANDOFF - 0.2, nut_af, M2_NUT_T + 0.6))

    return _cut_all(solid, cutters)


def lid_to_print(lid: cq.Workplane, p: dict) -> cq.Workplane:
    """Flip the lid so the outer face is on the bed and the skirt points up.

    Rotation about X mirrors Y. Flipping the printed part back onto the base
    undoes that mirror, so the window lands on the LCD.
    """
    rotated = lid.rotate((0, 0, 0), (1, 0, 0), 180)
    outer_face = p["base_h"] + LID_SEAT_GAP + LID_T
    return rotated.translate((0, p["outer_y"], outer_face))


def _envelope(x, y, z, lx, ly, lz) -> cq.Workplane:
    return _box(x, y, z, lx, ly, lz)


def reference_solids(p: dict) -> list[tuple[str, cq.Workplane]]:
    pcb_z = p["base_h"] + LID_SEAT_GAP - LCD_STANDOFF
    solids = [
        (
            "REF_lcd_module",
            _envelope(p["lcd_x"], p["lcd_y"], pcb_z, LCD_X, LCD_Y, LCD_STANDOFF),
        ),
        (
            "REF_lcd_backpack_UNVERIFIED",
            _envelope(
                p["lcd_x"] + 20.0,
                p["lcd_y"] + 14.0,
                pcb_z - LCD_BACKPACK_DEPTH,
                LCD_X - 40.0,
                LCD_Y - 28.0,
                LCD_BACKPACK_DEPTH,
            ),
        ),
        (
            "REF_ina228",
            _envelope(
                p["ina_x"],
                p["ina_y"],
                FLOOR + INA_STANDOFF,
                INA_PRODUCT_X,
                INA_PRODUCT_Y,
                INA_PRODUCT_Z,
            ),
        ),
        (
            "REF_usb_i2c_adapter_UNVERIFIED",
            _envelope(p["adapter_x"], p["adapter_y"], FLOOR + 2.0, ADAPTER_L, ADAPTER_W, ADAPTER_H),
        ),
    ]
    return solids


def _shape(workplane: cq.Workplane):
    return workplane.val()


def _require_single_valid_solid(workplane: cq.Workplane, label: str) -> None:
    shape = _shape(workplane)
    if not shape.isValid():
        raise SystemExit(f"{label} is not a valid solid")
    solids = shape.Solids()
    if len(solids) != 1:
        raise SystemExit(f"{label} has {len(solids)} solids, expected 1")
    volume = shape.Volume()
    if volume < 1000.0:
        raise SystemExit(f"{label} volume {volume:.1f} mm^3 is implausibly small")


def _interference(a: cq.Workplane, b: cq.Workplane) -> float:
    common = a.intersect(b)
    return float(common.val().Volume())


def _mesh_report(path: Path) -> dict:
    mesh = trimesh.load(path, force="mesh")
    if not isinstance(mesh, trimesh.Trimesh):
        raise SystemExit(f"{path.name} did not load as a single mesh")
    return {
        "file": path.name,
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "volume_mm3": _r3(float(mesh.volume)),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "extents_mm": [_r3(float(v)) for v in mesh.extents],
    }


def _export_solid(solid: cq.Workplane, stem: Path) -> None:
    cq.exporters.export(solid, str(stem.with_suffix(".step")))
    cq.exporters.export(solid, str(stem.with_suffix(".stl")), tolerance=0.08, angularTolerance=0.12)


def _decimate(mesh: trimesh.Trimesh, limit: int) -> np.ndarray:
    faces = mesh.triangles
    if len(faces) > limit:
        idx = np.linspace(0, len(faces) - 1, limit).astype(int)
        faces = faces[idx]
    return faces


def _shade(faces: np.ndarray, color: tuple[float, float, float], alpha: float) -> np.ndarray:
    normals = np.cross(faces[:, 1] - faces[:, 0], faces[:, 2] - faces[:, 0])
    scale = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = normals / np.clip(scale, 1e-9, None)
    light = np.array([0.25, 0.35, 0.90])
    light = light / np.linalg.norm(light)
    shade = np.clip(normals @ light, 0.30, 1.0)
    rgb = np.array(color) * shade[:, None]
    return np.concatenate([rgb, np.full((len(rgb), 1), alpha)], axis=1)


def _paint_sorted(ax, layers: list[tuple[np.ndarray, tuple[float, float, float], float]]) -> None:
    elev, azim = 24.0, -58.0
    az = math.radians(azim)
    el = math.radians(elev)
    camera = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    chunks_f = []
    chunks_c = []
    for faces, color, alpha in layers:
        if len(faces) == 0:
            continue
        chunks_f.append(faces)
        chunks_c.append(_shade(faces, color, alpha))
    faces = np.concatenate(chunks_f, axis=0)
    colors = np.concatenate(chunks_c, axis=0)
    depth = faces.mean(axis=1) @ camera
    order = np.argsort(depth)
    coll = Poly3DCollection(faces[order], facecolors=colors[order], edgecolors="none", linewidths=0)
    ax.add_collection3d(coll)


def render_preview(p: dict, meshes: dict[str, trimesh.Trimesh], path: Path) -> None:
    fig = plt.figure(figsize=(12.8, 6.4), dpi=130)
    titles = ("Interior", "Lid lifted")
    lifts = (0.0, 40.0)
    show_lid = (False, True)
    x0 = -TAB_LEN
    x1 = p["outer_x"] + TAB_LEN
    y1 = p["outer_y"] + TIE_DEPTH
    for panel, (title, lift, draw_lid) in enumerate(zip(titles, lifts, show_lid), start=1):
        ax = fig.add_subplot(1, 2, panel, projection="3d")
        layers: list[tuple[np.ndarray, tuple[float, float, float], float]] = []
        layers.append((_decimate(meshes["base"], 12000), (0.62, 0.66, 0.70), 0.30))
        if draw_lid:
            lid_faces = _decimate(meshes["lid_asm"], 8000).copy()
            lid_faces[:, :, 2] += lift
            layers.append((lid_faces, (0.16, 0.40, 0.56), 0.45))
        colors = {
            "ina": (0.80, 0.38, 0.12),
            "lcd": (0.20, 0.38, 0.75),
            "backpack": (0.40, 0.28, 0.62),
            "adapter": (0.45, 0.48, 0.52),
        }
        for name, mesh in meshes["refs"]:
            if "ina" in name:
                color = colors["ina"]
            elif "backpack" in name:
                color = colors["backpack"]
            elif "lcd" in name:
                color = colors["lcd"]
            else:
                color = colors["adapter"]
            layers.append((_decimate(mesh, 2000), color, 0.95))
        _paint_sorted(ax, layers)
        ax.set_title(title, fontsize=11, pad=8)
        ax.set_box_aspect((x1 - x0, y1, max(p["outer_z"] + lift, 70)))
        ax.set_xlim(x0, x1)
        ax.set_ylim(0, y1)
        ax.set_zlim(0, p["outer_z"] + lift)
        ax.view_init(elev=32 if draw_lid else 38, azim=-62)
        ax.set_axis_off()
    fig.suptitle(
        "Display and sense pod  "
        f"{p['outer_x'] + 2 * TAB_LEN:.1f} x {p['outer_y'] + TIE_DEPTH:.1f} x {p['outer_z']:.1f} mm with flanges",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path)
    plt.close(fig)


def _public_dimensions(p: dict) -> dict:
    return {
        "units": "mm",
        "role": "display_and_sense_pod",
        "body_x": _r3(p["outer_x"]),
        "body_y": _r3(p["outer_y"]),
        "outer_x_with_flanges": _r3(p["outer_x"] + 2.0 * TAB_LEN),
        "outer_y_with_tie_tab": _r3(p["outer_y"] + TIE_DEPTH),
        "outer_z": _r3(p["outer_z"]),
        "base_h": _r3(p["base_h"]),
        "internal_x": _r3(p["inner_x1"] - p["inner_x0"]),
        "internal_y": _r3(p["inner_y1"] - p["inner_y0"]),
        "internal_z": _r3(p["internal_h"]),
        "wall": WALL,
        "floor": FLOOR,
        "lid_t": LID_T,
        "fit_per_side": FIT,
        "mounting": {
            "type": "rear floor flanges, one each side",
            "tab_length_mm": TAB_LEN,
            "tab_width_mm": TAB_W,
            "hole": "M3 clearance, ISO 273 medium, 3.4 mm",
            "hole_diameter_mm": M3_CLEAR,
        },
        "cables": [
            {
                "slot": s["name"],
                "slot_width_mm": _r3(s["w"]),
                "carries": s["carries"],
                "x_mm": _r3(s["x"]),
            }
            for s in p["slots"]
        ],
        "lcd_module": [LCD_X, LCD_Y, LCD_Z_MAX],
        "lcd_window": [_r3(p["window_w"]), _r3(p["window_h"])],
        "shunt": "outside, at the battery. No shunt power path in this pod.",
        "not_in_this_box": ["Jetson Nano", "buck", "F1", "F2", "shunt", "TMP117"],
        "unverified_parameters": {
            "lcd_standoff_mm": LCD_STANDOFF,
            "lcd_backpack_depth_mm": LCD_BACKPACK_DEPTH,
            "usb_i2c_adapter_envelope_mm": [ADAPTER_L, ADAPTER_W, ADAPTER_H],
            "uart_cable_od_mm": UART_CABLE_OD,
            "sense_cable_od_mm": SENSE_CABLE_OD,
            "bend_clearance_mm": BEND_CLEAR,
            "insert_hole_diameter_mm": INSERT_HOLE_D,
            "insert_depth_mm": INSERT_DEPTH,
            "mount_tab_length_mm": TAB_LEN,
            "mount_tab_width_mm": TAB_W,
            "tie_hole_mm": TIE_HOLE,
        },
    }


def main() -> int:
    EXPORT.mkdir(parents=True, exist_ok=True)
    p = compute()
    print(
        f"body {p['outer_x']:.2f} x {p['outer_y']:.2f} x {p['outer_z']:.2f} mm, "
        f"with flanges {p['outer_x'] + 2 * TAB_LEN:.2f} x {p['outer_y'] + TIE_DEPTH:.2f}, "
        f"internal {p['inner_x1'] - p['inner_x0']:.2f} x "
        f"{p['inner_y1'] - p['inner_y0']:.2f} x {p['internal_h']:.2f} mm"
    )

    print("building base")
    base = build_base(p)
    _require_single_valid_solid(base, "base")
    print("building lid")
    lid_asm = build_lid(p)
    _require_single_valid_solid(lid_asm, "lid")
    lid_print = lid_to_print(lid_asm, p)

    overlap = _interference(base, lid_asm)
    print(f"base/lid intersection volume {overlap:.3f} mm^3")
    if overlap > 5.0:
        raise SystemExit("base and lid intersect")

    bb = lid_asm.val().BoundingBox()
    if abs(bb.xmin) > 0.5 or abs(bb.ymin) > 0.5:
        raise SystemExit(f"lid assembly XY origin is off: {bb.xmin:.2f}, {bb.ymin:.2f}")
    expected_top = p["base_h"] + LID_SEAT_GAP + LID_T
    if abs(bb.zmax - expected_top) > 0.2:
        raise SystemExit(f"lid top is {bb.zmax:.2f}, expected {expected_top:.2f}")

    print("exporting")
    _export_solid(base, EXPORT / "base")
    _export_solid(lid_print, EXPORT / "lid")

    assembly = cq.Assembly(name="display_sense_pod")
    assembly.add(base, name="base", color=cq.Color(0.62, 0.66, 0.70, 1))
    assembly.add(lid_asm, name="lid", color=cq.Color(0.18, 0.42, 0.58, 1))
    ref_meshes = []
    for name, solid in reference_solids(p):
        assembly.add(solid, name=name, color=cq.Color(0.4, 0.6, 0.4, 0.4))
        ref_path = EXPORT / f"_{name}.stl"
        cq.exporters.export(solid, str(ref_path), tolerance=0.2, angularTolerance=0.3)
        ref_meshes.append((name, trimesh.load(ref_path, force="mesh")))
        ref_path.unlink()
    assembly.export(str(EXPORT / "assembly.step"), "STEP")

    for stem in ("base", "lid", "assembly"):
        reopened = cq.importers.importStep(str(EXPORT / f"{stem}.step"))
        if reopened.val().Volume() <= 0:
            raise SystemExit(f"{stem}.step reopened with no volume")

    reports = []
    for stem in ("base", "lid"):
        report = _mesh_report(EXPORT / f"{stem}.stl")
        reports.append(report)
        print(stem, report)
        if not report["watertight"]:
            raise SystemExit(f"{stem}.stl is not watertight")
        if not report["winding_consistent"]:
            raise SystemExit(f"{stem}.stl winding is inconsistent")

    dims = _public_dimensions(p)
    (EXPORT / "dimensions.json").write_text(json.dumps(dims, indent=2) + "\n")
    (EXPORT / "manifold.txt").write_text(
        "\n".join(
            f"{r['file']}: watertight={r['watertight']} winding={r['winding_consistent']} "
            f"volume_mm3={r['volume_mm3']} faces={r['faces']}"
            for r in reports
        )
        + "\n"
    )

    asm_stl = EXPORT / "_lid_assembly.stl"
    cq.exporters.export(lid_asm, str(asm_stl), tolerance=0.15, angularTolerance=0.2)
    meshes = {
        "base": trimesh.load(EXPORT / "base.stl", force="mesh"),
        "lid_asm": trimesh.load(asm_stl, force="mesh"),
        "refs": ref_meshes,
    }
    asm_stl.unlink()
    render_preview(p, meshes, HERE / "preview.png")
    print(f"wrote {HERE / 'preview.png'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
