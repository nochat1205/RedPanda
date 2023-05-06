import os,sys                                     
sys.path.append(os.getcwd()) 

from tests.preview_widget import WidgetPreview
from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Elips, gp_Dir


def test_projector():
    from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnCurve
    from OCC.Core.Geom import Geom_Ellipse

    # 创建椭圆曲线
    ellipse = Geom_Ellipse(gp_Ax2(), 10, 5)

    # 创建要投影的点
    point = gp_Pnt(0, 5, 2)

    # 创建投影对象
    projector = GeomAPI_ProjectPointOnCurve(point, ellipse)

    # 检查是否成功投影
    if projector.NbPoints() > 0:
        projected_point = projector.Point(1)
        print("Projected point:", projected_point.Coord())
    else:
        print("No projection found.")

def _make_edge2d():
    from OCC.Core.gp import gp_Ax2d, gp_Ax3
    from OCC.Core.Geom2d import Geom2d_Ellipse
    from OCC.Extend.ShapeFactory import BRepBuilderAPI_MakeEdge2d
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.BRepLib import breplib_BuildCurve3d
    from RedPanda.Core.topogy.edge import EdgeAnalyst

    from math import pi
    major = 3
    minor = 1

    epse = Geom2d_Ellipse(gp_Ax2d(), major, minor)
    print(epse.Value(0).Coord(), epse.Value(pi).Coord())
    edge = BRepBuilderAPI_MakeEdge2d(epse).Edge()
    breplib_BuildCurve3d(edge) # TODO: need, edge2d have problem

    curve, u, v =  EdgeAnalyst(edge).curve # curve and first and last parameter
    print(curve.Value(u).Coord(), curve.Value(v/2).Coord())
    print(gp_Ax3().Location().Coord())
    return edge


def test_grid():
    from RedPanda.widgets.Logic_Viewer2d import qtViewer2d

    preview = WidgetPreview(qtViewer2d)
    view2d:qtViewer2d = preview.widget

    edge = _make_edge2d()
    view2d._display.DisplayShape(edge)
    view2d.SetUVGrid(-3, 3, -1, 1)
    view2d._display.DisplayShape(gp_Pnt())

    preview.run()

    return


if __name__ == '__main__':
    test_grid()

