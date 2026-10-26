"""
Robot cart - lower tray electronics base plate (parametric, CadQuery).  v3

Run:  python power_plate.py
Out:  step/plate_full.step, print_3mf/plate_full.3mf   (one piece: laser/CNC or big printer)
      step/ + print_3mf/ plate_left / plate_right       (two halves, dovetail joint, fits 256mm bed)
      .step -> open in Fusion 360 (File > Open), .3mf -> slicer

Coordinate system: origin = plate center, X = 330 tray length, Y = 235 tray width,
Z = up, plate bottom at Z=0.  All dims in mm.  Component sizes / hole patterns
marked VERIFY are estimates -> measure real parts and edit.
"""
import os
import cadquery as cq

# ---------------------------------------------------------------- tray / plate
TRAY_L, TRAY_W, TRAY_H, TRAY_FILLET = 330.0, 235.0, 55.0, 40.0
CLEAR = 2.0                       # gap to tray wall, each side
PL_L = TRAY_L - 2 * CLEAR         # 326
PL_W = TRAY_W - 2 * CLEAR         # 231
PL_FILLET = TRAY_FILLET - CLEAR   # corner radius follows tray corner
PL_T = 5.0                        # plate thickness

# ---------------------------------------------------------------- components
# name: (center_x, center_y, size_x, size_y, height, tab_sides, color)
# tab_sides: sides that get locating tabs: "N" (+Y) "S" (-Y) "E" (+X) "W" (-X)
COMPONENTS = {
    # SMPS 12V 350W (HS-350-12, fan on top face): body 193 x 100 x 45 + 2 mm clearance,
    # lies flat with the fan facing up, terminals face +X (toward AC inlet / GND bar)
    "SMPS_12V_350W": (-24.5, 56.0, 197.0, 104.0, 45.0, "", (0.75, 0.75, 0.78)),
    # Jetson Orin Nano Super dev kit, measured 100 x 90 (x 35), I/O edge faces -X
    "JETSON_ORIN_NANO": (-84.75, -58.5, 90.0, 100.0, 35.0, "", (0.15, 0.55, 0.15)),
    # 2x Dorhea 4-way blade fuse box (no negative bus), long axis along Y. VERIFY size
    "FUSE_12V_4WAY": (-3.0, -60.0, 50.0, 105.0, 38.0, "WE", (0.2, 0.2, 0.2)),   # F1 Jetson, F2 wheels, F3 buck
    "FUSE_5V_4WAY": (55.0, -60.0, 50.0, 105.0, 38.0, "WE", (0.2, 0.2, 0.2)),    # F4 leaders, F5 followers
    # TOBSUN EA75-5V 12V->5V 15A buck, ears along Y. VERIFY size
    "BUCK_5V_15A": (120.0, -32.5, 68.0, 85.0, 30.0, "SE", (0.6, 0.1, 0.1)),
}
TAB_LEN, TAB_T, TAB_H, TAB_GAP = 16.0, 3.0, 7.0, 0.6

# ---------------------------------------------------------------- raised mounts (airflow underneath)
STANDOFF_H = 10.0                 # air gap under SMPS and Jetson
RAISED = {"SMPS_12V_350W", "JETSON_ORIN_NANO"}

# Jetson carrier board: 4 bosses, M2.5/M3 self-tap pilot.  VERIFY pattern
JET_HOLES_X, JET_HOLES_Y = 58.0, 86.0     # board rotated: 86 runs along Y
JET_HOLE_OFFSET = (0.0, 0.0)              # pattern center offset from kit center
JET_BOSS_D, JET_PILOT_D = 7.0, 2.6

# SMPS ear mounts: the PSU has 4 screw-on ears (2 per long side) at its base.
# Each ear sits on a 10 mm riser pad with a long M4 slot, so unknown ear spacing still fits.
SMPS_BODY_W = 100.0               # measured body width (ears stick out beyond this)
SMPS_EAR_X = (-54.0, 73.5)        # VERIFY: ear centres along X, relative to SMPS centre
SMPS_EAR_OUT = 5.0                # VERIFY: ear hole distance outside the body edge
SMPS_PAD_LEN, SMPS_PAD_W = 40.0, 12.0
SMPS_EAR_SLOT_LEN, SMPS_EAR_SLOT_W = 30.0, 4.5

