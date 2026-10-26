"""
Combined exports for the Kiro power tray: one STEP, one OBJ and render PNGs.

Run (CadQuery env):  python export_assembly.py
Out (3d_models/):    assembly.step   base plate + USB hub tray (solids, Fusion 360)
                     assembly.obj    same two parts as meshes (Blender)
"""
import os
import sys

import cadquery as cq
import numpy as np
import trimesh
import vtk

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "3d_models")
sys.path.insert(0, HERE)
import base_plate as pp    # noqa: E402
import usb_hub_tray as ht  # noqa: E402

# hub tray shown in front of the plate (it lives on the middle floor)
TRAY_POS = (0.0, -pp.PL_W / 2 - 70.0, 0.0)


def to_mesh(wp, tol=0.05):
    verts, faces = wp.val().tessellate(tol, 0.2)
    return trimesh.Trimesh(np.array([(v.x, v.y, v.z) for v in verts]), np.array(faces), process=True)


def placeholders():
    """Simple stand-in boxes for the render only (not exported)."""
    items = []
    for name, (cx, cy, sx, sy, h, _, col) in pp.COMPONENTS.items():
        z = pp.PL_T + (pp.STANDOFF_H if name in pp.RAISED else 0)
        box = trimesh.creation.box((sx - 4 if "SMPS" in name else sx, sy - 4 if "SMPS" in name else sy, h))
        box.apply_translation((cx, cy, z + h / 2))
        items.append((name, box, col))
    # SMPS fan ring on the top face, near the end away from the terminals
    cx, cy, sx, _, h = pp.COMPONENTS["SMPS_12V_350W"][:5]
    fan = trimesh.creation.annulus(18, 26, 1.5)
    fan.apply_translation((cx - sx / 2 + 45, cy, pp.PL_T + pp.STANDOFF_H + h + 0.8))
    items.append(("fan", fan, (0.15, 0.15, 0.15)))
    # AC inlet module
    x = pp.PL_L / 2 - pp.AC_WALL_T
    inlet = trimesh.creation.box((30, pp.AC_CUT_W - 1, pp.AC_CUT_H - 1))
    inlet.apply_translation((x - 15, pp.AC_Y, pp.AC_CZ))
    items.append(("inlet", inlet, (0.08, 0.08, 0.08)))
    # USB hub in its tray
    hub = trimesh.creation.box((ht.HUB_L, ht.HUB_W, ht.HUB_H))
    hub.apply_translation((TRAY_POS[0], TRAY_POS[1], ht.BASE + ht.HUB_H / 2))
    items.append(("hub", hub, (0.12, 0.12, 0.14)))
    return items


def vtk_actor(mesh, color, opacity=1.0):
    pts = vtk.vtkPoints()
    for v in mesh.vertices:
        pts.InsertNextPoint(*v)
    polys = vtk.vtkCellArray()
    for f in mesh.faces:
        polys.InsertNextCell(3)
        for i in f:
            polys.InsertCellPoint(int(i))
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetPolys(polys)
    nrm = vtk.vtkPolyDataNormals()
    nrm.SetInputData(pd)
    nrm.SetFeatureAngle(30)
    m = vtk.vtkPolyDataMapper()
    m.SetInputConnection(nrm.GetOutputPort())
    a = vtk.vtkActor()
    a.SetMapper(m)
    a.GetProperty().SetColor(*color)
    a.GetProperty().SetOpacity(opacity)
    a.GetProperty().SetSpecular(0.25)
    a.GetProperty().SetSpecularPower(20)
    return a


def render(parts, name, cam_pos, focal=(0, -40, 30), zoom=1.2, size=(1800, 1200), up=(0, 0, 1)):
    ren = vtk.vtkRenderer()
    ren.SetBackground(0.97, 0.97, 0.98)
    ren.SetBackground2(0.86, 0.89, 0.93)
    ren.GradientBackgroundOn()
    for mesh, col, op in parts:
        ren.AddActor(vtk_actor(mesh, col, op))
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(*focal)
    cam.SetPosition(*cam_pos)
    cam.SetViewUp(*up)
    ren.ResetCamera()
    cam.Zoom(zoom)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetMultiSamples(8)
    win.AddRenderer(ren)
    win.SetSize(*size)
    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.Update()
    wr = vtk.vtkPNGWriter()
    os.makedirs(os.path.join(HERE, "images"), exist_ok=True)
    wr.SetFileName(os.path.join(HERE, "images", f"{name}.png"))
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()
    print("wrote", name + ".png")


if __name__ == "__main__":
    plate = pp.build_plate()
    tray = ht.build().translate(TRAY_POS)

    asm = cq.Assembly(name="kiro_power_tray")
    asm.add(plate, name="base_plate", color=cq.Color(0.93, 0.93, 0.93))
    asm.add(tray, name="usb_hub_tray", color=cq.Color(0.85, 0.72, 0.58))
    asm.export(os.path.join(OUT, "assembly.step"))
    print("wrote 3d_models/assembly.step")

    plate_m, tray_m = to_mesh(plate), to_mesh(tray)
    plate_m.visual = trimesh.visual.ColorVisuals(plate_m, face_colors=[236, 236, 236, 255])
    tray_m.visual = trimesh.visual.ColorVisuals(tray_m, face_colors=[217, 184, 148, 255])
    scene = trimesh.Scene()
    scene.add_geometry(plate_m, node_name="base_plate", geom_name="base_plate")
    scene.add_geometry(tray_m, node_name="usb_hub_tray", geom_name="usb_hub_tray")
    scene.export(os.path.join(OUT, "assembly.obj"), include_normals=True)
    print("wrote 3d_models/assembly.obj")
