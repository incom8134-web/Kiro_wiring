"""
Update KIRO_power_plate.blend (v2 scene) to the v3 hardware layout.

Run headless:
  blender -b blender/archive/KIRO_power_plate_v2_original.blend \
          --python blender/update_blend_v3.py -- <repo_root>

What it does
  * replaces the v2 plate mesh with the v3 plate (cad/assembly/kiro_power_tray.obj)
  * refits PSU1 to the real HS-350-12 (193 x 100 x 45, fan on top) lying flat on
    the slotted ear pads, adds the 4 mounting ears and the top fan grille
  * shifts the Jetson and both fuse boxes 3 mm (v3 positions)
  * lowers the AC inlet so its lower edge is 67 mm above the plate bottom
  * moves every wire point / crimp / zip tie with the part it belongs to
  * adds the USB hub tray + a detailed ST Lab hub (middle-floor part, shown behind the plate)
  * no ground bus bar: returns stay on PSU1 COM / U1 OUT- as in the v2 scene
  * saves blender/KIRO_power_plate.blend and renders every camera to blender/renders/
"""
import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = sys.argv[sys.argv.index("--") + 1]
OBJ = os.path.join(ROOT, "cad", "assembly", "kiro_power_tray.obj")
OUT_BLEND = os.path.join(ROOT, "blender", "KIRO_power_plate.blend")
RENDER_DIR = os.path.join(ROOT, "blender", "renders")

# ------------------------------------------------------------------ v2 -> v3 geometry maps
OLD_X0, OLD_X1, NEW_X0, NEW_X1 = -125.0, 75.0, -121.0, 72.0      # SMPS length 200 -> 193
OLD_Z0, OLD_Z1, NEW_Z0, NEW_Z1 = 25.0, 67.0, 15.0, 60.0          # SMPS base 25 -> 15, 42 -> 45 tall
SX = (NEW_X1 - NEW_X0) / (OLD_X1 - OLD_X0)
SZ = (NEW_Z1 - NEW_Z0) / (OLD_Z1 - OLD_Z0)
INLET_OLD_CZ, INLET_NEW_CZ = 132.6, 67.0 + 28.2 / 2              # inlet lower edge at 67 mm
DZ_INLET = INLET_NEW_CZ - INLET_OLD_CZ
DY_SHIFT = -3.0                                                  # Jetson + fuse boxes


def map_psu(p):
    return Vector((NEW_X0 + (p.x - OLD_X0) * SX, p.y, NEW_Z0 + (p.z - OLD_Z0) * SZ))


def map_point(p):
    """Move a free point (wire control point, crimp, zip tie) with the part it sits on."""
    p = Vector(p)
    if p.x > 115.0:                                   # AC tower / inlet zone: blend down
        f = min(max((p.z - 60.0) / 60.0, 0.0), 1.0)
        return Vector((p.x, p.y, p.z + DZ_INLET * f))
    if -130.0 <= p.x <= 90.0 and 0.0 <= p.y <= 112.0 and p.z > 30.0:
        return map_psu(p)                             # on / above the SMPS
    if -160.0 <= p.x <= -36.0 and -112.0 <= p.y <= -8.0 and p.z > 10.0:
        return p + Vector((0, DY_SHIFT, 0))           # Jetson
    if (-30.0 <= p.x <= 26.0 or 27.0 <= p.x <= 82.0) and -112.0 <= p.y <= -8.0 and p.z > 10.0:
        return p + Vector((0, DY_SHIFT, 0))           # fuse boxes
    return p


def coll_objects(name):
    c = bpy.data.collections.get(name)
    return list(c.objects) if c else []


def material(name, rgb=None, metal=0.0, rough=0.5):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf and rgb:
            bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
            bsdf.inputs["Metallic"].default_value = metal
            bsdf.inputs["Roughness"].default_value = rough
    return m


def add_box(name, size, loc, mat, coll):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    move_to(o, coll)
    return o


