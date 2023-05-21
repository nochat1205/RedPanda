import os,sys
sys.path.append(os.getcwd()) 

import pickle

def test_wire_face():
    from OCC.Core.gp import gp_Pnt2d
    from OCC.Core.GCE2d import GCE2d_MakeSegment, GCE2d_MakeArcOfCircle
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
    from OCC.Extend.ShapeFactory import make_wire, make_edge2d, make_face
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert, BRepBuilderAPI_MakeFace
    from OCC.Core.BRepLib import breplib_BuildCurve3d, breplib_BuildCurves3d
    from OCC.Display.SimpleGui import init_display

    disp, start, *_ = init_display()
    p1 = gp_Pnt2d(30, 10)
    p12 = gp_Pnt2d(0, 20)
    p2 = gp_Pnt2d(-30, 10)

    p3 = gp_Pnt2d(30, -10)
    p34 = gp_Pnt2d(0, -20)
    p4 = gp_Pnt2d(-30, -10)

    e1 = make_edge2d(GCE2d_MakeArcOfCircle(p1, p12, p2).Value())
    e2 = make_edge2d(p2, p4)

    e3 = make_edge2d(GCE2d_MakeArcOfCircle(p4, p34, p3).Value())
    e4 = make_edge2d(p3, p1)
    breplib_BuildCurve3d(e1)
    breplib_BuildCurve3d(e2)
    breplib_BuildCurve3d(e3)
    breplib_BuildCurve3d(e4)

    wire = make_wire([e1, e2, e3, e4])
    face = BRepBuilderAPI_MakeFace(wire, True).Face()
    
    face1 = BRepBuilderAPI_NurbsConvert(face, True).Shape()
    surface = BRep_Tool.Surface(face1)
    print(surface.Bounds())
    disp.DisplayShape(wire)
    disp.DisplayShape(face)
    disp.DisplayShape(face1)

    start()

def test_face_bound():
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.Geom import Geom_BoundedCurve
    with open(r'tests\wireface_test_01.rppickle', 'rb') as f:
        shape = pickle.load(f)

        surface:Geom_BoundedCurve = BRep_Tool.Surface(shape)
        surface = Geom_BoundedCurve.DownCast(surface)
        print(surface.get_type_name())
        print(surface.Bounds())


if __name__ == '__main__':
    test_wire_face()
