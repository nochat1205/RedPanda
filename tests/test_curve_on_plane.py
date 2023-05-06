import os,sys
sys.path.append(os.getcwd())

from OCC.Display.SimpleGui import init_display

from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.gp import gp_XOY, gp_Ax3, gp_Ax2d
from OCC.Core.Geom import Geom_Plane
from OCC.Core.Geom2d import Geom2d_Circle
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepLib import breplib_BuildCurve3d
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeEdge2d
)
def test_curve_on_plane():
    display, start_display, *_ = init_display()
    curve1 = Geom2d_Circle(gp_Ax2d(), 5)
    curve2 = Geom2d_Circle(gp_Ax2d(), 4)
    edge2 = BRepBuilderAPI_MakeEdge2d(curve1).Edge()
    edge2d = BRepBuilderAPI_MakeEdge2d(curve2).Edge()
    breplib_BuildCurve3d(edge2d)
    
    edge2d2, u, v = BRep_Tool.CurveOnPlane(edge2d, Geom_Plane(gp_Ax3()), TopLoc_Location())
    print(u, v)
    edge2d2 = BRepBuilderAPI_MakeEdge2d(edge2d2).Edge()
    display.DisplayShape(edge2, False)
    display.DisplayShape(edge2d, False)
    display.DisplayShape(edge2d2, False)

    start_display()

def test_curve_edge2d():
    curve = Geom2d_Circle(gp_Ax2d(), 4)
    edge = BRepBuilderAPI_MakeEdge2d(curve).Edge()

    a = BRep_Tool.Curve(edge)
    assert a == (0.0, 0.0)

if __name__ == '__main__':
    test_curve_edge2d()
