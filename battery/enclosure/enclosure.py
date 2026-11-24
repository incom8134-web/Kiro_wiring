#!/usr/bin/env python3
"""Parametric enclosure for the Jetson Nano battery monitor.

Run from this directory:

    python3 enclosure.py

Writes STEP and STL for the base and the lid, an assembly STEP, a preview
PNG, and export/dimensions.json. Dimensions are millimetres.

Printed parts are the base and the lid only. The assembly STEP also contains
reference envelopes (names start with REF_) so the layout is visible. Those
envelopes are not for printing.

Verified numbers are cited next to the constant. Anything that is not from a
drawing or a datasheet is marked UNVERIFIED and is a parameter on purpose.
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

# NVIDIA Jetson Nano Developer Kit datasheet, January 2020 (Mouser reprint of
# the NVIDIA data sheet). Mechanical: 100 mm x 80 mm x 29 mm.
# Kit contents in that sheet: "NVIDIA Jetson Nano Module with Heatsink and
# Reference Carrier Board". The 29 mm figure is the published kit envelope,
# so the cavity clears the heatsink that ships with the kit.
# https://www.mouser.com/datasheet/2/813/jetson_nano_devkit_datasheet_updates_us_v3-2487380.pdf
# Mounting-hole coordinates are NOT in that sheet. NVIDIA staff have said the
# carrier specification omits them; they live in the P3449 design files and
# the P3450 STEP, which require an NVIDIA login. They are not invented here.
JETSON_X = 100.0
JETSON_Y = 80.0
JETSON_Z = 29.0

# Module only (not the carrier). NVIDIA module datasheet DA-09366 and the
# current Jetson Nano specifications page: 69.6 mm x 45 mm. Not used to size
# the pocket. The pocket follows the developer-kit envelope above.
JETSON_MODULE_X = 69.6
JETSON_MODULE_Y = 45.0

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
# Assembled product size from the Adafruit product page: 25.8 x 20.2 x 10.1 mm
# (the extra length over the PCB is the terminal block).
# https://www.adafruit.com/product/5832
INA_PCB_X = 25.4
INA_PCB_Y = 20.32
INA_HOLES = ((2.54, 17.78), (22.86, 17.78))
INA_HOLE_D = 2.5
INA_PRODUCT_X = 25.8
INA_PRODUCT_Y = 20.4  # page says 20.2; 20.4 covers the 20.32 PCB
INA_PRODUCT_Z = 10.1

# LAPP SKINTOP / cable-gland catalogue T21. Panel hole D3:
#   PG7  12.8 mm (tolerance -0.2), thread OD 12.5 mm
#   PG9  15.5 mm (tolerance -0.2), thread OD 15.2 mm
# SKINTOP ST body (same catalogue family): PG7 wrench 15 mm, thread length
# 7.8 mm, overall length 32 mm. PG9 wrench 19 mm, thread length 8 mm,
# overall length 36 mm.
# https://e-catalog.lappgroup.com/ (SKINTOP ST and catalogue sheet T21)
PG7_HOLE = 12.8
PG9_HOLE = 15.5
PG7_WRENCH = 15.0
PG9_WRENCH = 19.0
PG7_OVERALL = 32.0
PG9_OVERALL = 36.0

# ISO 273 medium clearance holes. ISO 4032 hex nut, across flats and thickness.
M2_CLEAR = 2.4
M3_CLEAR = 3.4
M2_NUT_AF = 4.0
M2_NUT_T = 1.6
M3_NUT_AF = 5.5
M3_NUT_T = 2.4

# ---------------------------------------------------------------------------
# UNVERIFIED parameters. Not from a datasheet. Change these; do not treat
# the defaults as measured parts.
# ---------------------------------------------------------------------------

# How far the lid standoff holds the LCD PCB back from the lid inner face.
# Default is the WH2004A maximum module thickness, which is right if the PCB
# is the back face of that stack. The contour drawing also shows 9.0 mm and
# 1.6 mm (LED backlight). If the bezel hits the lid before the PCB meets the
# standoff, shorten this.
LCD_STANDOFF = 13.6  # UNVERIFIED interpretation of which face 13.6 MAX is

# PCF8574 backpack depth behind the LCD PCB. Not in the Winstar drawing.
LCD_BACKPACK_DEPTH = 16.0  # UNVERIFIED

# Envelopes for parts that are not selected yet (pack current and voltage
# are unknown, so the buck, the fuse holder, and the terminal blocks have
# no catalog part). The box grows to fit these boxes.
BUCK_L, BUCK_W, BUCK_H = 66.0, 36.0, 20.0  # UNVERIFIED
FUSE_L, FUSE_W, FUSE_H = 48.0, 22.0, 28.0  # UNVERIFIED
TB_L, TB_W, TB_H = 42.0, 18.0, 22.0  # UNVERIFIED, one 3-position block
ADAPTER_L, ADAPTER_W, ADAPTER_H = 54.0, 22.0, 14.0  # UNVERIFIED USB-I2C dongle

# Straight cable length kept inside each gland before the conductor may bend.
# Real bend radius depends on the cable, which is not chosen yet.
BEND_CLEAR = 18.0  # UNVERIFIED

# M3 heat-set insert. Hole diameter and depth must match the insert you buy.
# No insert datasheet is cited. 4.0 mm x 6.0 mm is a common starting hole
# for a short M3 brass insert and it will be wrong for some inserts.
INSERT_HOLE_D = 4.0  # UNVERIFIED
INSERT_DEPTH = 6.0  # UNVERIFIED

# Jetson carrier mounting holes. Empty means the kit is retained by the
# outline cradle, not by screws. Fill with (x, y) pairs in millimetres,
# origin at the kit corner that sits at the south-west of the pocket, +X
# along the 100 mm edge, +Y along the 80 mm edge, only after you measure
# the P3449 board or the P3450 STEP.
JETSON_HOLE_XY: tuple[tuple[float, float], ...] = ()  # UNVERIFIED, intentionally empty
JETSON_HOLE_D = 2.7  # UNVERIFIED, unused while JETSON_HOLE_XY is empty

# ---------------------------------------------------------------------------
# Design choices (print practice, not part dimensions)
# ---------------------------------------------------------------------------

WALL = 2.5
FLOOR = 3.0
LID_T = 2.5
FIT = 0.25  # clearance per side for boards, skirt, and cradle ribs
PRINT_HOLE_ALLOW = 0.20  # extra radius on gland holes so a printed hole matches D3
SHELF_H = 8.0  # air under the carrier; not a datasheet stack height
VENT_GAP = 8.0
BOSS_R = 4.5
SKIRT_H = 5.0
SKIRT_T = 1.6
WINDOW_MARGIN = 1.0  # lid window is this much inside the view area, per side
INA_STANDOFF = 4.0
CHANNEL = 8.0  # UART / I2C wire channel between the kit and the power bay


def _r3(value: float) -> float:
    return round(value, 3)


def compute() -> dict:
    """Every placement the solids, the drawing, and the README share."""
    p: dict = {}
    p["wall"] = WALL
    p["floor"] = FLOOR
    p["lid_t"] = LID_T
    p["fit"] = FIT
    p["shelf_h"] = SHELF_H
    p["bend_clear"] = BEND_CLEAR

    # LCD hang from the inner face of the lid, including the unverified backpack.
    lcd_hang = LCD_STANDOFF + LCD_BACKPACK_DEPTH
    ina_top = INA_STANDOFF + INA_PRODUCT_Z
    adapter_top = 2.0 + ADAPTER_H
    under_lcd = max(ina_top, adapter_top) + 4.0
    h_lcd = under_lcd + lcd_hang
    h_jetson = SHELF_H + JETSON_Z + VENT_GAP
    h_power = max(BUCK_H, FUSE_H, TB_H) + 4.0
    internal_h = max(h_lcd, h_jetson, h_power)
    p["internal_h"] = internal_h
    p["lcd_hang"] = lcd_hang
    p["base_h"] = FLOOR + internal_h
    p["outer_z"] = p["base_h"] + LID_T

    # Footprint. Origin is the outside south-west corner of the base.
    board_x = WALL + FIT
    board_y = WALL + FIT
    bay_x0 = board_x + JETSON_X + FIT + 4.0
    bay_w = LCD_X + 2.0 * (3.5 - LCD_HOLE_INSET + 0.4)
    bay_x1 = bay_x0 + bay_w
    outer_x = bay_x1 + 0.6 + WALL

    tall_y0 = board_y + JETSON_Y + FIT + CHANNEL
    # Power bay, from south to north: buck/fuse row, gap, terminal row, bend.
    power_depth = max(BUCK_W, FUSE_W) + 4.0 + TB_W + BEND_CLEAR
    tall_y1 = tall_y0 + power_depth
    outer_y = tall_y1 + 0.6 + WALL

    p.update(
        {
            "board_x": board_x,
            "board_y": board_y,
            "bay_x0": bay_x0,
            "bay_x1": bay_x1,
            "bay_w": bay_w,
            "tall_y0": tall_y0,
            "tall_y1": tall_y1,
            "outer_x": outer_x,
            "outer_y": outer_y,
            "inner_x0": WALL,
            "inner_y0": WALL,
            "inner_x1": outer_x - WALL,
            "inner_y1": outer_y - WALL,
        }
    )

    # LCD sits in the bay. Shifted north of center so the south-wall screw
    # boss clears the southern mounting holes.
    lcd_x = bay_x0 + (bay_w - LCD_X) / 2.0
    lcd_y = board_y + (JETSON_Y - LCD_Y) / 2.0 + 4.0
    if lcd_y + LCD_Y > board_y + JETSON_Y - 1.0:
        raise SystemExit("LCD does not fit in the jetson-depth bay")
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

    # INA228 and the USB-I2C adapter sit on the floor under the LCD.
    # The backpack hangs above them.
    gap = 4.0
    pair = INA_PRODUCT_X + gap + ADAPTER_L
    pair_x = lcd_x + (LCD_X - pair) / 2.0
    ina_y = lcd_y + (LCD_Y - INA_PRODUCT_Y) / 2.0
    ad_y = lcd_y + (LCD_Y - ADAPTER_W) / 2.0
    p["ina_x"] = pair_x
    p["ina_y"] = ina_y
    p["adapter_x"] = pair_x + INA_PRODUCT_X + gap
    p["adapter_y"] = ad_y

    # Power parts. Two rows. Keep 16 mm clear of the inner east and west
    # walls so the corner screw bosses have room.
    keep = 16.0
    row_x0 = p["inner_x0"] + keep
    row_x1 = p["inner_x1"] - keep
    row_w = row_x1 - row_x0
    need = BUCK_L + 4.0 + FUSE_L
    if need > row_w:
        raise SystemExit(f"buck + fuse need {need:.1f} mm, row is {row_w:.1f} mm")
    spare = row_w - need
    buck_x = row_x0 + spare / 2.0
    fuse_x = buck_x + BUCK_L + 4.0
    # Buck/fuse row is the southern row of the power bay.
    power_y0 = tall_y0
    buck_y = power_y0
    fuse_y = power_y0 + (BUCK_W - FUSE_W) / 2.0
    tb_y = power_y0 + max(BUCK_W, FUSE_W) + 4.0
    tb_need = TB_L + 6.0 + TB_L
    if tb_need > row_w:
        raise SystemExit(f"terminal blocks need {tb_need:.1f} mm, row is {row_w:.1f} mm")
    tb_spare = row_w - tb_need
    tb1_x = row_x0 + tb_spare / 2.0
    tb2_x = tb1_x + TB_L + 6.0
    p.update(
        {
            "buck": (buck_x, buck_y, BUCK_L, BUCK_W, BUCK_H),
            "fuse": (fuse_x, fuse_y, FUSE_L, FUSE_W, FUSE_H),
            "tb_shunt": (tb1_x, tb_y, TB_L, TB_W, TB_H),
            "tb_load": (tb2_x, tb_y, TB_L, TB_W, TB_H),
        }
    )

    # Glands along the north wall. Five PG9 power glands, three PG7 signal glands.
    # Printed diameter is the catalogue maximum plus 0.2 mm per side.
    p["pg7_printed"] = PG7_HOLE + 2.0 * PRINT_HOLE_ALLOW
    p["pg9_printed"] = PG9_HOLE + 2.0 * PRINT_HOLE_ALLOW
    glands = [
        ("battery_in", "PG9"),
        ("shunt_battery_side", "PG9"),
        ("shunt_bus_side", "PG9"),
        ("load", "PG9"),
        ("charger", "PG9"),
        ("kelvin_vbus", "PG7"),
        ("usb", "PG7"),
        ("uart", "PG7"),
    ]
    pitch = {"PG9": 26.0, "PG7": 22.0}
    span = 0.0
    for i, (_, kind) in enumerate(glands):
        if i:
            span += pitch[kind]
    # End margins have to clear the north-wall screw bosses as well as the
    # gland nuts. Boss center is BOSS_R+1 mm in from the inner wall.
    boss_keep = (BOSS_R + 1.0) + BOSS_R + (p["pg9_printed"] / 2.0) + 1.5
    margin = (p["inner_x1"] - p["inner_x0"] - span) / 2.0
    if margin < boss_keep:
        # Widen the east wall so the end glands clear the corner bosses.
        grow = 2.0 * (boss_keep - margin)
        p["outer_x"] += grow
        p["inner_x1"] += grow
        margin = boss_keep
    x = p["inner_x0"] + margin
    placed = []
    zc = FLOOR + 16.0
    for i, (name, kind) in enumerate(glands):
        if i:
            x += pitch[kind]
        dia = p["pg9_printed"] if kind == "PG9" else p["pg7_printed"]
        placed.append(
            {
                "name": name,
                "kind": kind,
                "x": x,
                "z": zc,
                "diameter": dia,
                "datasheet_hole": PG9_HOLE if kind == "PG9" else PG7_HOLE,
                "wrench": PG9_WRENCH if kind == "PG9" else PG7_WRENCH,
            }
        )
    p["glands"] = placed

    # Screw bosses on solid wall. The south-west corner is the port opening,
    # so that corner is located by the lid skirt rather than a sixth screw.
    bosses = [
        ("west_power", p["inner_x0"] + BOSS_R + 1.0, tall_y0 + 10.0),
        ("north_west", p["inner_x0"] + BOSS_R + 1.0, p["inner_y1"] - BOSS_R - 1.0),
        ("north_east", p["inner_x1"] - BOSS_R - 1.0, p["inner_y1"] - BOSS_R - 1.0),
        ("east_power", p["inner_x1"] - BOSS_R - 1.0, tall_y0 + max(BUCK_W, FUSE_W) * 0.5),
        ("south_lcd", (bay_x0 + bay_x1) / 2.0, p["inner_y0"] + BOSS_R + 1.0),
    ]
    p["bosses"] = bosses
    _assert_bosses_clear(p)
    return p


def _assert_bosses_clear(p: dict) -> None:
    """Bosses must miss the kit, the LCD holes, the glands, and the power parts."""
    jetson = (p["board_x"] - 1.0, p["board_y"] - 1.0, JETSON_X + 2.0, JETSON_Y + 2.0)
    blocks = [jetson]
    for key in ("buck", "fuse", "tb_shunt", "tb_load"):
        x, y, lx, ly, _lz = p[key]
        blocks.append((x - 1.0, y - 1.0, lx + 2.0, ly + 2.0))
    for name, x, y in p["bosses"]:
        for bx, by, lx, ly in blocks:
            if bx - BOSS_R < x < bx + lx + BOSS_R and by - BOSS_R < y < by + ly + BOSS_R:
                raise SystemExit(f"boss {name} hits a kept-out block at ({x:.1f}, {y:.1f})")
        for hx, hy in p["lcd_holes"]:
            if math.hypot(x - hx, y - hy) < BOSS_R + 3.5 + 1.0:
                raise SystemExit(f"boss {name} is too close to an LCD standoff")
        for gland in p["glands"]:
            limit = gland["diameter"] / 2.0 + BOSS_R + 1.0
            if math.hypot(x - gland["x"], y - p["inner_y1"]) < limit:
                raise SystemExit(f"boss {name} is too close to gland {gland['name']}")


def _box(x: float, y: float, z: float, lx: float, ly: float, lz: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(lx, ly, lz, centered=(False, False, False))
        .translate((x, y, z))
    )


def _cyl(x: float, y: float, z: float, r: float, h: float) -> cq.Workplane:
    return cq.Workplane("XY").center(x, y).workplane(offset=z).circle(r).extrude(h)


def _hex(x: float, y: float, z: float, across_flats: float, h: float) -> cq.Workplane:
    # cadquery polygon() diameter is the circumscribed diameter.
    circum = across_flats / math.cos(math.radians(30.0))
    return (
        cq.Workplane("XY")
        .center(x, y)
        .workplane(offset=z)
        .polygon(6, circum)
        .extrude(h)
    )


def _teardrop(cx: float, y0: float, cz: float, radius: float, length: float) -> cq.Workplane:
    """Horizontal hole along +Y. The point is up, so the overhang is 45 degrees."""
    angle = math.radians(45.0)
    left = (radius * math.cos(math.pi - angle), radius * math.sin(angle))
    right = (radius * math.cos(angle), radius * math.sin(angle))
    tip_z = radius * math.sqrt(2.0)
    # Workplane "XZ" extrudes toward -Y. Negative length runs the hole toward +Y.
    circle = (
        cq.Workplane("XZ")
        .center(cx, cz)
        .circle(radius)
        .extrude(-length)
        .translate((0, y0, 0))
    )
    wedge = (
        cq.Workplane("XZ")
        .center(cx, cz)
        .moveTo(left[0], left[1])
        .lineTo(0.0, tip_z)
        .lineTo(right[0], right[1])
        .close()
        .extrude(-length)
        .translate((0, y0, 0))
    )
    return circle.union(wedge)


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

    # Port openings on the south and west edges of the kit only.
    # A sill stays below the carrier and a rail stays above the envelope.
    opening_z0 = FLOOR + 1.5
    opening_z1 = FLOOR + SHELF_H + JETSON_Z - 1.0
    opening_h = opening_z1 - opening_z0
    west = _box(
        -1.0,
        p["board_y"] + 14.0,
        opening_z0,
        WALL + 2.0,
        JETSON_Y - 28.0,
        opening_h,
    )
    south = _box(
        p["board_x"] + 14.0,
        -1.0,
        opening_z0,
        JETSON_X - 28.0,
        WALL + 2.0,
        opening_h,
    )
    solid = solid.cut(west).cut(south)

    features: list[cq.Workplane] = []

    # Cradle shelves under the four edges of the kit. They support the
    # carrier from below. They do not clamp an unknown PCB thickness.
    # Embed 0.2 mm into the floor. A face-coincident union stays a separate solid.
    shelf_z = FLOOR - 0.2
    shelf_top = FLOOR + SHELF_H
    bx, by = p["board_x"], p["board_y"]
    rib_w = 7.0
    features.append(_box(bx, by, shelf_z, JETSON_X, rib_w, SHELF_H + 0.2))
    features.append(_box(bx, by + JETSON_Y - rib_w, shelf_z, JETSON_X, rib_w, SHELF_H + 0.2))
    features.append(_box(bx, by, shelf_z, rib_w, JETSON_Y, SHELF_H + 0.2))
    features.append(_box(bx + JETSON_X - rib_w, by, shelf_z, rib_w, JETSON_Y, SHELF_H + 0.2))

    # Corner locating ribs. Inner face is FIT clear of the 100 x 80 envelope.
    # Only the corners, so the middle of each port edge stays open. The ribs
    # sit in the wall or in the wire channel; they do not refill the openings.
    loc_h = 5.0
    loc_t = 2.2
    loc_l = 12.0
    g = FIT

    def _rib_x(x_start: float, y_start: float) -> cq.Workplane:
        return _box(x_start, y_start, shelf_z, loc_l, loc_t, SHELF_H + loc_h + 0.2)

    def _rib_y(x_start: float, y_start: float) -> cq.Workplane:
        return _box(x_start, y_start, shelf_z, loc_t, loc_l, SHELF_H + loc_h + 0.2)

    # South-west, outside the kit, buried in the corner walls.
    features.append(_rib_x(bx - g - loc_t, by - g - loc_t))
    features.append(_rib_y(bx - g - loc_t, by - g - loc_t))
    # South-east.
    features.append(_rib_x(bx + JETSON_X + g + loc_t - loc_l, by - g - loc_t))
    features.append(_rib_y(bx + JETSON_X + g, by - g - loc_t))
    # North-west, in the wire channel.
    features.append(_rib_x(bx - g - loc_t, by + JETSON_Y + g))
    features.append(_rib_y(bx - g - loc_t, by + JETSON_Y + g + loc_t - loc_l))
    # North-east.
    features.append(_rib_x(bx + JETSON_X + g + loc_t - loc_l, by + JETSON_Y + g))
    features.append(_rib_y(bx + JETSON_X + g, by + JETSON_Y + g + loc_t - loc_l))

    # Optional Jetson screw bosses. Off unless JETSON_HOLE_XY is filled in
    # from the P3449 file or the P3450 STEP.
    for hx, hy in JETSON_HOLE_XY:
        features.append(_cyl(bx + hx, by + hy, FLOOR - 0.2, 3.5, SHELF_H + 0.2))

    # INA228 standoffs.
    for hx, hy in INA_HOLES:
        features.append(
            _cyl(p["ina_x"] + hx, p["ina_y"] + hy, FLOOR - 0.2, 3.0, INA_STANDOFF + 0.2)
        )

    # Adapter cleats. The dongle's holes are unknown, so rails locate the
    # unverified envelope with FIT clearance per side.
    ax, ay = p["adapter_x"], p["adapter_y"]
    cleat_h = 3.2
    features.append(_box(ax - FIT - 1.6, ay - FIT - 1.6, FLOOR - 0.2, ADAPTER_L + 2 * FIT + 3.2, 1.6, cleat_h))
    features.append(_box(ax - FIT - 1.6, ay + ADAPTER_W + FIT, FLOOR - 0.2, ADAPTER_L + 2 * FIT + 3.2, 1.6, cleat_h))
    features.append(_box(ax - FIT - 1.6, ay - FIT, FLOOR - 0.2, 1.6, ADAPTER_W + 2 * FIT, cleat_h))

    # Screw bosses, embedded 0.2 mm into the floor.
    for _name, x, y in p["bosses"]:
        features.append(_cyl(x, y, FLOOR - 0.2, BOSS_R, p["base_h"] - FLOOR + 0.2))

    # Low pads under the unverified power parts so a zip-tie or an M3 screw
    # has a land. The pads are 2 mm tall.
    for key in ("buck", "fuse", "tb_shunt", "tb_load"):
        x, y, lx, ly, _lz = p[key]
        features.append(_box(x, y, FLOOR - 0.2, lx, ly, 2.2))

    solid = solid.union(_fuse(features))

    cutters: list[cq.Workplane] = []

    # Insert holes, from the top of each boss.
    for _name, x, y in p["bosses"]:
        cutters.append(_cyl(x, y, p["base_h"] - INSERT_DEPTH, INSERT_HOLE_D / 2.0, INSERT_DEPTH + 1.0))

    # INA228 screw holes and M2 nut pockets opened through the bottom.
    nut_af = M2_NUT_AF + 2.0 * FIT
    for hx, hy in INA_HOLES:
        x = p["ina_x"] + hx
        y = p["ina_y"] + hy
        cutters.append(_cyl(x, y, -0.5, M2_CLEAR / 2.0, INA_STANDOFF + FLOOR + 1.0))
        cutters.append(_hex(x, y, -0.2, nut_af, M2_NUT_T + 0.4))

    for hx, hy in JETSON_HOLE_XY:
        cutters.append(
            _cyl(bx + hx, by + hy, -0.5, M2_CLEAR / 2.0, SHELF_H + FLOOR + 1.0)
        )

    # M3 slots in the power pads. The real hole pitch is unknown, so each
    # pad gets two slots and the screw can land anywhere along the slot.
    for key in ("buck", "fuse", "tb_shunt", "tb_load"):
        x, y, lx, ly, _lz = p[key]
        slot_w = M3_CLEAR
        slot_l = min(16.0, lx * 0.45)
        for frac in (0.28, 0.72):
            cutters.append(
                _box(
                    x + lx * frac - slot_l / 2.0,
                    y + ly / 2.0 - slot_w / 2.0,
                    -0.5,
                    slot_l,
                    slot_w,
                    FLOOR + 2.6,
                )
            )

    # Glands. Teardrop so the top of a horizontal hole prints without support.
    for gland in p["glands"]:
        cutters.append(
            _teardrop(
                gland["x"],
                p["outer_y"] - WALL - 1.0,
                gland["z"],
                gland["diameter"] / 2.0,
                WALL + 2.0,
            )
        )

    # Intake slots in the east wall, beside the LCD bay, low in the wall.
    slot_z = FLOOR + 6.0
    for i, y in enumerate(range(0, 4)):
        yy = p["board_y"] + 8.0 + i * 16.0
        cutters.append(_box(p["outer_x"] - WALL - 1.0, yy, slot_z, WALL + 2.0, 3.0, 12.0))

    # Exhaust slots in the west rail above the port opening.
    rail_z = opening_z1 + 1.0
    rail_h = p["base_h"] - rail_z - 2.0
    if rail_h > 6.0:
        for i in range(4):
            yy = p["board_y"] + 18.0 + i * 14.0
            cutters.append(_box(-1.0, yy, rail_z, WALL + 2.0, 3.0, rail_h))

    return _cut_all(solid, cutters)


# Keep the lid off the wall top by a hair so the two solids do not share a face.
LID_SEAT_GAP = 0.05


def build_lid(p: dict) -> cq.Workplane:
    """Lid in assembly orientation, sitting on the base."""
    ox, oy = p["outer_x"], p["outer_y"]
    z_plate = p["base_h"] + LID_SEAT_GAP
    plate = _box(0, 0, z_plate, ox, oy, LID_T)
    features: list[cq.Workplane] = []

    # Skirt. FIT clear of the inner wall. Port edges of the kit are left open.
    # Bosses are cleared afterwards with a cylindrical cut, which is safer
    # than trying to gap every bar by hand.
    x0 = p["inner_x0"] + FIT
    y0 = p["inner_y0"] + FIT
    x1 = p["inner_x1"] - FIT
    y1 = p["inner_y1"] - FIT
    skirt_z = z_plate - SKIRT_H
    features.append(_box(p["bay_x0"], y0, skirt_z, p["bay_w"], SKIRT_T, SKIRT_H + 0.2))
    features.append(_box(x0 + 20.0, y1 - SKIRT_T, skirt_z, (x1 - x0) - 40.0, SKIRT_T, SKIRT_H + 0.2))
    features.append(
        _box(x0, p["tall_y0"] + 4.0, skirt_z, SKIRT_T, y1 - (p["tall_y0"] + 4.0) - 4.0, SKIRT_H + 0.2)
    )
    features.append(_box(x1 - SKIRT_T, y0, skirt_z, SKIRT_T, y1 - y0, SKIRT_H + 0.2))

    # LCD standoffs hang from the inner face. Length is LCD_STANDOFF.
    for hx, hy in p["lcd_holes"]:
        features.append(_cyl(hx, hy, z_plate - LCD_STANDOFF, 3.5, LCD_STANDOFF + 0.2))

    # Stop ribs end 1 mm above the published kit envelope.
    jetson_top = FLOOR + SHELF_H + JETSON_Z
    rib_len = z_plate - (jetson_top + 1.0)
    if rib_len < 2.0:
        raise SystemExit("no room for heatsink stop ribs; internal height is short")
    for xoff in (18.0, 62.0):
        features.append(
            _box(
                p["board_x"] + xoff,
                p["board_y"] + 22.0,
                z_plate - rib_len,
                6.0,
                36.0,
                rib_len + 0.2,
            )
        )

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
        # Clear the skirt around the boss. The boss itself is part of the base.
        cutters.append(_cyl(x, y, skirt_z - 0.5, BOSS_R + 1.5, SKIRT_H + 2.0))

    # Screw hole through each LCD standoff, and an M2 nut pocket at the
    # lower end. In the print orientation that pocket is an open hex on top.
    nut_af = M2_NUT_AF + 2.0 * FIT
    for hx, hy in p["lcd_holes"]:
        cutters.append(_cyl(hx, hy, z_plate - LCD_STANDOFF - 0.5, M2_CLEAR / 2.0, LCD_STANDOFF + LID_T + 1.0))
        cutters.append(_hex(hx, hy, z_plate - LCD_STANDOFF - 0.2, nut_af, M2_NUT_T + 0.6))

    # Vent grid over the kit. Slots are 3 mm wide.
    x = p["board_x"] + 8.0
    while x + 12.0 < p["board_x"] + JETSON_X - 4.0:
        y = p["board_y"] + 6.0
        while y + 8.0 < p["board_y"] + JETSON_Y - 4.0:
            rib_hit = False
            for xoff in (18.0, 62.0):
                rx = p["board_x"] + xoff
                ry = p["board_y"] + 22.0
                if x < rx + 6.0 and x + 3.0 > rx and y < ry + 36.0 and y + 8.0 > ry:
                    rib_hit = True
            if not rib_hit:
                cutters.append(_box(x, y, z_plate - 0.5, 3.0, 8.0, LID_T + 1.0))
            y += 14.0
        x += 12.0

    return _cut_all(solid, cutters)


def lid_to_print(lid: cq.Workplane, p: dict) -> cq.Workplane:
    """Flip the lid so the outer face is on the bed and the skirt points up.

    Rotation about X mirrors Y in the file. Flipping the printed part back
    onto the base undoes that mirror, so the window lands on the LCD bay.
    """
    rotated = lid.rotate((0, 0, 0), (1, 0, 0), 180)
    outer_face = p["base_h"] + LID_SEAT_GAP + LID_T
    return rotated.translate((0, p["outer_y"], outer_face))


def _envelope(x, y, z, lx, ly, lz) -> cq.Workplane:
    return _box(x, y, z, lx, ly, lz)


def reference_solids(p: dict) -> list[tuple[str, cq.Workplane]]:
    """Non-printed envelopes. Names start with REF_."""
    z_board = FLOOR + SHELF_H
    solids = [
        (
            "REF_jetson_kit_envelope",
            _envelope(p["board_x"], p["board_y"], z_board, JETSON_X, JETSON_Y, JETSON_Z),
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
            "REF_lcd_module",
            _envelope(p["lcd_x"], p["lcd_y"], p["base_h"] - LCD_STANDOFF, LCD_X, LCD_Y, LCD_STANDOFF),
        ),
        (
            "REF_lcd_backpack_UNVERIFIED",
            _envelope(
                p["lcd_x"] + 15.0,
                p["lcd_y"] + 10.0,
                p["base_h"] - LCD_STANDOFF - LCD_BACKPACK_DEPTH,
                LCD_X - 30.0,
                LCD_Y - 20.0,
                LCD_BACKPACK_DEPTH,
            ),
        ),
        (
            "REF_usb_i2c_adapter_UNVERIFIED",
            _envelope(p["adapter_x"], p["adapter_y"], FLOOR + 2.0, ADAPTER_L, ADAPTER_W, ADAPTER_H),
        ),
    ]
    for key in ("buck", "fuse", "tb_shunt", "tb_load"):
        x, y, lx, ly, lz = p[key]
        solids.append((f"REF_{key}_UNVERIFIED", _envelope(x, y, FLOOR + 2.0, lx, ly, lz)))
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
    """Draw every triangle in one collection, far to near, so the lid does not stripe."""
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
    order = np.argsort(depth)  # far first
    coll = Poly3DCollection(faces[order], facecolors=colors[order], edgecolors="none", linewidths=0)
    ax.add_collection3d(coll)


def render_preview(p: dict, meshes: dict[str, trimesh.Trimesh], path: Path) -> None:
    fig = plt.figure(figsize=(12.8, 6.4), dpi=130)
    # The left view looks into the base. The right view holds the lid above it.
    # A closed stack fights matplotlib's depth sort on the lid, so the lid is
    # shown lifted rather than as a second opaque shell.
    titles = ("Interior", "Lid lifted")
    lifts = (0.0, 48.0)
    show_lid = (False, True)
    for panel, (title, lift, draw_lid) in enumerate(zip(titles, lifts, show_lid), start=1):
        ax = fig.add_subplot(1, 2, panel, projection="3d")
        layers: list[tuple[np.ndarray, tuple[float, float, float], float]] = []
        layers.append((_decimate(meshes["base"], 14000), (0.62, 0.66, 0.70), 0.30))
        if draw_lid:
            lid_faces = _decimate(meshes["lid_asm"], 10000).copy()
            lid_faces[:, :, 2] += lift
            layers.append((lid_faces, (0.16, 0.40, 0.56), 0.45))
        colors = {
            "jetson": (0.15, 0.55, 0.32),
            "ina": (0.80, 0.38, 0.12),
            "lcd": (0.20, 0.38, 0.75),
            "backpack": (0.40, 0.28, 0.62),
            "adapter": (0.45, 0.48, 0.52),
            "buck": (0.55, 0.40, 0.18),
            "fuse": (0.72, 0.18, 0.18),
            "tb": (0.25, 0.28, 0.32),
        }
        for name, mesh in meshes["refs"]:
            if "jetson" in name:
                color = colors["jetson"]
            elif "ina" in name:
                color = colors["ina"]
            elif "backpack" in name:
                color = colors["backpack"]
            elif "lcd" in name:
                color = colors["lcd"]
            elif "adapter" in name:
                color = colors["adapter"]
            elif "buck" in name:
                color = colors["buck"]
            elif "fuse" in name:
                color = colors["fuse"]
            else:
                color = colors["tb"]
            layers.append((_decimate(mesh, 2500), color, 0.95))
        _paint_sorted(ax, layers)
        ax.set_title(title, fontsize=11, pad=8)
        ax.set_box_aspect((p["outer_x"], p["outer_y"], max(p["outer_z"] + lift, 80)))
        ax.set_xlim(0, p["outer_x"])
        ax.set_ylim(0, p["outer_y"])
        ax.set_zlim(0, p["outer_z"] + lift)
        ax.view_init(elev=32 if draw_lid else 38, azim=-62)
        ax.set_axis_off()
    fig.suptitle(
        "Jetson Nano battery-monitor enclosure  "
        f"{p['outer_x']:.1f} x {p['outer_y']:.1f} x {p['outer_z']:.1f} mm",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path)
    plt.close(fig)


def _public_dimensions(p: dict) -> dict:
    """JSON the README quotes. Rounded, with the unverified list called out."""
    return {
        "units": "mm",
        "outer_x": _r3(p["outer_x"]),
        "outer_y": _r3(p["outer_y"]),
        "outer_z": _r3(p["outer_z"]),
        "base_h": _r3(p["base_h"]),
        "internal_x": _r3(p["inner_x1"] - p["inner_x0"]),
        "internal_y": _r3(p["inner_y1"] - p["inner_y0"]),
        "internal_z": _r3(p["internal_h"]),
        "wall": WALL,
        "floor": FLOOR,
        "lid_t": LID_T,
        "fit_per_side": FIT,
        "gland_print_allowance_per_side": PRINT_HOLE_ALLOW,
        "pg7_datasheet_hole": PG7_HOLE,
        "pg9_datasheet_hole": PG9_HOLE,
        "pg7_printed_hole": _r3(p["pg7_printed"]),
        "pg9_printed_hole": _r3(p["pg9_printed"]),
        "glands": [
            {
                "name": g["name"],
                "thread": g["kind"],
                "x_mm": _r3(g["x"]),
                "z_mm": _r3(g["z"]),
                "printed_diameter_mm": _r3(g["diameter"]),
            }
            for g in p["glands"]
        ],
        "jetson_envelope": [JETSON_X, JETSON_Y, JETSON_Z],
        "jetson_hole_xy": list(JETSON_HOLE_XY),
        "lcd_module": [LCD_X, LCD_Y, LCD_Z_MAX],
        "lcd_window": [_r3(p["window_w"]), _r3(p["window_h"])],
        "shunt": "outside",
        "unverified_parameters": {
            "lcd_standoff_mm": LCD_STANDOFF,
            "lcd_backpack_depth_mm": LCD_BACKPACK_DEPTH,
            "buck_envelope_mm": [BUCK_L, BUCK_W, BUCK_H],
            "fuse_holder_envelope_mm": [FUSE_L, FUSE_W, FUSE_H],
            "terminal_block_envelope_mm": [TB_L, TB_W, TB_H],
            "usb_i2c_adapter_envelope_mm": [ADAPTER_L, ADAPTER_W, ADAPTER_H],
            "bend_clearance_mm": BEND_CLEAR,
            "insert_hole_diameter_mm": INSERT_HOLE_D,
            "insert_depth_mm": INSERT_DEPTH,
            "jetson_hole_xy_mm": list(JETSON_HOLE_XY),
            "jetson_hole_diameter_mm": JETSON_HOLE_D,
        },
    }


def main() -> int:
    EXPORT.mkdir(parents=True, exist_ok=True)
    p = compute()
    print(
        f"outer {p['outer_x']:.2f} x {p['outer_y']:.2f} x {p['outer_z']:.2f} mm, "
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

    assembly = cq.Assembly(name="battery_monitor_enclosure")
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

    # Confirm the STEP files reopen.
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
