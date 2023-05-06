import os,sys
sys.path.append(os.getcwd()) 

from math import radians

from OCC.Core.gp import gp_Pnt, gp_Dir
from OCC.Core.Graphic3d import Graphic3d_Structure

from OCC.Display.SimpleGui import init_display
from OCC.Display.OCCViewer import Viewer3d


def test_Arrow(display:Viewer3d):
    from OCC.Core.gp import gp_Ax1
    from OCC.Core.Prs3d import Prs3d_Arrow
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox

    # box = BRepPrimAPI_MakeBox(1, 1, 1).Solid()
    # display.DisplayShape(box)

    aStruc = Graphic3d_Structure(display._struc_mgr)
    aTris = Prs3d_Arrow.DrawShaded(gp_Ax1(), 1.0, 15, 3, 4, 10)
    # Prs3d_Arrow.DrawSegments(gp_Pnt(), gp_Dir(), )
    # Prs3d_Arrow.Draw(aStruc.CurrentGroup(), gp_Pnt(), gp_Dir(), radians(30), 1)
    group = aStruc.NewGroup()
    group.AddPrimitiveArray(aTris)

    aStruc.Display()
    # aStruc.Erase()
    return aStruc

def test_BndBox(display:Viewer3d):
    from OCC.Core.Prs3d import Prs3d_BndBox
    from OCC.Core.Bnd import Bnd_Box

    aStruc = Graphic3d_Structure(display._struc_mgr)
    Prs3d_BndBox.Add(aStruc, Bnd_Box(gp_Pnt(0, 0, 0), gp_Pnt(1, 2, 1)),  
                     display.default_drawer)
    aStruc.Display()
    return aStruc

def test_point(display:Viewer3d):
    from OCC.Core.Prs3d import Prs3d_Point

    aStruc = Graphic3d_Structure(display._struc_mgr)

def test_toolCylinder(display:Viewer3d):
    from OCC.Core.Prs3d import Prs3d_ToolCylinder
    Prs3d_ToolCylinder

def test_WireFrame(display:Viewer3d):
    from OCC.Core.StdPrs import StdPrs_WFShape
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeTorus
    aStruc = Graphic3d_Structure(display._struc_mgr)

    shape = BRepPrimAPI_MakeTorus(3, 1).Solid()
    StdPrs_WFShape.Add(aStruc, shape, display.default_drawer)

    aStruc.Display()
    return aStruc

def test_shadedShape(display:Viewer3d):
    from OCC.Core.StdPrs import StdPrs_ShadedShape
    from OCC.Core.StdPrs import (
        StdPrs_Volume_Opened, StdPrs_Volume_Closed, 
        StdPrs_Volume_Autodetection
    )
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeTorus

    aStruc = Graphic3d_Structure(display._struc_mgr)

    shape = BRepPrimAPI_MakeTorus(3, 1).Solid()
    StdPrs_ShadedShape.Add(aStruc, shape, display.default_drawer, 
                           StdPrs_Volume_Autodetection)

    aStruc.Display()
    return aStruc

# dsg
def test_Symbol(display:Viewer3d):
    # notwarp
    from OCC.Core.DsgPrs import DsgPrs_SymbPresentation
    aStruc = Graphic3d_Structure(display._struc_mgr)

if __name__ == '__main__':
    display, start_display, *_ = init_display()

    test_Arrow(display)

    display.FitAll()
    start_display()