# SMPS support rails under the body (also slotted, in case the base has threaded holes)
SMPS_RAIL_PITCH_Y = 50.0          # VERIFY: distance between the two bottom hole rows
SMPS_RAIL_W, SMPS_RAIL_LEN = 14.0, 184.0
SMPS_SLOT_W, SMPS_SLOT_LEN = 4.4, 60.0    # M4 clearance, 2 slots per rail
SMPS_SLOT_X = 55.0                # slot centers at +/- this from SMPS center

# ---------------------------------------------------------------- AC inlet tower
# IEC C14 inlet + fuse + switch, mounted horizontally; inlet lower edge 67 mm above the plate bottom.
AC_Y = 47.0                       # center along +X edge
AC_WALL_W, AC_WALL_T = 60.0, 5.0
AC_INLET_BOTTOM = 67.0            # bottom edge of the inlet cutout, above plate bottom
AC_WALL_TOP = 112.0               # absolute Z of tower top
AC_CUT_W, AC_CUT_H = 47.8, 28.2   # panel cutout (long axis horizontal)
AC_CZ = AC_INLET_BOTTOM + AC_CUT_H / 2   # cutout center Z (~81 mm; mount holes ~61 / ~101 mm)
AC_HOLE_PITCH, AC_HOLE_D = 40.0, 3.4
GUSSET_X, GUSSET_Z, GUSSET_T = 40.0, 90.0, 5.0

# ---------------------------------------------------------------- zip-tie anchors
# (x, y, wire_dir_deg)  -> two 2.4x5 slots straddling the wire bundle
ZIP_ANCHORS = [
    (110.0, 92.0, 90), (110.0, 28.0, 90),      # AC lines inlet -> SMPS
    (82.0, -8.0, 0),                           # 12V SMPS -> fuse boxes
    (-36.0, -35.0, 90), (-36.0, -85.0, 90),    # fuse -> Jetson feed
    (-148.0, -25.0, 90), (-148.0, -75.0, 90),  # Jetson I/O cables
    (120.0, -85.0, 0),                         # 5V out
    (-150.0, 40.0, 90),                        # left riser to upper floors
]
ZIP_SLOT_W, ZIP_SLOT_L, ZIP_PITCH = 2.4, 5.0, 8.0

# ---------------------------------------------------------------- honeycomb (airflow + less filament)
HEX_F = 10.0                      # hole size across flats
HEX_WEB = 2.6                     # rib between holes
HEX_EDGE = 6.0                    # solid border around plate edge
HEX_KEEP = 2.0                    # solid margin around rails, bosses, tabs, tower, labels
SCREW_BAND = 10.0                 # solid strip inside fuse box / buck footprint edge for screws

# ---------------------------------------------------------------- labels (engraved)
LABELS = [  # (text, x, y, rot_deg, size)
    ("AC IN 220V", 140.0, 95.0, 90, 6.0),
    ("12V", 82.0, 4.0, 0, 5.0),
    ("5V OUT", 120.0, -95.0, 0, 5.0),
    ("JETSON I/O", -153.0, -50.0, 90, 5.0),
]
ENGRAVE = 0.8

# ---------------------------------------------------------------- split for printing
SPLIT_X = -45.0
DOVETAILS_Y = [-70.0, 0.0, 70.0]
DT_NECK, DT_HEAD, DT_DEPTH, DT_CLEAR = 10.0, 16.0, 9.0, 0.15


def rounded_outline(l, w, r, h):
    return cq.Workplane("XY").rect(l, w).extrude(h).edges("|Z").fillet(r)


def slot(x, y, lx, ly, depth=PL_T + 2, z0=-1):
    return (cq.Workplane("XY").workplane(offset=z0).center(x, y)
            .slot2D(max(lx, ly), min(lx, ly), 0 if lx >= ly else 90).extrude(depth))


