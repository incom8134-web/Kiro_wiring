"""
USB hub tray for the robot cart's middle floor (parametric, CadQuery).

Holds one ST Lab USB hub (157 x 37 x 40 mm) lying flat with its downstream ports
facing up. Both ends are open (upstream USB on one end, DC input on the other).
Side flanges carry zip-tie slot pairs to tie the tray to the basket mesh.

Run:  python hub_tray.py   ->  out/hub_tray.step, out/hub_tray.3mf
Prints in one piece on a Bambu Lab P1S, flat side down, no supports.
"""
import math
import os
import cadquery as cq

HUB_L, HUB_W, HUB_H = 157.0, 37.0, 40.0
CLR = 1.0                         # clearance per side
WALL, BASE = 3.0, 3.0             # wall and floor thickness
WALL_H = 22.0                     # side wall height above the floor (~half the hub)
END_LIP = 6.0                     # low lip at both ends, stays below the end connectors
FLANGE = 14.0                     # base flange width each side (zip-tie anchors)
CORNER_R = 6.0

ZIP_X = (-60.0, 0.0, 60.0)        # zip-tie pair positions along the tray
ZIP_SLOT_L, ZIP_SLOT_W, ZIP_PITCH = 5.0, 2.4, 8.0

FLOOR_HEX_F, FLOOR_HEX_WEB = 8.0, 2.4  # airflow cut-outs in the floor
SIDE_VENT_L, SIDE_VENT_W, SIDE_VENTS = 18.0, 3.0, 5

IN_L, IN_W = HUB_L + 2 * CLR, HUB_W + 2 * CLR
OUT_L, OUT_W = IN_L + 2 * WALL, IN_W + 2 * WALL
BASE_W = OUT_W + 2 * FLANGE


def slot(x, y, lx, ly, z0, depth):
    return (cq.Workplane("XY").workplane(offset=z0).center(x, y)
            .slot2D(max(lx, ly), min(lx, ly), 0 if lx >= ly else 90).extrude(depth))


def build():
    # base plate with flanges
    t = cq.Workplane("XY").rect(OUT_L, BASE_W).extrude(BASE).edges("|Z").fillet(CORNER_R)
    # walls
    walls = (cq.Workplane("XY").rect(OUT_L, OUT_W).extrude(BASE + WALL_H)
             .edges("|Z").fillet(3.0)
             .cut(cq.Workplane("XY").workplane(offset=BASE).rect(IN_L, IN_W).extrude(WALL_H + 1)
                  .edges("|Z").fillet(1.0)))
    t = t.union(walls)
    # open both ends down to the lip height
    for sx in (-1, 1):
        cut = cq.Workplane("XY").box(WALL + 2, IN_W, WALL_H, centered=(True, True, False)) \
            .translate((sx * (OUT_L / 2 - WALL / 2), 0, BASE + END_LIP))
        t = t.cut(cut)
    # side vents
    pitch = (IN_L - 40) / (SIDE_VENTS - 1)
    for i in range(SIDE_VENTS):
        x = -(IN_L - 40) / 2 + i * pitch
        for sy in (-1, 1):
            v = (cq.Workplane("XZ", origin=(0, sy * (OUT_W / 2 + 1), 0))
                 .center(x, BASE + WALL_H / 2 + 1).slot2D(SIDE_VENT_L, SIDE_VENT_W)
                 .extrude(WALL + 2 if sy > 0 else -(WALL + 2)))
            t = t.cut(v)
    # floor honeycomb
    r = FLOOR_HEX_F / math.sqrt(3)
    fc = FLOOR_HEX_F + FLOOR_HEX_WEB
    dx, dy = 1.5 * fc / math.sqrt(3), fc
    pts, i, x = [], 0, -IN_L / 2 + 8
    while x <= IN_L / 2 - 8:
        y = -IN_W / 2 + 6 + (dy / 2 if i % 2 else 0)
        while y <= IN_W / 2 - 6:
            pts.append((x, y))
            y += dy
        x += dx
        i += 1
    t = t.cut(cq.Workplane("XY").workplane(offset=-1).pushPoints(pts)
              .polygon(6, 2 * r).extrude(BASE + 2))
    # zip-tie slot pairs in both flanges
    fy = OUT_W / 2 + FLANGE / 2
    for x in ZIP_X:
        for sy in (-1, 1):
            for oy in (-ZIP_PITCH / 2, ZIP_PITCH / 2):
                t = t.cut(slot(x, sy * fy + oy, ZIP_SLOT_L, ZIP_SLOT_W, -1, BASE + 2))
    # label
    t = t.cut(cq.Workplane("XY").workplane(offset=BASE - 0.6)
              .text("USB HUB", 5.0, 1.0, kind="bold", halign="center", valign="center")
              .translate((-OUT_L / 2 + 22, -(OUT_W / 2 + FLANGE / 2), 0)))
    return t


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    tray = build()
    cq.exporters.export(tray, f"{out}/hub_tray.step")
    cq.exporters.export(tray, f"{out}/hub_tray.3mf", tolerance=0.02, angularTolerance=0.1)
    b = tray.val().BoundingBox()
    print("hub tray", round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1), "solids", len(tray.solids().vals()))
