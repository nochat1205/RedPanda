import os,sys
sys.path.append(os.getcwd())

from OCC.Display.SimpleGui import init_display
from RedPanda.Core.Euclid import RP_Pnt
from OCC.Core.gp import gp_Dir, gp_Lin, gp_Circ
from OCC.Core.TopoDS import TopoDS_Shape
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


from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_WIRE, TopAbs_VERTEX
from OCC.Core.BRep import BRep_Tool

class Point(object):
    def __init__(self, shape, param) -> None:
        self.shape:TopoDS_Shape = shape
        self.param = [0 for i in range(3)]

        for i in range(min(3, len(param))):
            self.param[i] = param[i]
        
    @property
    def Point3d(self):
        if self.shape is None or self.shape.IsNull():
            return RP_Pnt(*self.param)
        elif self.shape.ShapeType() == TopAbs_VERTEX:
            return BRep_Tool.Pnt(self.shape)
        elif self.shape.ShapeType() == TopAbs_EDGE:
            curve, u0, u1 = BRep_Tool.Curve(self.shape, TopLoc_Location())
            pnt = curve.Value(self.param[0])
            return pnt

        return None
            

def GetPoint(shapes, x, y, _display):
    from OCC.Core.Geom import Geom_Line
    from OCC.Core.BRepLib import breplib_BuildCurve3d
    from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
    from OCC.Extend.ShapeFactory import make_edge, make_wire
    from RedPanda.Core.Make import project_point_on_curve
    print('Run')
    # # self._display.Context.ClearSelected(True)
    # shapes:list[TopoDS_Shape] = _display.Select(x, y)

    projX, projy, projz, rayx, rayy, rayz = _display.View.ProjReferenceAxe(x, y)
    p = RP_Pnt(projX, projy, projz)
    if len(shapes) == 0:
        return p

    if shapes[0].ShapeType() == TopAbs_VERTEX:
        p = BRep_Tool.Pnt(shapes[0])
        # self._display.DisplayMessage(p, f'Coord:{p.Coord()}')
    elif shapes[0].ShapeType() == TopAbs_EDGE:
        try:
            # 1
            # dir = gp_Dir(rayx, rayy, rayz)
            # line = gp_Lin(p, dir)
            # edge = make_edge(line)
            # extrema = BRepExtrema_DistShapeShape(shapes[0], edge)
            # p = extrema.PointOnShape1(1)

            # 2
            from RedPanda.Core.topogy.edge import EdgeAnalyst
            from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnCurve
            curve, u0, u1 = EdgeAnalyst(shapes[0]).curve
            builder = GeomAPI_ProjectPointOnCurve(p, curve)
            print(u0, u1)
            print(builder.LowerDistanceParameter(), builder.NearestPoint(), builder.LowerDistance())
        except Exception as error:
            print(f'error:{error}')

    return p

if __name__ == '__main__':
    display, start, *_ = init_display()
    display.Viewer.SetPrivilegedPlane(gp_Ax3())
    edge = BRepBuilderAPI_MakeEdge(gp_Circ(gp_XOY(), 5)).Edge()
    display.DisplayShape(edge)
    display.FitAll()
    display.register_select_callback(lambda shape, x, y:GetPoint(shape, x, y, display))

    start()