def tabs(p):
    for cx, cy, sx, sy, _, sides, _ in COMPONENTS.values():
        for s in sides:
            if s in "NS":
                ty = cy + (1 if s == "N" else -1) * (sy / 2 + TAB_GAP + TAB_T / 2)
                tab = cq.Workplane("XY").box(TAB_LEN, TAB_T, TAB_H, centered=(True, True, False)) \
                    .translate((cx, ty, PL_T))
            else:
                tx = cx + (1 if s == "E" else -1) * (sx / 2 + TAB_GAP + TAB_T / 2)
                tab = cq.Workplane("XY").box(TAB_T, TAB_LEN, TAB_H, centered=(True, True, False)) \
                    .translate((tx, cy, PL_T))
            p = p.union(tab.edges("|Z").fillet(1.0))
    return p


def jetson_mounts(p):
    cx, cy = COMPONENTS["JETSON_ORIN_NANO"][:2]
    ox, oy = cx + JET_HOLE_OFFSET[0], cy + JET_HOLE_OFFSET[1]
    pts = [(ox + sx * JET_HOLES_X / 2, oy + sy * JET_HOLES_Y / 2) for sx in (-1, 1) for sy in (-1, 1)]
    bosses = (cq.Workplane("XY").workplane(offset=PL_T).pushPoints(pts)
              .circle(JET_BOSS_D / 2).extrude(STANDOFF_H))
    p = p.union(bosses)
    pilots = (cq.Workplane("XY").workplane(offset=-1).pushPoints(pts)
              .circle(JET_PILOT_D / 2).extrude(PL_T + STANDOFF_H + 2))
    return p.cut(pilots)


def smps_ear_pads():
    """(x, y, len_x, len_y) of the four ear riser pads, clipped to the plate edge."""
    cx, cy = COMPONENTS["SMPS_12V_350W"][:2]
    lim = PL_W / 2 - 1.5
    pads = []
    for sy in (-1, 1):
        hole_y = cy + sy * (SMPS_BODY_W / 2 + SMPS_EAR_OUT)
        y0, y1 = hole_y - SMPS_PAD_W / 2, hole_y + SMPS_PAD_W / 2
        y0, y1 = max(y0, -lim), min(y1, lim)
        for ex in SMPS_EAR_X:
            pads.append((cx + ex, (y0 + y1) / 2, SMPS_PAD_LEN, y1 - y0, hole_y))
    return pads


def smps_mounts(p):
    for x, y, lx, ly, hole_y in smps_ear_pads():
        pad = cq.Workplane("XY").box(lx, ly, STANDOFF_H, centered=(True, True, False)) \
            .translate((x, y, PL_T)).edges("|Z").fillet(2.0)
        p = p.union(pad)
        p = p.cut(slot(x, hole_y, SMPS_EAR_SLOT_LEN, SMPS_EAR_SLOT_W, PL_T + STANDOFF_H + 2))
    cx, cy = COMPONENTS["SMPS_12V_350W"][:2]
    for sy in (-1, 1):
        ry = cy + sy * SMPS_RAIL_PITCH_Y / 2
        rail = cq.Workplane("XY").box(SMPS_RAIL_LEN, SMPS_RAIL_W, STANDOFF_H, centered=(True, True, False)) \
            .translate((cx, ry, PL_T)).edges("|Z").fillet(3.0)
        p = p.union(rail)
        for sx in (-1, 1):
            p = p.cut(slot(cx + sx * SMPS_SLOT_X, ry, SMPS_SLOT_LEN, SMPS_SLOT_W, PL_T + STANDOFF_H + 2))
    return p


def ac_tower(p):
    x_in = PL_L / 2 - AC_WALL_T          # inner face of wall
    wall = cq.Workplane("XY").box(AC_WALL_T, AC_WALL_W, AC_WALL_TOP, centered=(True, True, False)) \
        .translate((PL_L / 2 - AC_WALL_T / 2, AC_Y, 0))
    for gy in (AC_Y - AC_WALL_W / 2 + GUSSET_T / 2, AC_Y + AC_WALL_W / 2 - GUSSET_T / 2):
        g = (cq.Workplane("XZ", origin=(0, gy + GUSSET_T / 2, 0))
             .polyline([(x_in, PL_T), (x_in - GUSSET_X, PL_T), (x_in, PL_T + GUSSET_Z)])
             .close().extrude(GUSSET_T))
        wall = wall.union(g)
    wall = wall.edges("|Y").edges(">Z").fillet(2.0)
    cut = cq.Workplane("YZ").workplane(offset=x_in - 1) \
        .center(AC_Y, AC_CZ).rect(AC_CUT_W, AC_CUT_H).extrude(AC_WALL_T + 2)
    holes = cq.Workplane("YZ").workplane(offset=x_in - 1) \
        .pushPoints([(AC_Y, AC_CZ - AC_HOLE_PITCH / 2), (AC_Y, AC_CZ + AC_HOLE_PITCH / 2)]) \
        .circle(AC_HOLE_D / 2).extrude(AC_WALL_T + 2)
    return p.union(wall).cut(cut).cut(holes)


