#!/usr/bin/env python3
"""Printable case for the Matek I2C-INA-BM module.

The board outline is the Matek published size, 27 x 20 x 6 mm:
https://www.mateksys.com/?portfolio=i2c-ina-bm

The shunt is the module's own conductive path, so this case has no
external shunt plate. Open-top slots take the two power leads and the
two JST-GH plugs. The slots are open at the top so the print needs no
supports. Mounting tabs are on the case, not through the PCB.

Connector positions are taken from the product photo, not from a
dimensioned drawing. The retailer claim of a 3 mm PCB hole is not on
mateksys.com and is not used. The power-lead opening is a printable
default; the pack current is still unknown, so no wire gauge is chosen.

Run from this directory:

    python3 enclosure.py

Writes STEP and STL for the base and the lid, an assembly STEP, a
preview PNG, and export/dimensions.json. Dimensions are millimetres.
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

# Matek I2C-INA-BM. Board size is on the product page. The 6 mm figure is
# the module height Matek publishes, not a measured solder-side height.
# https://www.mateksys.com/?portfolio=i2c-ina-bm
BOARD_X = 27.0
BOARD_Y = 20.0
BOARD_Z = 6.0

WALL = 2.2
FLOOR = 1.8
LID_T = 1.8
FIT = 1.2
STANDOFF = 1.2  # keeps the bottom dead pad off the floor (Matek: bottom pad is dead)
AIR = 1.0
TAB_LEN = 8.0
TAB_W = 10.0
M3_CLEAR = 3.4  # ISO 273 medium
SKIRT_H = 2.4
SKIRT_T = 1.4
LID_GAP = 0.05
RIB_H = 2.0

# UNVERIFIED. Not on the Matek drawing. The product photo shows two
# JST-GH plugs along one long edge and the power pads on the short edges.
JST_W = 11.0
JST_GAP = 3.0
WIRE_W = 6.0
SLOT_Z0_ABOVE_FLOOR = 2.2


def _r3(value: float) -> float:
    return round(float(value), 3)


def compute() -> dict:
    inner_x = BOARD_X + 2.0 * FIT
    inner_y = BOARD_Y + 2.0 * FIT
    outer_x = inner_x + 2.0 * WALL
    outer_y = inner_y + 2.0 * WALL
    cavity_h = STANDOFF + BOARD_Z + AIR
    base_h = FLOOR + cavity_h
    board_x0 = WALL + FIT
    board_y0 = WALL + FIT
    span = 2.0 * JST_W + JST_GAP
    jst0 = WALL + (inner_x - span) / 2.0
    return {
        "inner_x": inner_x,
        "inner_y": inner_y,
        "outer_x": outer_x,
        "outer_y": outer_y,
        "cavity_h": cavity_h,
        "base_h": base_h,
        "board_x0": board_x0,
        "board_y0": board_y0,
        "slot_z0": FLOOR + SLOT_Z0_ABOVE_FLOOR,
        "wire_y0": WALL + (inner_y - WIRE_W) / 2.0,
        "jst_x": (jst0, jst0 + JST_W + JST_GAP),
        "tab_y0": outer_y - TAB_W,
        "with_tabs_x": outer_x + 2.0 * TAB_LEN,
    }


def _box(x: float, y: float, z: float, dx: float, dy: float, dz: float) -> cq.Workplane:
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x, y, z))


def _hole(x: float, y: float, z0: float, z1: float, diameter: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center(x, y)
        .circle(diameter / 2.0)
        .extrude(z1 - z0)
    )


def build_base(p: dict) -> cq.Workplane:
    ox, oy, bh = p["outer_x"], p["outer_y"], p["base_h"]
    solid = _box(0, 0, 0, ox, oy, bh)
    solid = solid.union(_box(-TAB_LEN, p["tab_y0"], 0, TAB_LEN, TAB_W, FLOOR + 1.2))
    solid = solid.union(_box(ox, p["tab_y0"], 0, TAB_LEN, TAB_W, FLOOR + 1.2))
    solid = solid.cut(_box(WALL, WALL, FLOOR, p["inner_x"], p["inner_y"], bh))
    solid = solid.cut(_box(-0.2, p["wire_y0"], p["slot_z0"], WALL + 0.4, WIRE_W, bh))
    solid = solid.cut(_box(ox - WALL - 0.2, p["wire_y0"], p["slot_z0"], WALL + 0.4, WIRE_W, bh))
    for x0 in p["jst_x"]:
        solid = solid.cut(_box(x0, -0.2, p["slot_z0"], JST_W, WALL + 0.4, bh))
    solid = solid.cut(_hole(-TAB_LEN / 2.0, p["tab_y0"] + TAB_W / 2.0, -0.2, FLOOR + 1.6, M3_CLEAR))
    solid = solid.cut(_hole(ox + TAB_LEN / 2.0, p["tab_y0"] + TAB_W / 2.0, -0.2, FLOOR + 1.6, M3_CLEAR))
    # Floor vents over the on-board shunt. Three slots, ribs left between them.
    cx = WALL + p["inner_x"] / 2.0
    cy = WALL + p["inner_y"] / 2.0
    for dx in (-6.0, 0.0, 6.0):
        solid = solid.cut(_box(cx + dx - 1.1, cy - 6.0, -0.2, 2.2, 12.0, FLOOR + 0.4))
    # Corner locators and pads. The pads stay off the center dead pad.
    rib_top = FLOOR + STANDOFF + RIB_H
    for sx in (0.0, 1.0):
        for sy in (0.0, 1.0):
            rx = WALL + sx * (p["inner_x"] - 1.0)
            ry = WALL + sy * (p["inner_y"] - 1.0)
            solid = solid.union(_box(rx, ry, FLOOR - 0.01, 1.0, 1.0, rib_top - FLOOR + 0.01))
            px = p["board_x0"] + sx * (BOARD_X - 3.2) + (0.6 if sx == 0 else 0.0)
            py = p["board_y0"] + sy * (BOARD_Y - 3.2) + (0.6 if sy == 0 else 0.0)
            solid = solid.union(_box(px, py, FLOOR - 0.01, 2.6, 2.6, STANDOFF + 0.01))
    return solid


def build_lid(p: dict) -> cq.Workplane:
    ox, oy = p["outer_x"], p["outer_y"]
    z0 = p["base_h"] + LID_GAP
    lid = _box(0, 0, z0, ox, oy, LID_T)
    skirt = _box(WALL + 0.25, WALL + 0.25, z0 - SKIRT_H, p["inner_x"] - 0.5, p["inner_y"] - 0.5, SKIRT_H)
    skirt = skirt.cut(
        _box(
            WALL + 0.25 + SKIRT_T,
            WALL + 0.25 + SKIRT_T,
            z0 - SKIRT_H - 0.1,
            p["inner_x"] - 0.5 - 2.0 * SKIRT_T,
            p["inner_y"] - 0.5 - 2.0 * SKIRT_T,
            SKIRT_H + 0.2,
        )
    )
    lid = lid.union(skirt)
    lid = lid.cut(_box(-0.2, p["wire_y0"], p["slot_z0"], WALL + 0.6, WIRE_W, LID_T + SKIRT_H + 2.0))
    lid = lid.cut(_box(ox - WALL - 0.4, p["wire_y0"], p["slot_z0"], WALL + 0.6, WIRE_W, LID_T + SKIRT_H + 2.0))
    for x0 in p["jst_x"]:
        lid = lid.cut(_box(x0, -0.2, p["slot_z0"], JST_W, WALL + 0.6, LID_T + SKIRT_H + 2.0))
    cx = WALL + p["inner_x"] / 2.0
    cy = WALL + p["inner_y"] / 2.0
    for dx in (-6.0, 0.0, 6.0):
        lid = lid.cut(_box(cx + dx - 1.1, cy - 5.0, z0 - 0.2, 2.2, 10.0, LID_T + 0.4))
    return lid


def lid_to_print(lid: cq.Workplane) -> cq.Workplane:
    bb = lid.val().BoundingBox()
    flipped = lid.rotate((0, 0, 0), (1, 0, 0), 180)
    bb2 = flipped.val().BoundingBox()
    return flipped.translate((-bb2.xmin, -bb2.ymin, -bb2.zmin))


def board_reference(p: dict) -> cq.Workplane:
    return _box(p["board_x0"], p["board_y0"], FLOOR + STANDOFF, BOARD_X, BOARD_Y, BOARD_Z)


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


def render_preview(p: dict, meshes: dict, path: Path) -> None:
    fig = plt.figure(figsize=(12.4, 5.6), dpi=130)
    span_x = p["with_tabs_x"]
    span_y = p["outer_y"]
    for panel, (title, lift) in enumerate((("Matek module case", 0.0), ("Lid lifted", 14.0)), start=1):
        ax = fig.add_subplot(1, 2, panel, projection="3d")
        lid = meshes["lid"].copy()
        lid.apply_translation((0, 0, lift))
        layers = [
            (_decimate(meshes["base"], 8000), (0.62, 0.66, 0.70), 0.92),
            (_decimate(meshes["board"], 1500), (0.72, 0.45, 0.18), 0.85),
            (_decimate(lid, 4000), (0.18, 0.42, 0.58), 0.55),
        ]
        _paint_sorted(ax, layers)
        ax.set_xlim(-TAB_LEN - 2, p["outer_x"] + TAB_LEN + 2)
        ax.set_ylim(-2, span_y + 2)
        ax.set_zlim(0, p["base_h"] + LID_T + lift + 2)
        ax.set_box_aspect((span_x, span_y, p["base_h"] + 8))
        ax.set_title(title)
        ax.view_init(elev=28, azim=-58)
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _public_dimensions(p: dict, reports: list[dict]) -> dict:
    return {
        "units": "mm",
        "module": "Matek I2C-INA-BM",
        "source": "https://www.mateksys.com/?portfolio=i2c-ina-bm",
        "board_mm": [BOARD_X, BOARD_Y, BOARD_Z],
        "body_mm": [_r3(p["outer_x"]), _r3(p["outer_y"]), _r3(p["base_h"] + LID_T)],
        "base_with_tabs_mm": [_r3(p["with_tabs_x"]), _r3(p["outer_y"]), _r3(p["base_h"])],
        "cavity_mm": [_r3(p["inner_x"]), _r3(p["inner_y"]), _r3(p["cavity_h"])],
        "wall_mm": WALL,
        "floor_mm": FLOOR,
        "lid_mm": LID_T,
        "fit_per_side_mm": FIT,
        "standoff_mm": STANDOFF,
        "openings": {
            "power_slot_mm": [WIRE_W, "open top, both short walls"],
            "jst_gh_slots": 2,
            "jst_slot_width_mm": JST_W,
            "note": "JST positions follow the product photo. Power-lead width is a printable default, not a chosen wire gauge.",
        },
        "mesh_extents_mm": {r["file"]: r["extents_mm"] for r in reports},
        "unverified": [
            "JST-GH positions and housing size (photo, not a dimensioned drawing)",
            "power lead outside diameter (pack current is unknown)",
            "solder-side height under the published 6 mm module height",
            "3 mm PCB hole claimed by a retailer and not used here",
        ],
    }


def main() -> int:
    EXPORT.mkdir(parents=True, exist_ok=True)
    for stale in ("shunt_base.step", "shunt_base.stl"):
        path = EXPORT / stale
        if path.exists():
            path.unlink()
    p = compute()
    print(
        f"body {p['outer_x']:.2f} x {p['outer_y']:.2f} x {p['base_h'] + LID_T:.2f} mm, "
        f"with tabs {p['with_tabs_x']:.2f} x {p['outer_y']:.2f} x {p['base_h']:.2f}, "
        f"cavity {p['inner_x']:.2f} x {p['inner_y']:.2f} x {p['cavity_h']:.2f}"
    )
    base = build_base(p)
    _require_single_valid_solid(base, "base")
    lid = build_lid(p)
    _require_single_valid_solid(lid, "lid")
    lid_print = lid_to_print(lid)
    board = board_reference(p)
    overlap = _interference(base, lid)
    print(f"intersection mm^3  base/lid {overlap:.3f}")
    if overlap > 5.0:
        raise SystemExit("printed solids intersect")

    _export_solid(base, EXPORT / "base")
    _export_solid(lid_print, EXPORT / "lid")
    assembly = cq.Assembly(name="matek_i2c_ina_bm")
    assembly.add(base, name="base", color=cq.Color(0.62, 0.66, 0.70, 1))
    assembly.add(lid, name="lid", color=cq.Color(0.18, 0.42, 0.58, 1))
    assembly.add(board, name="REF_module", color=cq.Color(0.72, 0.45, 0.18, 0.45))
    assembly.export(str(EXPORT / "assembly.step"), "STEP")

    for stem in ("base", "lid"):
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
    base_ext = reports[0]["extents_mm"]
    lid_ext = reports[1]["extents_mm"]
    expect_base = [_r3(p["with_tabs_x"]), _r3(p["outer_y"]), _r3(p["base_h"])]
    expect_lid = [_r3(p["outer_x"]), _r3(p["outer_y"]), _r3(LID_T + SKIRT_H)]
    if base_ext != expect_base:
        raise SystemExit(f"base extents {base_ext} != {expect_base}")
    if lid_ext != expect_lid:
        raise SystemExit(f"lid extents {lid_ext} != {expect_lid}")

    (EXPORT / "dimensions.json").write_text(json.dumps(_public_dimensions(p, reports), indent=2) + "\n")
    (EXPORT / "manifold.txt").write_text(
        "\n".join(
            f"{r['file']}: watertight={r['watertight']} winding={r['winding_consistent']} "
            f"volume_mm3={r['volume_mm3']} extents_mm={r['extents_mm']}"
            for r in reports
        )
        + "\n"
    )
    board_stl = EXPORT / "_board.stl"
    lid_stl = EXPORT / "_lid_assembly.stl"
    cq.exporters.export(board, str(board_stl), tolerance=0.15, angularTolerance=0.2)
    cq.exporters.export(lid, str(lid_stl), tolerance=0.15, angularTolerance=0.2)
    meshes = {
        "base": trimesh.load(EXPORT / "base.stl", force="mesh"),
        "lid": trimesh.load(lid_stl, force="mesh"),
        "board": trimesh.load(board_stl, force="mesh"),
    }
    board_stl.unlink()
    lid_stl.unlink()
    render_preview(p, meshes, HERE / "preview.png")
    print(f"wrote {HERE / 'preview.png'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
