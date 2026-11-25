#!/usr/bin/env python3
"""Small printable case for the INA228 breakout, plus a shunt plate.

The case cavity, slots, and flanges are unchanged. A separate plate bolts
to those flanges and carries a 4-terminal shunt on the north side, next to
the sense slot. The Jetson stays where it already is. The case holds only
the INA228 board. Two slots leave the north wall: the sensor cable
(3.3 V, GND, SDA, SCL) and the sense cable (IN+, IN-, VBUS).

Run from this directory:

    python3 enclosure.py

Writes STEP and STL for the base and the lid, an assembly STEP, a preview
PNG, and export/dimensions.json. Dimensions are millimetres.
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

# Adafruit INA228 breakout, product 5832.
# PCB outline and holes from Adafruit's Eagle board
# (adafruit/Adafruit-INA228-PCB, "Adafruit INA228 I2C Power Monitor.brd"):
# outline 25.4 x 20.32 mm, two 2.5 mm holes at (2.54, 17.78) and (22.86, 17.78).
# Assembled size on the product page: 25.8 x 20.2 x 10.1 mm.
# https://www.adafruit.com/product/5832
INA_PCB_X = 25.4
INA_PCB_Y = 20.32
INA_HOLES = ((2.54, 17.78), (22.86, 17.78))
INA_PRODUCT_X = 25.8
INA_PRODUCT_Y = 20.4  # page says 20.2; 20.4 covers the 20.32 PCB
INA_PRODUCT_Z = 10.1

# ISO 273 medium clearance. ISO 4032 M2 nut, across flats and thickness.
M2_CLEAR = 2.4
M3_CLEAR = 3.4
M2_NUT_AF = 4.0
M2_NUT_T = 1.6

# Print allowances. 0.25 mm per side is the fit clearance. Walls are 2.5 mm.
WALL = 2.5
FLOOR = 2.5
LID_T = 2.5
FIT = 0.25

# UNVERIFIED. Not from a datasheet.
INA_STANDOFF = 3.0
AIR_ABOVE = 2.0
SIDE_MARGIN = 9.0
SOUTH_MARGIN = 9.0
BEND_CLEAR = 12.0
SENSOR_CABLE_OD = 4.0
SENSE_CABLE_OD = 4.0
SLOT_DEPTH = 6.0
TAB_LEN = 12.0
TAB_W = 14.0
BOSS_R = 3.6
INSERT_HOLE_D = 3.2
INSERT_DEPTH = 4.0
SKIRT_H = 3.0
SKIRT_T = 1.6
LID_SEAT_GAP = 0.05

# Accuenergy Shunt-100A, 75 mV. Datasheet revision August 2024, version 1.0.3.
# https://www.accuenergy.com/wp-content/uploads/DC-Current-Shunt-100A-75mV.pdf
# One drawing gives these length callouts. This model centers the 85 mm and
# 62 mm spans on the 104 mm length.
SHUNT_L = 104.0
SHUNT_W = 21.6
SHUNT_T = 2.0
SHUNT_CURRENT_PITCH = 85.0
SHUNT_CURRENT_HOLE = 8.5
SHUNT_SENSE_PITCH = 62.0
SHUNT_SENSE_THREAD = 5.0  # drawing says 2-M5; thread size, not a drilled plate hole

# Plate parameters. Not on the shunt drawing.
PLATE_T = 4.0
PLATE_GAP = 0.05  # keeps the plate from sharing a face with the case
STANDOFF_H = 12.0  # clears an ISO 4032 M8 nut (thickness 6.8 mm) under the terminal
STANDOFF_R = 3.0
LUG_CLEAR_D = 18.0  # through-window; an M8 nut is 13 mm across flats
GAP_NORTH = 14.0
DECK_MARGIN = 6.0
PLATE_NORTH_MARGIN = 4.0
CHANNEL_W = 8.0
CHANNEL_FLOOR_Z = 10.0
CHANNEL_RIB_H = 4.0
CHANNEL_RIB_T = 1.6


def _r3(value: float) -> float:
    return round(float(value), 3)


def compute() -> dict:
    internal_h = INA_STANDOFF + INA_PRODUCT_Z + AIR_ABOVE
    inner_w = INA_PRODUCT_X + 2.0 * SIDE_MARGIN
    inner_d = SOUTH_MARGIN + INA_PRODUCT_Y + BEND_CLEAR
    outer_x = inner_w + 2.0 * WALL
    outer_y = inner_d + 2.0 * WALL
    base_h = FLOOR + internal_h
    outer_z = base_h + LID_T

    inner_x0 = WALL
    inner_y0 = WALL
    inner_x1 = WALL + inner_w
    inner_y1 = WALL + inner_d

    # Center the PCB in the product keep-out, which is slightly larger.
    ina_x = inner_x0 + SIDE_MARGIN + (INA_PRODUCT_X - INA_PCB_X) / 2.0
    ina_y = inner_y0 + SOUTH_MARGIN + (INA_PRODUCT_Y - INA_PCB_Y) / 2.0

    slot_w_sensor = SENSOR_CABLE_OD + 2.0 * FIT
    slot_w_sense = SENSE_CABLE_OD + 2.0 * FIT
    slots = [
        {
            "name": "sensor",
            "x": 16.0,
            "w": slot_w_sensor,
            "carries": "sensor cable: pin 1 3.3 V, pin 6 GND, pin 3 SDA, pin 5 SCL",
        },
        {
            "name": "sense",
            "x": 28.0,
            "w": slot_w_sense,
            "carries": "sense cable: IN+, IN-, VBUS",
        },
    ]

    bosses = [
        ("sw", inner_x0 + BOSS_R + 0.8, inner_y0 + BOSS_R + 0.8),
        ("se", inner_x1 - BOSS_R - 0.8, inner_y0 + BOSS_R + 0.8),
        ("nw", inner_x0 + BOSS_R + 0.8, inner_y1 - BOSS_R - 0.8),
        ("ne", inner_x1 - BOSS_R - 0.8, inner_y1 - BOSS_R - 0.8),
    ]

    board = (
        ina_x - 0.4,
        ina_y - 0.4,
        INA_PRODUCT_X + 0.4,
        INA_PRODUCT_Y + 0.4,
    )
    for name, x, y in bosses:
        if _hit(board, x - BOSS_R, y - BOSS_R, 2 * BOSS_R, 2 * BOSS_R):
            raise SystemExit(f"boss {name} hits the INA228")
    for slot in slots:
        for name, x, y in bosses:
            if abs(x - (slot["x"] + slot["w"] / 2.0)) < BOSS_R + slot["w"] / 2.0 + 1.0:
                if y > inner_y1 - BOSS_R - 2.0:
                    raise SystemExit(f"boss {name} blocks slot {slot['name']}")
        if slot["x"] < WALL or slot["x"] + slot["w"] > outer_x - WALL:
            raise SystemExit(f"slot {slot['name']} leaves the north wall")

    return {
        "outer_x": outer_x,
        "outer_y": outer_y,
        "outer_z": outer_z,
        "base_h": base_h,
        "internal_h": internal_h,
        "inner_x0": inner_x0,
        "inner_y0": inner_y0,
        "inner_x1": inner_x1,
        "inner_y1": inner_y1,
        "ina_x": ina_x,
        "ina_y": ina_y,
        "slots": slots,
        "bosses": bosses,
    }


def shunt_layout(p: dict) -> dict:
    """North plate. It uses the existing flange holes and does not alter the case."""
    sense = next(slot for slot in p["slots"] if slot["name"] == "sense")
    slot_cx = sense["x"] + sense["w"] / 2.0
    ox, oy = p["outer_x"], p["outer_y"]
    shunt_south = oy + GAP_NORTH
    shunt_cx = slot_cx
    shunt_cy = shunt_south + SHUNT_W / 2.0
    shunt_x0 = shunt_cx - SHUNT_L / 2.0
    deck_x0 = shunt_x0 - DECK_MARGIN
    deck_x1 = shunt_x0 + SHUNT_L + DECK_MARGIN
    deck_y0 = oy + 0.05
    deck_y1 = shunt_south + SHUNT_W + PLATE_NORTH_MARGIN
    z1 = -PLATE_GAP
    z0 = z1 - PLATE_T
    tab_y0 = (oy - TAB_W) / 2.0
    # Same centers as the M3 holes already drilled in the case flanges.
    flange_holes = [(-(TAB_LEN - 6.0), oy / 2.0), (ox + (TAB_LEN - 6.0), oy / 2.0)]
    standoffs = [
        (shunt_cx + sx, shunt_cy + sy)
        for sx in (-20.0, 20.0)
        for sy in (-6.5, 6.5)
    ]
    currents = [
        (shunt_cx + sign * SHUNT_CURRENT_PITCH / 2.0, shunt_cy) for sign in (-1.0, 1.0)
    ]
    senses = [
        (shunt_cx + sign * SHUNT_SENSE_PITCH / 2.0, shunt_cy) for sign in (-1.0, 1.0)
    ]
    for sx, sy in standoffs:
        for hx, hy in currents:
            if math.hypot(sx - hx, sy - hy) < STANDOFF_R + LUG_CLEAR_D / 2.0 + 1.0:
                raise SystemExit("a shunt standoff falls in a lug window")
        if not (deck_x0 + STANDOFF_R < sx < deck_x1 - STANDOFF_R and deck_y0 + STANDOFF_R < sy < deck_y1 - STANDOFF_R):
            raise SystemExit("a shunt standoff misses the plate")
    return {
        "slot_cx": slot_cx,
        "shunt_x0": shunt_x0,
        "shunt_y0": shunt_south,
        "shunt_cx": shunt_cx,
        "shunt_cy": shunt_cy,
        "deck_x0": deck_x0,
        "deck_x1": deck_x1,
        "deck_y0": deck_y0,
        "deck_y1": deck_y1,
        "z0": z0,
        "z1": z1,
        "tab_y0": tab_y0,
        "flange_holes": flange_holes,
        "standoffs": standoffs,
        "currents": currents,
        "senses": senses,
        "xmin": min(deck_x0, -TAB_LEN),
        "xmax": max(deck_x1, ox + TAB_LEN),
        "ymin": 0.0,
        "ymax": deck_y1,
    }


def _hit(rect, x, y, w, h) -> bool:
    rx, ry, rw, rh = rect
    return x < rx + rw and x + w > rx and y < ry + rh and y + h > ry


def _box(x, y, z, lx, ly, lz) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(lx, ly, lz, centered=(False, False, False))
        .translate((x, y, z))
    )


def _cyl(x, y, z, r, h) -> cq.Workplane:
    return cq.Workplane("XY").center(x, y).workplane(offset=z).circle(r).extrude(h)


def _hex(x, y, z, across_flats, h) -> cq.Workplane:
    circum = across_flats / math.cos(math.radians(30.0))
    return cq.Workplane("XY").center(x, y).workplane(offset=z).polygon(6, circum).extrude(h)


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


def _uslot(x, width, y0, length, base_h) -> cq.Workplane:
    radius = width / 2.0
    z_round = base_h - SLOT_DEPTH
    rect = _box(x, y0, z_round, width, length, SLOT_DEPTH + 1.0)
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

    tab_y = (oy - TAB_W) / 2.0
    features.append(_box(-TAB_LEN, tab_y, 0, TAB_LEN + 0.4, TAB_W, FLOOR))
    features.append(_box(ox - 0.4, tab_y, 0, TAB_LEN + 0.4, TAB_W, FLOOR))

    for _name, x, y in p["bosses"]:
        features.append(_cyl(x, y, FLOOR - 0.2, BOSS_R, bh - FLOOR + 0.2))

    for hx, hy in INA_HOLES:
        features.append(_cyl(p["ina_x"] + hx, p["ina_y"] + hy, FLOOR - 0.2, 2.6, INA_STANDOFF + 0.2))

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

    hole_r = M3_CLEAR / 2.0
    for sign, x_body in ((-1.0, 0.0), (1.0, ox)):
        hx = x_body + sign * (TAB_LEN - 6.0)
        cutters.append(_cyl(hx, oy / 2.0, -0.5, hole_r, FLOOR + 1.0))

    for slot in p["slots"]:
        cutters.append(_uslot(slot["x"], slot["w"], oy - WALL - 1.0, WALL + 2.0, bh))

    return _cut_all(solid, cutters)


def build_lid(p: dict) -> cq.Workplane:
    ox, oy = p["outer_x"], p["outer_y"]
    z_plate = p["base_h"] + LID_SEAT_GAP
    plate = _box(0, 0, z_plate, ox, oy, LID_T)
    x0 = p["inner_x0"] + FIT
    y0 = p["inner_y0"] + FIT
    x1 = p["inner_x1"] - FIT
    y1 = p["inner_y1"] - FIT
    skirt_z = z_plate - SKIRT_H
    features = [
        _box(x0 + 8.0, y0, skirt_z, (x1 - x0) - 16.0, SKIRT_T, SKIRT_H + 0.2),
        _box(x0, y0 + 8.0, skirt_z, SKIRT_T, (y1 - y0) - 16.0, SKIRT_H + 0.2),
        _box(x1 - SKIRT_T, y0 + 8.0, skirt_z, SKIRT_T, (y1 - y0) - 16.0, SKIRT_H + 0.2),
    ]
    blocked = [(s["x"] - 1.0, s["x"] + s["w"] + 1.0) for s in p["slots"]]
    cursor = x0
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
            features.append(_box(cursor, y1 - SKIRT_T, skirt_z, nxt - cursor, SKIRT_T, SKIRT_H + 0.2))
        cursor = nxt

    solid = plate.union(_fuse(features))
    cutters = []
    for _name, x, y in p["bosses"]:
        cutters.append(_cyl(x, y, z_plate - 0.5, M2_CLEAR / 2.0, LID_T + 1.0))
        cutters.append(_cyl(x, y, skirt_z - 0.5, BOSS_R + 1.2, SKIRT_H + 2.0))
    return _cut_all(solid, cutters)


def lid_to_print(lid: cq.Workplane, p: dict) -> cq.Workplane:
    """Outer face on the bed. Rotating about X mirrors Y; flipping it back undoes that."""
    rotated = lid.rotate((0, 0, 0), (1, 0, 0), 180)
    outer_face = p["base_h"] + LID_SEAT_GAP + LID_T
    return rotated.translate((0, p["outer_y"], outer_face))


def build_shunt_base(p: dict, plate: dict) -> cq.Workplane:
    ox = p["outer_x"]
    z0, z1 = plate["z0"], plate["z1"]
    parts = [
        _box(-TAB_LEN, plate["tab_y0"], z0, TAB_LEN, plate["deck_y0"] + 0.4 - plate["tab_y0"], PLATE_T),
        _box(ox, plate["tab_y0"], z0, TAB_LEN, plate["deck_y0"] + 0.4 - plate["tab_y0"], PLATE_T),
        _box(
            plate["deck_x0"],
            plate["deck_y0"],
            z0,
            plate["deck_x1"] - plate["deck_x0"],
            plate["deck_y1"] - plate["deck_y0"],
            PLATE_T,
        ),
    ]
    for x, y in plate["standoffs"]:
        parts.append(_cyl(x, y, z1 - 0.2, STANDOFF_R, STANDOFF_H + 0.2))

    y0 = p["outer_y"] + 0.2
    y1 = plate["shunt_y0"] - 0.4
    cx = plate["slot_cx"]
    parts.append(_box(cx - CHANNEL_W / 2.0, y0, z1 - 0.2, CHANNEL_W, y1 - y0, CHANNEL_FLOOR_Z - z1 + 0.2))
    rib_top = CHANNEL_FLOOR_Z + CHANNEL_RIB_H
    parts.append(_box(cx - CHANNEL_W / 2.0 - CHANNEL_RIB_T, y0, z1 - 0.2, CHANNEL_RIB_T, y1 - y0, rib_top - z1 + 0.2))
    parts.append(_box(cx + CHANNEL_W / 2.0, y0, z1 - 0.2, CHANNEL_RIB_T, y1 - y0, rib_top - z1 + 0.2))

    solid = _fuse(parts)
    cutters = []
    for x, y in plate["flange_holes"]:
        cutters.append(_cyl(x, y, z0 - 0.5, M3_CLEAR / 2.0, PLATE_T + 1.0))
    for x, y in plate["currents"]:
        cutters.append(_cyl(x, y, z0 - 0.5, LUG_CLEAR_D / 2.0, PLATE_T + 1.0))
    return _cut_all(solid, cutters)


def shunt_placeholder(plate: dict) -> cq.Workplane:
    """Simple envelope of the Accuenergy bar, with the four terminal holes."""
    z = plate["z1"] + STANDOFF_H + 0.05
    body = _box(plate["shunt_x0"], plate["shunt_y0"], z, SHUNT_L, SHUNT_W, SHUNT_T)
    cutters = [_cyl(x, y, z - 0.2, SHUNT_CURRENT_HOLE / 2.0, SHUNT_T + 0.4) for x, y in plate["currents"]]
    cutters += [_cyl(x, y, z - 0.2, SHUNT_SENSE_THREAD / 2.0, SHUNT_T + 0.4) for x, y in plate["senses"]]
    return _cut_all(body, cutters)


def reference_solids(p: dict) -> list[tuple[str, cq.Workplane]]:
    z = FLOOR + INA_STANDOFF
    x = p["ina_x"] - (INA_PRODUCT_X - INA_PCB_X) / 2.0
    y = p["ina_y"] - (INA_PRODUCT_Y - INA_PCB_Y) / 2.0
    return [("REF_ina228", _box(x, y, z, INA_PRODUCT_X, INA_PRODUCT_Y, INA_PRODUCT_Z))]


def _require_single_valid_solid(workplane: cq.Workplane, label: str) -> None:
    shape = workplane.val()
    if not shape.isValid():
        raise SystemExit(f"{label} is not a valid solid")
    solids = shape.Solids()
    if len(solids) != 1:
        raise SystemExit(f"{label} has {len(solids)} solids, expected 1")
    if shape.Volume() < 1000.0:
        raise SystemExit(f"{label} volume {shape.Volume():.1f} mm^3 is implausibly small")


def _interference(a: cq.Workplane, b: cq.Workplane) -> float:
    return float(a.intersect(b).val().Volume())


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


def _paint_sorted(ax, layers) -> None:
    elev, azim = 28.0, -58.0
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
    order = np.argsort(faces.mean(axis=1) @ camera)
    ax.add_collection3d(
        Poly3DCollection(faces[order], facecolors=colors[order], edgecolors="none", linewidths=0)
    )


def render_preview(p: dict, plate: dict, meshes: dict, path: Path) -> None:
    fig = plt.figure(figsize=(12.4, 5.6), dpi=130)
    x0, x1 = plate["xmin"], plate["xmax"]
    span_x = x1 - x0
    span_y = plate["ymax"] - plate["ymin"]
    z0 = plate["z0"]
    for panel, (title, lift, draw_lid) in enumerate(
        (("Case and shunt", 0.0, False), ("Lid lifted", 18.0, True)), start=1
    ):
        ax = fig.add_subplot(1, 2, panel, projection="3d")
        layers = [
            (_decimate(meshes["plate"], 6000), (0.45, 0.48, 0.52), 0.95),
            (_decimate(meshes["base"], 8000), (0.62, 0.66, 0.70), 0.35),
        ]
        if draw_lid:
            lid_faces = _decimate(meshes["lid_asm"], 4000).copy()
            lid_faces[:, :, 2] += lift
            layers.append((lid_faces, (0.16, 0.40, 0.56), 0.55))
        for name, mesh in meshes["refs"]:
            color = (0.72, 0.48, 0.22) if "shunt" in name else (0.80, 0.38, 0.12)
            layers.append((_decimate(mesh, 1500), color, 0.95))
        _paint_sorted(ax, layers)
        ax.set_title(title, fontsize=11, pad=8)
        ax.set_box_aspect((span_x, span_y, max(p["outer_z"] + lift - z0, 30)))
        ax.set_xlim(x0, x1)
        ax.set_ylim(plate["ymin"], plate["ymax"])
        ax.set_zlim(z0, p["outer_z"] + lift)
        ax.view_init(elev=28, azim=-58)
        ax.set_axis_off()
    fig.suptitle(
        "INA228 case and shunt plate  "
        f"{plate['xmax'] - plate['xmin']:.1f} x {plate['ymax']:.1f} x {p['outer_z'] - plate['z0']:.1f} mm",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path)
    plt.close(fig)


def _public_dimensions(p: dict, plate: dict) -> dict:
    return {
        "units": "mm",
        "role": "ina228_case_with_shunt_plate",
        "body_x": _r3(p["outer_x"]),
        "body_y": _r3(p["outer_y"]),
        "outer_x_with_flanges": _r3(p["outer_x"] + 2.0 * TAB_LEN),
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
        "mounting": {
            "type": "floor flanges, one each side",
            "tab_length_mm": TAB_LEN,
            "tab_width_mm": TAB_W,
            "hole": "M3 clearance, ISO 273 medium, 3.4 mm",
            "hole_diameter_mm": M3_CLEAR,
        },
        "cables": [
            {"slot": s["name"], "slot_width_mm": _r3(s["w"]), "carries": s["carries"], "x_mm": _r3(s["x"])}
            for s in p["slots"]
        ],
        "board": "Adafruit INA228 product 5832, 25.8 x 20.4 x 10.1 mm keep-out",
        "not_in_this_box": ["Jetson Nano"],
        "shunt_plate": {
            "part": "shunt_base",
            "bolts_to": "the two existing M3 flange holes; the case solid is unchanged",
            "printed_extents_mm": [
                _r3(plate["xmax"] - plate["xmin"]),
                _r3(plate["ymax"] - plate["tab_y0"]),
                _r3(max(plate["z1"] + STANDOFF_H, CHANNEL_FLOOR_Z + CHANNEL_RIB_H) - plate["z0"]),
            ],
            "sheet_thickness_mm": PLATE_T,
            "overall_x": _r3(plate["xmax"] - plate["xmin"]),
            "overall_y": _r3(plate["ymax"]),
            "overall_z": _r3(p["outer_z"] - plate["z0"]),
            "shunt_model": "Accuenergy Shunt-100A, 75 mV",
            "shunt_source": "https://www.accuenergy.com/wp-content/uploads/DC-Current-Shunt-100A-75mV.pdf",
            "shunt_footprint_mm": [SHUNT_L, SHUNT_W, SHUNT_T],
            "current_hole_pitch_mm": SHUNT_CURRENT_PITCH,
            "current_hole_diameter_mm": SHUNT_CURRENT_HOLE,
            "sense_screw_pitch_mm": SHUNT_SENSE_PITCH,
            "sense_thread": "M5",
            "lug_window_diameter_mm": LUG_CLEAR_D,
            "standoff_height_mm": STANDOFF_H,
        },
        "unverified_parameters": {
            "ina_standoff_mm": INA_STANDOFF,
            "air_above_mm": AIR_ABOVE,
            "sensor_cable_od_mm": SENSOR_CABLE_OD,
            "sense_cable_od_mm": SENSE_CABLE_OD,
            "bend_clearance_mm": BEND_CLEAR,
            "insert_hole_diameter_mm": INSERT_HOLE_D,
            "insert_depth_mm": INSERT_DEPTH,
            "mount_tab_length_mm": TAB_LEN,
            "mount_tab_width_mm": TAB_W,
            "plate_thickness_mm": PLATE_T,
            "standoff_height_mm": STANDOFF_H,
            "lug_window_diameter_mm": LUG_CLEAR_D,
            "gap_north_mm": GAP_NORTH,
            "channel_width_mm": CHANNEL_W,
        },
    }


def main() -> int:
    EXPORT.mkdir(parents=True, exist_ok=True)
    p = compute()
    print(
        f"body {p['outer_x']:.2f} x {p['outer_y']:.2f} x {p['outer_z']:.2f} mm, "
        f"with flanges {p['outer_x'] + 2 * TAB_LEN:.2f} x {p['outer_y']:.2f}, "
        f"internal {p['inner_x1'] - p['inner_x0']:.2f} x "
        f"{p['inner_y1'] - p['inner_y0']:.2f} x {p['internal_h']:.2f} mm"
    )
    base = build_base(p)
    _require_single_valid_solid(base, "base")
    lid_asm = build_lid(p)
    _require_single_valid_solid(lid_asm, "lid")
    lid_print = lid_to_print(lid_asm, p)
    plate = shunt_layout(p)
    shunt_base = build_shunt_base(p, plate)
    _require_single_valid_solid(shunt_base, "shunt base")
    shunt_ref = shunt_placeholder(plate)
    overlap = _interference(base, lid_asm)
    plate_overlap = _interference(base, shunt_base)
    lid_overlap = _interference(lid_asm, shunt_base)
    print(
        f"intersection mm^3  base/lid {overlap:.3f}  "
        f"base/plate {plate_overlap:.3f}  lid/plate {lid_overlap:.3f}"
    )
    if max(overlap, plate_overlap, lid_overlap) > 5.0:
        raise SystemExit("printed solids intersect")
    print(
        f"shunt plate x {plate['xmin']:.2f}..{plate['xmax']:.2f}  "
        f"y {plate['tab_y0']:.2f}..{plate['ymax']:.2f}  "
        f"overall {plate['xmax'] - plate['xmin']:.2f} x {plate['ymax']:.2f} x "
        f"{p['outer_z'] - plate['z0']:.2f} mm"
    )

    bb = lid_asm.val().BoundingBox()
    if abs(bb.xmin) > 0.5 or abs(bb.ymin) > 0.5:
        raise SystemExit(f"lid assembly XY origin is off: {bb.xmin:.2f}, {bb.ymin:.2f}")
    expected_top = p["base_h"] + LID_SEAT_GAP + LID_T
    if abs(bb.zmax - expected_top) > 0.2:
        raise SystemExit(f"lid top is {bb.zmax:.2f}, expected {expected_top:.2f}")

    _export_solid(base, EXPORT / "base")
    _export_solid(lid_print, EXPORT / "lid")
    _export_solid(shunt_base, EXPORT / "shunt_base")
    assembly = cq.Assembly(name="ina228_with_shunt_plate")
    assembly.add(base, name="base", color=cq.Color(0.62, 0.66, 0.70, 1))
    assembly.add(lid_asm, name="lid", color=cq.Color(0.18, 0.42, 0.58, 1))
    assembly.add(shunt_base, name="shunt_base", color=cq.Color(0.45, 0.48, 0.52, 1))
    assembly.add(shunt_ref, name="REF_shunt", color=cq.Color(0.72, 0.48, 0.22, 0.55))
    ref_meshes = []
    for name, solid in [("REF_shunt", shunt_ref), *reference_solids(p)]:
        if name != "REF_shunt":
            assembly.add(solid, name=name, color=cq.Color(0.80, 0.38, 0.12, 0.45))
        ref_path = EXPORT / f"_{name}.stl"
        cq.exporters.export(solid, str(ref_path), tolerance=0.2, angularTolerance=0.3)
        ref_meshes.append((name, trimesh.load(ref_path, force="mesh")))
        ref_path.unlink()
    assembly.export(str(EXPORT / "assembly.step"), "STEP")

    for stem in ("base", "lid", "shunt_base", "assembly"):
        reopened = cq.importers.importStep(str(EXPORT / f"{stem}.step"))
        if reopened.val().Volume() <= 0:
            raise SystemExit(f"{stem}.step reopened with no volume")

    reports = []
    for stem in ("base", "lid", "shunt_base"):
        report = _mesh_report(EXPORT / f"{stem}.stl")
        reports.append(report)
        print(stem, report)
        if not report["watertight"]:
            raise SystemExit(f"{stem}.stl is not watertight")
        if not report["winding_consistent"]:
            raise SystemExit(f"{stem}.stl winding is inconsistent")
    base_report = reports[0]
    lid_report = reports[1]
    if base_report["extents_mm"] != [72.8, 46.4, 17.6]:
        raise SystemExit(f"case base extents changed: {base_report['extents_mm']}")
    if lid_report["extents_mm"] != [48.8, 46.4, 5.5]:
        raise SystemExit(f"case lid extents changed: {lid_report['extents_mm']}")

    (EXPORT / "dimensions.json").write_text(json.dumps(_public_dimensions(p, plate), indent=2) + "\n")
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
        "plate": trimesh.load(EXPORT / "shunt_base.stl", force="mesh"),
        "lid_asm": trimesh.load(asm_stl, force="mesh"),
        "refs": ref_meshes,
    }
    asm_stl.unlink()
    render_preview(p, plate, meshes, HERE / "preview.png")
    print(f"wrote {HERE / 'preview.png'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