def _keepouts():
    """Rectangles (x0, y0, x1, y1), circles (x, y, r) and screw bands that must stay solid."""
    rects, circles = [], []
    k = HEX_KEEP
    for cx, cy, sx, sy, _, sides, _ in COMPONENTS.values():      # tabs
        for s in sides:
            if s in "NS":
                ty = cy + (1 if s == "N" else -1) * (sy / 2 + TAB_GAP + TAB_T / 2)
                rects.append((cx - TAB_LEN / 2 - k, ty - TAB_T / 2 - k, cx + TAB_LEN / 2 + k, ty + TAB_T / 2 + k))
            else:
                tx = cx + (1 if s == "E" else -1) * (sx / 2 + TAB_GAP + TAB_T / 2)
                rects.append((tx - TAB_T / 2 - k, cy - TAB_LEN / 2 - k, tx + TAB_T / 2 + k, cy + TAB_LEN / 2 + k))
    for x, y, lx, ly, _ in smps_ear_pads():                        # SMPS ear pads
        rects.append((x - lx / 2 - k, y - ly / 2 - k, x + lx / 2 + k, y + ly / 2 + k))
    cx, cy = COMPONENTS["SMPS_12V_350W"][:2]                      # SMPS rails
    for sy in (-1, 1):
        ry = cy + sy * SMPS_RAIL_PITCH_Y / 2
        rects.append((cx - SMPS_RAIL_LEN / 2 - k, ry - SMPS_RAIL_W / 2 - k,
                      cx + SMPS_RAIL_LEN / 2 + k, ry + SMPS_RAIL_W / 2 + k))
    cx, cy = COMPONENTS["JETSON_ORIN_NANO"][:2]                   # Jetson bosses
    ox, oy = cx + JET_HOLE_OFFSET[0], cy + JET_HOLE_OFFSET[1]
    for sx in (-1, 1):
        for sy in (-1, 1):
            circles.append((ox + sx * JET_HOLES_X / 2, oy + sy * JET_HOLES_Y / 2, JET_BOSS_D / 2 + k + 2))
    rects.append((PL_L / 2 - AC_WALL_T - GUSSET_X - k, AC_Y - AC_WALL_W / 2 - k,   # AC tower
                  PL_L / 2, AC_Y + AC_WALL_W / 2 + k))
    for x, y, _ in ZIP_ANCHORS:                                   # zip-tie anchors
        circles.append((x, y, ZIP_PITCH / 2 + ZIP_SLOT_L / 2 + k))
    for txt, x, y, rot, size in LABELS:                           # labels
        hl, hh = len(txt) * size * 0.4 + k, size * 0.7 + k
        if rot % 180:
            hl, hh = hh, hl
        rects.append((x - hl, y - hh, x + hl, y + hh))
    rects.append((SPLIT_X - DT_DEPTH - 6, -PL_W, SPLIT_X + 6, PL_W))  # split joint band
    bands = []                                                    # fuse / buck screw zones
    for name in ("FUSE_12V_4WAY", "FUSE_5V_4WAY", "BUCK_5V_15A"):
        cx, cy, sx, sy = COMPONENTS[name][:4]
        bands.append((cx, cy, sx / 2, sy / 2))
    return rects, circles, bands


