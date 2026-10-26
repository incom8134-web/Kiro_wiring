"""Render images/base_plate_print.png from the two print halves (VTK, offscreen)."""
import os
import tempfile

import trimesh
import vtk

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = os.path.join(ROOT, "print_files"), os.path.join(ROOT, "images")


def actor(mesh_path):
    r = vtk.vtkSTLReader()
    r.SetFileName(mesh_path)
    n = vtk.vtkPolyDataNormals()
    n.SetInputConnection(r.GetOutputPort())
    n.SetFeatureAngle(30)
    m = vtk.vtkPolyDataMapper()
    m.SetInputConnection(n.GetOutputPort())
    a = vtk.vtkActor()
    a.SetMapper(m)
    a.GetProperty().SetColor(0.93, 0.93, 0.93)
    a.GetProperty().SetSpecular(0.2)
    return a


if __name__ == "__main__":
    tmp = tempfile.mkdtemp()
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    for half in ("base_plate_left", "base_plate_right"):
        stl = os.path.join(tmp, half + ".stl")
        trimesh.load(os.path.join(SRC, half + ".3mf"), force="mesh").export(stl)
        ren.AddActor(actor(stl))
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(0, 0, 40)
    cam.SetPosition(-250, -420, 380)
    cam.SetViewUp(0, 0, 1)
    ren.ResetCamera()
    cam.Zoom(1.25)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.AddRenderer(ren)
    win.SetSize(1400, 1000)
    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.Update()
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(os.path.join(OUT, "base_plate_print.png"))
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()
    print("wrote images/base_plate_print.png")