def add_cyl(name, r, h, loc, mat, coll, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(mat)
    move_to(o, coll)
    return o


def add_text(name, body, size, loc, mat, coll, rot=(0, 0, 0)):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.data.body = body
    o.data.size = size
    o.data.extrude = 0.15
    o.data.align_x = "CENTER"
    o.data.align_y = "CENTER"
    o.data.materials.append(mat)
    move_to(o, coll)
    return o


def move_to(o, coll):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    coll.objects.link(o)


def new_coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    return c


scene = bpy.context.scene

# ------------------------------------------------------------------ 1. plate + hub tray meshes
old = bpy.data.objects.get("Cart_power_plate_v2")
plate_mat = old.data.materials[0] if old else material("PLA_plate", (0.92, 0.92, 0.92))
plate_coll = old.users_collection[0] if old else new_coll("Plate")
if old:
    bpy.data.objects.remove(old, do_unlink=True)
before = set(bpy.data.objects)
bpy.ops.wm.obj_import(filepath=OBJ, forward_axis="Y", up_axis="Z", global_scale=1.0)
imported = [o for o in bpy.data.objects if o not in before]
hub_coll = new_coll("H1_USB_hub_middle_floor")
tray = None
for o in imported:
    o.data.materials.clear()
    if "tray" in o.name.lower():
        tray = o
        o.name = "H1_tray_printed"
        o.data.materials.append(material("PLA_tray_beige", (0.80, 0.66, 0.50), rough=0.6))
        move_to(o, hub_coll)
    else:
        o.name = "Cart_power_plate_v3"
        o.data.materials.append(plate_mat)
        move_to(o, plate_coll)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_auto_smooth() if hasattr(bpy.ops.object, "shade_auto_smooth") else None
    o.select_set(False)

# ------------------------------------------------------------------ 2. SMPS refit
psu = new_coll("PSU1_SMPS_12V")
for o in coll_objects("PSU1_SMPS_12V"):
    if o.name.startswith("SMPS_spacer_"):
        bpy.data.objects.remove(o, do_unlink=True)
        continue
    if o.name.startswith("SMPS_bolt_"):
        continue                                    # re-placed on the ears below
    o.location = map_psu(o.location)
    if o.type == "MESH" and not o.name.endswith(("_x1", "_x2")) and "_T" not in o.name:
        o.scale.x *= SX
        o.scale.z *= SZ
# label + sticker away from the fan (fan sits at the -X end, opposite the terminals)
for n, x in (("SMPS_label", -15.0), ("SMPS_txt1", -15.0), ("SMPS_txt2", -15.0), ("SMPS_txt3", -15.0),
             ("SMPS_warning", 35.0)):
    o = bpy.data.objects.get(n)
    if o:
        o.location.x = x
for n in ("SMPS_txt1",):
    o = bpy.data.objects.get(n)
    if o and o.type == "FONT":
        o.data.body = "12V  29A  350W"
for n in ("SMPS_txt2",):
    o = bpy.data.objects.get(n)
    if o and o.type == "FONT":
        o.data.body = "HS-350-12   AC 220V / DC 12V"

zinc = bpy.data.materials.get("zinc") or material("zinc", (0.75, 0.76, 0.78), 0.9, 0.35)
black = bpy.data.materials.get("black_matte") or material("black_matte", (0.02, 0.02, 0.02))
cx, cy = (NEW_X0 + NEW_X1) / 2, 56.0
top_z = NEW_Z1
# mounting ears (2 per long side) + bolts through the slotted plate pads
ear_x = (cx - 54.0, cx + 73.5)
bolts = sorted([o for o in coll_objects("PSU1_SMPS_12V") if o.name.startswith("SMPS_bolt_")], key=lambda o: o.name)
i = 0
for sy in (-1, 1):
    edge = cy + sy * 50.0
    hole = cy + sy * 55.0
    for ex in ear_x:
        add_box(f"SMPS_ear_{'S' if sy < 0 else 'N'}{int(ex)}", (16, 11, 1.5), (ex, edge + sy * 5.5, NEW_Z0 + 0.75), zinc, psu)
        add_box(f"SMPS_ear_{'S' if sy < 0 else 'N'}{int(ex)}_up", (16, 1.5, 14), (ex, edge + sy * 0.75, NEW_Z0 + 7), zinc, psu)
        if i < len(bolts):
            b = bolts[i]
            b.location = Vector((ex, hole, NEW_Z0 + 1.5 + 0.3))
            b.name = f"SMPS_ear_bolt_{i}"
        i += 1
# top fan grille, near the -X end
fx = NEW_X0 + 38.0
add_cyl("SMPS_fan_opening", 27.0, 0.4, (fx, cy, top_z + 0.1), black, psu, verts=64)
for k, r in enumerate((26.0, 19.0, 12.0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.9, location=(fx, cy, top_z + 0.6))
    t = bpy.context.active_object
    t.name = f"SMPS_fan_ring{k}"
    t.data.materials.append(zinc)
    move_to(t, psu)
for k in range(4):
    a = k * math.pi / 2 + math.pi / 4
    add_box(f"SMPS_fan_spoke{k}", (52, 1.6, 1.0), (fx, cy, top_z + 0.6), zinc, psu).rotation_euler.z = a
add_cyl("SMPS_fan_hub", 7.0, 1.6, (fx, cy, top_z + 0.8), black, psu)
for k in range(7):
    a = k * 2 * math.pi / 7
    add_box(f"SMPS_fan_blade{k}", (16, 6, 0.6), (fx + 14 * math.cos(a), cy + 14 * math.sin(a), top_z - 1.0),
            black, psu).rotation_euler = (0.35, 0, a + math.pi / 2)
for k, dx in enumerate((-8.0, 0.0, 8.0)):
    add_box(f"SMPS_vent_slot{k}", (2.5, 36, 0.3), (NEW_X1 - 30 + dx, cy, top_z + 0.15), black, psu)

# ------------------------------------------------------------------ 3. Jetson + fuse boxes + inlet
for name in ("U2_Jetson_Orin_Nano_Super", "FB1_Fuse_box", "FB2_Fuse_box"):
    for o in coll_objects(name):
        o.location.y += DY_SHIFT
for o in coll_objects("J1_AC_inlet"):
    o.location.z += DZ_INLET

# ------------------------------------------------------------------ 4. wires, crimps, zip ties, cord
for cname in ("Wiring", "AC_cord"):
    for o in coll_objects(cname):
        if o.type == "CURVE":
            mw, mwi = o.matrix_world, o.matrix_world.inverted()
            for sp in o.data.splines:
                if sp.type == "BEZIER":
                    for bp in sp.bezier_points:
                        for attr in ("co", "handle_left", "handle_right"):
                            setattr(bp, attr, mwi @ map_point(mw @ getattr(bp, attr)))
                else:
                    for pt in sp.points:
                        w = pt.co.w
                        v = mwi @ map_point(mw @ pt.co.xyz)
                        pt.co = (v.x, v.y, v.z, w)
        elif o.type in ("MESH", "FONT"):
            o.location = map_point(o.location)

# ------------------------------------------------------------------ 5. USB hub (ST Lab) in its tray
HUB_L, HUB_W, HUB_H, TRAY_BASE = 157.0, 37.0, 40.0, 3.0
tray_y = 115.5 + 170.0                            # clear of the plate: it lives on the middle floor
if tray:
    c = sum((tray.matrix_world @ Vector(v) for v in tray.bound_box), Vector()) / 8
    tray.location += Vector((0 - c.x, tray_y - c.y, 0))
hub_black = material("hub_black_anodized", (0.025, 0.025, 0.028), 0.4, 0.45)
usb_blue = bpy.data.materials.get("usb_blue") or material("usb_blue", (0.05, 0.25, 0.85))
white = bpy.data.materials.get("white_print") or material("white_print", (0.95, 0.95, 0.95))
led = bpy.data.materials.get("led_green") or material("led_green", (0.1, 1.0, 0.2))
hz = TRAY_BASE + HUB_H / 2
add_box("H1_body", (HUB_L, HUB_W, HUB_H), (0, tray_y, hz), hub_black, hub_coll)
top = TRAY_BASE + HUB_H
for k in range(4):
    x = -HUB_L / 2 + 28 + k * 30
    add_box(f"H1_port{k}_shell", (13.5, 6.5, 0.6), (x, tray_y, top + 0.3), zinc, hub_coll)
    add_box(f"H1_port{k}_tongue", (11.0, 2.0, 0.7), (x, tray_y + 1.0, top + 0.5), usb_blue, hub_coll)
    add_text(f"H1_port{k}_num", str(k + 1), 2.5, (x + 9, tray_y + 5, top + 0.05), white, hub_coll)
add_box("H1_ports_frame", (126, 18, 0.15), (-2, tray_y, top + 0.08), material("hub_frame_line", (0.35, 0.35, 0.38)), hub_coll)
add_text("H1_ports_txt", "Downstream Ports", 3.0, (-2, tray_y - 12, top + 0.05), white, hub_coll)
end_x = HUB_L / 2
add_box("H1_upstream_usbB", (0.8, 9, 8), (end_x + 0.4, tray_y - 4, hz + 6), zinc, hub_coll)
add_cyl("H1_power_led", 1.2, 1.0, (end_x + 0.5, tray_y + 8, hz + 6), led, hub_coll, rot=(0, math.pi / 2, 0))
add_text("H1_brand", "ST Lab", 4.0, (end_x + 0.2, tray_y, hz - 8), white, hub_coll, rot=(math.pi / 2, 0, math.pi / 2))
add_cyl("H1_dc_jack", 3.5, 1.0, (-end_x - 0.5, tray_y, hz + 5), zinc, hub_coll, rot=(0, math.pi / 2, 0))
add_cyl("H1_dc_jack_pin", 1.0, 1.2, (-end_x - 0.6, tray_y, hz + 5), black, hub_coll, rot=(0, math.pi / 2, 0))
for k in range(6):
    add_box(f"H1_side_vent{k}", (12, 0.3, 1.8), (-HUB_L / 2 + 20 + k * 22, tray_y - HUB_W / 2 - 0.15, hz - 8), black, hub_coll)
add_text("H1_note", "USB hub tray  ->  middle floor", 7.0, (0, tray_y + 52, 0.5), white, hub_coll)

# camera for the hub
cam_data = bpy.data.cameras.new("CAM_hub")
cam_data.lens = 50
cam = bpy.data.objects.new("CAM_hub", cam_data)
(bpy.data.collections.get("Cameras") or scene.collection).objects.link(cam)
cam.location = (230, tray_y - 260, 230)
direction = Vector((0, tray_y, 20)) - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

# ------------------------------------------------------------------ 6. save + render
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True)
print("saved", OUT_BLEND)
os.makedirs(RENDER_DIR, exist_ok=True)
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.image_settings.file_format = "PNG"
for cam_name in ("CAM_hero", "CAM_top", "CAM_close", "CAM_side", "CAM_ac", "CAM_hub"):
    c = bpy.data.objects.get(cam_name)
    if not c:
        continue
    scene.camera = c
    scene.render.filepath = os.path.join(RENDER_DIR, cam_name.replace("CAM_", "") + ".png")
    bpy.ops.render.render(write_still=True)
    print("rendered", scene.render.filepath)
