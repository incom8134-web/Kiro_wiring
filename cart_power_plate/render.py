"""Render preview PNGs of the plate + dummy parts with VTK (offscreen)."""
import glob, os, tempfile
import trimesh, vtk

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
COL = {"plate": (0.93, 0.93, 0.93), "SMPS": (0.72, 0.74, 0.78), "JETSON": (0.25, 0.6, 0.25),
       "FUSE": (0.2, 0.2, 0.22), "BUCK": (0.7, 0.12, 0.12), "AC_INLET": (0.08, 0.08, 0.08)}

def actor(path, opacity=1.0):
    r = vtk.vtkSTLReader(); r.SetFileName(path)
    n = vtk.vtkPolyDataNormals(); n.SetInputConnection(r.GetOutputPort()); n.SetFeatureAngle(30)
    m = vtk.vtkPolyDataMapper(); m.SetInputConnection(n.GetOutputPort())
    a = vtk.vtkActor(); a.SetMapper(m)
    c = next((v for k, v in COL.items() if k in os.path.basename(path)), (0.6, 0.6, 0.6))
    a.GetProperty().SetColor(*c); a.GetProperty().SetOpacity(opacity)
    a.GetProperty().SetSpecular(0.2)
    return a

def render(files, name, pos, up=(0, 0, 1), opacity=1.0):
    ren = vtk.vtkRenderer(); ren.SetBackground(1, 1, 1)
    for f in files:
        ren.AddActor(actor(f, opacity if "_dummy" in f else 1.0))
    cam = ren.GetActiveCamera(); cam.SetFocalPoint(0, 0, 40); cam.SetPosition(*pos); cam.SetViewUp(*up)
    ren.ResetCamera(); cam.Zoom(1.25)
    win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.AddRenderer(ren); win.SetSize(1400, 1000)
    win.Render()
    w2i = vtk.vtkWindowToImageFilter(); w2i.SetInput(win); w2i.Update()
    wr = vtk.vtkPNGWriter(); wr.SetFileName(f"{out}/{name}.png"); wr.SetInputConnection(w2i.GetOutputPort()); wr.Write()

tmp = tempfile.mkdtemp()
def stl(name):  # 3MF -> temp STL for VTK
    path = f"{tmp}/{name}.stl"
    trimesh.load(f"{out}/{name}.3mf", force="mesh").export(path)
    return path

render([stl("plate_full")], "preview_plate_iso", (-250, -420, 380))
render([stl("plate_left"), stl("plate_right")], "preview_split", (300, -350, 450))
print("ok")