def honeycomb():
    """Hex through-holes over the free plate area."""
    import math
    rects, circles, bands = _keepouts()
    r_hole = HEX_F / math.sqrt(3)                  # circumradius of hole
    fc = HEX_F + HEX_WEB                           # cell across flats
    dx, dy = 1.5 * fc / math.sqrt(3), fc           # flat-top hex tiling
    hl, hw, rr = PL_L / 2 - HEX_EDGE, PL_W / 2 - HEX_EDGE, max(PL_FILLET - HEX_EDGE, 0.1)

    def inside_plate(x, y, m):
        ax, ay = abs(x), abs(y)
        if ax > hl - m or ay > hw - m:
            return False
        qx, qy = ax - (hl - rr), ay - (hw - rr)
        return not (qx > 0 and qy > 0 and math.hypot(qx, qy) > rr - m)

    def blocked(x, y):
        r = r_hole
        for x0, y0, x1, y1 in rects:
            if x0 - r < x < x1 + r and y0 - r < y < y1 + r:
                return True
        for cx, cy, cr in circles:
            if math.hypot(x - cx, y - cy) < cr + r:
                return True
        for cx, cy, hx, hy in bands:   # near footprint edge -> keep solid for screws
            ax, ay = abs(x - cx), abs(y - cy)
            near = ax < hx + 2 + r and ay < hy + 2 + r
            deep = ax < hx - SCREW_BAND - r and ay < hy - SCREW_BAND - r
            if near and not deep:
                return True
        return False

    pts, i, x = [], 0, -PL_L / 2
    while x <= PL_L / 2:
        y = -PL_W / 2 + (dy / 2 if i % 2 else 0)
        while y <= PL_W / 2:
            if inside_plate(x, y, r_hole) and not blocked(x, y):
                pts.append((x, y))
            y += dy
        x += dx
        i += 1
    print("honeycomb holes:", len(pts))
    return (cq.Workplane("XY").workplane(offset=-1).pushPoints(pts)
            .polygon(6, 2 * r_hole).extrude(PL_T + 2))


def build_plate():
    p = rounded_outline(PL_L, PL_W, PL_FILLET, PL_T)
    p = tabs(p)
    p = jetson_mounts(p)
    p = smps_mounts(p)
    p = ac_tower(p)

    p = p.cut(honeycomb())

    for x, y, d in ZIP_ANCHORS:
        off = ZIP_PITCH / 2
        if d == 0:   # wire runs along X -> slots offset in Y
            pts, lx, ly = [(x, y - off), (x, y + off)], ZIP_SLOT_W, ZIP_SLOT_L
        else:
            pts, lx, ly = [(x - off, y), (x + off, y)], ZIP_SLOT_L, ZIP_SLOT_W
        for px, py in pts:
            p = p.cut(slot(px, py, lx, ly))

    for txt, x, y, rot, size in LABELS:
        t = (cq.Workplane("XY").workplane(offset=PL_T - ENGRAVE)
             .text(txt, size, ENGRAVE + 1, kind="bold", halign="center", valign="center")
             .rotate((0, 0, 0), (0, 0, 1), rot).translate((x, y, 0)))
        p = p.cut(t)
    return p


def split_region(clear=0.0):
    """Polygon covering the LEFT half incl. dovetail sockets (tongues belong to right half)."""
    hw = PL_W / 2 + 5
    x0 = -PL_L / 2 - 5
    pts = [(x0, -hw), (SPLIT_X - clear, -hw)]
    for y in DOVETAILS_Y:   # tongue of right half pokes into left (-X)
        n, h, d = DT_NECK / 2 + clear, DT_HEAD / 2 + clear, DT_DEPTH + clear
        pts += [(SPLIT_X - clear, y - n), (SPLIT_X - d, y - h),
                (SPLIT_X - d, y + h), (SPLIT_X - clear, y + n)]
    pts += [(SPLIT_X - clear, hw), (x0, hw)]
    return cq.Workplane("XY").workplane(offset=-1).polyline(pts).close().extrude(AC_WALL_TOP + 5)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    step_dir, print_dir = os.path.join(here, "step"), os.path.join(here, "print_3mf")
    os.makedirs(step_dir, exist_ok=True)
    os.makedirs(print_dir, exist_ok=True)
    plate = build_plate()
    left = plate.intersect(split_region(0.0))
    right = plate.cut(split_region(DT_CLEAR))
    for nm, part in (("full", plate), ("left", left), ("right", right)):
        cq.exporters.export(part, f"{step_dir}/plate_{nm}.step")            # Fusion 360: File > Open
        cq.exporters.export(part, f"{print_dir}/plate_{nm}.3mf", tolerance=0.02, angularTolerance=0.1)
        b = part.val().BoundingBox()
        print(nm, round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1), "solids", len(part.solids().vals()))
