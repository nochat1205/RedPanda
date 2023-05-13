
import os,sys
sys.path.append(os.getcwd())

from OCC.Display.SimpleGui import init_display
from OCC.Core.V3d import V3d_View
from OCC.Core.AIS import (
    AIS_Axis,
    AIS_InteractiveContext,
    AIS_Shape
)
from OCC.Core.GC import GC_MakeLine
from RedPanda.Core.Make import make_box, make_line
from RedPanda.Core.Euclid import RP_Pnt, RP_Dir, RP_Vec, RP_Ax3
from OCC.Core.V3d import V3d_Viewer
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_BLACK, Quantity_TOC_RGB

def test_Axis():
    # line = make_line(RP_Pnt(0, 0, 0), RP_Pnt(0, 2, 0))
    line = GC_MakeLine(RP_Pnt(0, 0, 0), RP_Pnt(0, 1, 1)).Value()

    context.Display(AIS_Axis(line), True)
    # AIS_Circle
    

def test_camera():
    from OCC.Core.AIS import AIS_CameraFrustum
    a = AIS_CameraFrustum()
    context.Display(a, True)

def test_colorscale():
    from OCC.Core.AIS import AIS_ColorScale
    from OCC.Core.Aspect import Aspect_TOCSP_RIGHT, Aspect_TOTP_LEFT
    from OCC.Core.Graphic3d import (
        Graphic3d_ZLayerId_TopOSD,
        Graphic3d_TransformPers,
        Graphic3d_TMF_2d,
        Graphic3d_Vec2i
    )
    colorScale = AIS_ColorScale()
    colorScale.SetRange(0, 1) #数值范围
    colorScale.SetNumberOfIntervals(1)#颜色间隔
    colorScale.SetSmoothTransition(True) # 颜色光滑过渡
    colorScale.SetLabelPosition(Aspect_TOCSP_RIGHT) # 标签位置
    colorScale.SetTextHeight(16) # 文本高度
    colorScale.SetSize(50, 200) # 标尺大小
    colorScale.SetZLayer(Graphic3d_ZLayerId_TopOSD) # 最上层显示
    aTrsfPers = Graphic3d_TransformPers(Graphic3d_TMF_2d, Aspect_TOTP_LEFT, Graphic3d_Vec2i(0, 0));
    colorScale.SetTransformPersistence(aTrsfPers) # 显示位置
    colorScale.SetToUpdate()
    # colorScale.SetTitle()
    context.Display(colorScale, True)


def text_manipulator(ais_box):
    # transform 球
    from OCC.Core.AIS import AIS_Manipulator, AIS_ManipulatorMode
    aManipulator = AIS_Manipulator()
    aManipulator.SetPart(0, AIS_ManipulatorMode.AIS_MM_Scaling, False)
    aManipulator.SetPart(1, AIS_ManipulatorMode.AIS_MM_Rotation, False)
    # Attach manipulator to already displayed object and manage manipulation modes
    aManipulator.Attach(ais_box)
    aManipulator.EnableMode(AIS_ManipulatorMode.AIS_MM_Translation)
    aManipulator.EnableMode(AIS_ManipulatorMode.AIS_MM_Rotation)
    aManipulator.EnableMode(AIS_ManipulatorMode.AIS_MM_Scaling)

    aManipulator.SetModeActivationOnDetection(True)
    context.Display(aManipulator, False)

def test_connect():
    from OCC.Core.AIS import AIS_MultipleConnectedInteractive, AIS_ConnectedInteractive

def test_plane():
    from OCC.Core.AIS import AIS_Plane
    from OCC.Core.BRep import BRep_Tool_Surface
    from OCC.Core.Geom import Geom_Plane
    from OCC.Core.Prs3d import Prs3d_PlaneAspect
    from OCC.Core.Prs3d import Prs3d_Drawer

    from RedPanda.Core.Make import make_plane

    display.SetModeHLR()
    #
    # Get Context
    #
    ais_context = display.GetContext()
    #
    # Get Prs3d_drawer from previous context
    #
    drawer:Prs3d_Drawer = ais_context.DefaultDrawer()
    drawer.SetIsoOnPlane(False)
    planeAspect = drawer.PlaneAspect()
    planeAspect.SetIsoDistance(0.2)
    print(planeAspect.IsoDistance())
    drawer.SetPlaneAspect(planeAspect)

    la = drawer.LineAspect()
    la.SetWidth(4)
    # increase line width in the current viewer
    # This is only viewed in the HLR mode (hit 'e' key for instance)
    line_aspect = drawer.SeenLineAspect()
    drawer.EnableDrawHiddenLine() # hiddenline
    line_aspect.SetWidth(4)
    #
    drawer.SetWireAspect(line_aspect)


    face = make_plane()
    surface = BRep_Tool_Surface(face)
    plane = Geom_Plane.DownCast(surface)
    ais = AIS_Plane(plane)
    # aspect = Prs3d_PlaneAspect()
    # x = aspect.PlaneXLength()
    # aspect.SetDisplayCenterArrow(True)
    # print(x)
    # aspect.SetIsoDistance(x/5)
    # ais.SetAspect(aspect)
    context.Display(ais_box, False)

def test_planeTrihedron():
    from OCC.Core.AIS import AIS_PlaneTrihedron
    from OCC.Core.BRep import BRep_Tool_Surface
    from OCC.Core.Geom import Geom_Plane

    from RedPanda.Core.Make import make_plane
    face = make_plane()
    surface = BRep_Tool_Surface(face)
    plane = Geom_Plane.DownCast(surface)
    context.Display(AIS_PlaneTrihedron(plane), False)

def test_RubberBand():
    # select Rubber
    from OCC.Core.AIS import AIS_RubberBand
    context.Display(AIS_RubberBand(), False)

def Test_mesh():
    from OCC.Core.MeshVS import MeshVS_Mesh
    context.Display(MeshVS_Mesh(), False)

def test_grid():
    from OCC.Core.V3d import V3d_RectangularGrid
    from OCC.Core.Aspect import Aspect_GT_Rectangular, Aspect_GDM_Lines
    from OCC.Core.Quantity import Quantity_NOC_ANTIQUEWHITE, Quantity_NOC_WHITE
    # grid = V3d_RectangularGrid(viewer, Quantity_Color(), Quantity_Color())
    # viewer.SetGridEcho(True)
    viewer.ActivateGrid(Aspect_GT_Rectangular, Aspect_GDM_Lines)
    grid = viewer.Grid()
    # grid.SetColors(Quantity_NOC_ANTIQUEWHITE, Quantity_NOC_WHITE)

def AxisTest():
    from OCC.Core.TopLoc import TopLoc_Location
    pnt = RP_Pnt(1, 0, 0)
    ax = RP_Ax3()
    ax.Scale(pnt, 2)

    box = make_box(ax, 1, 1, 1)
    display.DisplayShape(box)

def Prs_dim():
    from OCC.Core.gp import gp_Circ, gp_Ax2
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
    
    from OCC.Core.PrsDim import PrsDim_RadiusDimension, PrsDim_DiameterDimension
    from OCC.Core.Prs3d import Prs3d_DimensionAspect

    c = gp_Circ(gp_Ax2(RP_Pnt(200.0, 200.0, 0.0), RP_Dir(0.0, 0.0, 1.0)), 80)
    edge_circ = BRepBuilderAPI_MakeEdge(c).Edge()
    ais_shp = AIS_Shape(edge_circ)
    display.Context.Display(ais_shp, True)

    rd = PrsDim_DiameterDimension(edge_circ) # 演示组件 AIS
    the_aspect = Prs3d_DimensionAspect()
    the_aspect.SetCommonColor(Quantity_Color(Quantity_NOC_BLACK))
    rd.SetDimensionAspect(the_aspect) # 设置样式

    display.Context.Display(rd, True)

def line():
    # create a line
    from OCC.Core.Geom import Geom_Line
    from OCC.Core.AIS import AIS_Line
    from OCC.Core.Prs3d import Prs3d_Drawer, Prs3d_LineAspect

    p1 = RP_Pnt(2.0, 3.0, 4.0)
    d1 = RP_Dir(4.0, 5.0, 6.0)
    line1 = Geom_Line(p1, d1)

    ais_line1 = AIS_Line(line1)

    # if we need to edit color, we can simply use SetColor
    # ais_line1.SetColor(Quantity_NOC_RED)

    # but actually we need to edit more, not just color. Line width and style as well
    # To do that, we need to do use AIS_Drawer and apply it to ais_line1
    drawer = Prs3d_Drawer()
    ais_line1.SetAttributes(drawer)

    display.Context.Display(ais_line1, False)
    # we can apply the same rule for other lines by just doing a for loop
    for i in range(1, 5):
        p2 = RP_Pnt(i, 2.0, 5.0)
        d2 = RP_Dir(4 * i, 6.0, 9.0)
        line2 = Geom_Line(p2, d2)

        ais_line2 = AIS_Line(line2)

        width = float(i)
        drawer = ais_line2.Attributes()
        # asp : first parameter color, second type, last width
        asp = Prs3d_LineAspect(Quantity_Color(9 * i), i, width)
        drawer.SetLineAspect(asp)
        ais_line2.SetAttributes(drawer)

        display.Context.Display(ais_line2, False)


def pnt():
    from OCC.Core.Aspect import (
        Aspect_TOM_POINT,
        Aspect_TOM_PLUS,
        Aspect_TOM_STAR,
        Aspect_TOM_X,
        Aspect_TOM_O,
        Aspect_TOM_O_POINT,
        Aspect_TOM_O_PLUS,
        Aspect_TOM_O_STAR,
        Aspect_TOM_O_X,
        Aspect_TOM_RING1,
        Aspect_TOM_RING2,
        Aspect_TOM_RING3,
        Aspect_TOM_BALL,
    )
    from OCC.Core.Geom import Geom_CartesianPoint
    from OCC.Core.AIS import AIS_Point
    from OCC.Core.Prs3d import Prs3d_PointAspect
    ALL_ASPECTS = [
        Aspect_TOM_POINT,
        Aspect_TOM_PLUS,
        Aspect_TOM_STAR,
        Aspect_TOM_X,
        Aspect_TOM_O,
        Aspect_TOM_O_POINT,
        Aspect_TOM_O_PLUS,
        Aspect_TOM_O_STAR,
        Aspect_TOM_O_X,
        Aspect_TOM_RING1,
        Aspect_TOM_RING2,
        Aspect_TOM_RING3,
        Aspect_TOM_BALL,
    ]
    # create a point
    for idx in range(10):
        for idy in range(10):
            for idz, aspect in enumerate(ALL_ASPECTS):
                x = 0 + idx * 0.1
                y = 0 + idy * 0.1
                z = 0 + idz / len(ALL_ASPECTS)
                p = Geom_CartesianPoint(RP_Pnt(x, y, z))
                color = Quantity_Color(x / len(ALL_ASPECTS), 0, z, Quantity_TOC_RGB)
                ais_point = AIS_Point(p)

                drawer = ais_point.Attributes()
                asp = Prs3d_PointAspect(aspect, color, 3)
                drawer.SetPointAspect(asp)
                ais_point.SetAttributes(drawer)

                display.Context.Display(ais_point, False)

def quantity():
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCC.Core.Prs3d import Prs3d_Drawer
    ais_context = display.GetContext()
    #
    # Display current quality
    dc = ais_context.DeviationCoefficient()
    da = ais_context.DeviationAngle()
    print("Default AISInteractiveContext display quality settings:")
    print("Deviation Coefficient: %f" % dc)
    print("Deviation Angle: %f" % da)
    #
    # Improve quality by a factor 10
    #
    factor = 10
    ais_context.SetDeviationCoefficient(dc / factor)
    ais_context.SetDeviationAngle(da / factor)
    ais_context:AIS_InteractiveContext
    ais_context.SetIsoNumber(5)
    print("Quality display improved by a factor {0}".format(factor))
    #
    # Displays a cylinder
    #
    s = BRepPrimAPI_MakeCylinder(50.0, 50.0).Shape()
    ais_shp:AIS_Shape = display.DisplayShape(s)[0]

    drawer = Prs3d_Drawer()
    da_hlr = drawer.HLRAngle()
    print("Deviation Angle Hidden Line Removal: %f" % da_hlr)
    drawer.SetHLRAngle(da_hlr / factor)

    ais_shp.SetAttributes(drawer)
    #
    # Display settings and display loop
    #
    display.View_Iso()

def Angle():
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
    from OCC.Core.PrsDim import PrsDim_AngleDimension
    line = GC_MakeLine(RP_Pnt(0, 0, 0), RP_Pnt(0, 1, 1)).Value()
    edge1 = BRepBuilderAPI_MakeEdge(line).Edge()

    line = GC_MakeLine(RP_Pnt(0, 0, 0), RP_Pnt(0, 0, 1)).Value()
    edge2 = BRepBuilderAPI_MakeEdge(line).Edge()
    angleDim = PrsDim_AngleDimension(edge1, edge2)

    display.DisplayShape(edge1, False)
    display.DisplayShape(edge2, False)
    context.Display(angleDim, False)

def DisplayVector():
    pnt = RP_Pnt()
    vec = RP_Vec(0, 0, 1)
    display.DisplayVector(vec, pnt)

def DisplayDimension():
    from OCC.Core.PrsDim import PrsDim_LengthDimension
    from OCC.Core.Prs3d import Prs3d_DimensionAspect
    from OCC.Core.Geom import Geom_Plane
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.TCollection import TCollection_AsciiString

    from RedPanda.Core.topogy import SolidAnalyst, FaceAnalyst
    
    analyst = SolidAnalyst(box)
    shellAnalyst = analyst.shells()[0]
    face = shellAnalyst.Faces()[1]
    faceAnalyst = FaceAnalyst(face)
    edge = faceAnalyst.edges()[2]
    plane = Geom_Plane.DownCast(faceAnalyst.surface).Pln()


    prs = PrsDim_LengthDimension(edge, plane)
    the_aspect = Prs3d_DimensionAspect()
    the_aspect.SetCommonColor(Quantity_Color(Quantity_NOC_BLACK))
    prs.SetDimensionAspect(the_aspect) # 设置样式

    prs.SetCustomValue (10.2)
    prs.SetFlyout(0)
    # print(prs.GetTextPosition())
    display.DisplayShape(box)
    context.Display(prs, False)

def Label():
    from OCC.Core.TDF import TDF_Data
    from OCC.Core.TPrsStd import TPrsStd_AISPresentation
    from OCC.Core.TDataStd import TDataStd_Name
    from OCC.Core.TNaming import TNaming_NamedShape
    from OCC.Core.TCollection import TCollection_ExtendedString
    df = TDF_Data()
    label = df.Root()
    prs = TPrsStd_AISPresentation.Set(label, TNaming_NamedShape.GetID())
    ais_box.SetOwner(prs)

def curve():
    from OCC.Core.Geom import Geom_CylindricalSurface, Geom_RectangularTrimmedSurface
    from RedPanda.Core.topogy import FaceAnalyst
    from RedPanda.Core.topogy import make_face
    from RedPanda.Core.Euclid import RP_Ax3
    from math import pi
    cy = Geom_CylindricalSurface(RP_Ax3(), 3)
    surface = Geom_RectangularTrimmedSurface(cy, 0, pi, 0, 20)

    # face = make_face(cy)
    # analyster = FaceAnalyst(face)
    # print(analyster.domain())

def Curve_on_plane():
    from RedPanda.Core.Make import make_plane
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.Geom import Geom_Plane
    plane = make_plane()
    plane = BRep_Tool.Surface(plane)
    plane = Geom_Plane.DownCast(plane)
    print(plane.Bounds())

def SetConment():
    import re
    from OCC.Core.TCollection import TCollection_ExtendedString
    from OCC.Core.TDataStd import TDataStd_Comment, TDataStd_Name
    from OCC.Core.TDF import TDF_Label, TDF_Data

    df = TDF_Data()
    aLabel = df.Root()
    msg:str = TDataStd_Comment.Set(aLabel, TCollection_ExtendedString('Lain')).DumpToString()
    print(msg)
    a = re.match()
    print(a.group(1))

    def test_builder(self):
        from OCC.Core.Geom import Geom_CylindricalSurface, Geom_RectangularTrimmedSurface
        from OCC.Core.Geom2d import Geom2d_Ellipse, Geom2d_TrimmedCurve
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge2d
        from RedPanda.Core.topogy import FaceAnalyst
        from RedPanda.Core.topogy import make_face, make_edge2d
        from RedPanda.Core.Euclid import RP_Ax3
        from OCC.Core.gp import gp_Pnt2d, gp_Dir2d, gp_Ax2d
        from math import pi
        height = 20
        cy = Geom_CylindricalSurface(RP_Ax3(), 3)
        surface = Geom_RectangularTrimmedSurface(cy, 0, 2*pi, 0, height)

        aPnt = gp_Pnt2d(2*pi, height/2)
        aDir = gp_Dir2d(2*pi, height/4)
        anAx2d = gp_Ax2d(aPnt, aDir)
        aMajor = 2 * pi
        aMinor = height / 10
        anEllipse1 = Geom2d_Ellipse(anAx2d, aMajor, aMinor)
        anArc1 = Geom2d_TrimmedCurve(anEllipse1, 0, pi)
        anEdge10Surf1 = BRepBuilderAPI_MakeEdge2d(anArc1, cy).Edge()

        from OCC.Core.gp import gp_Ax3, gp_Pnt, gp_Dir
        ax = gp_Ax3(gp_Pnt(aPnt.X(), aPnt.Y(), 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
        self.v2d._display.FocusOn(ax)
        self.v3d._display.DisplayShape(surface)
        self.v2d.DisplaySurfaceFlay(surface)

        self.v3d._display.DisplayShape(anEdge10Surf1)
        self.v2d._display.DisplayShape(anArc1)

def test_pickle():
    import pickle
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCC.Core.TopoDS import TopoDS_Shape
    builder = BRepPrimAPI_MakeBox(10, 10, 10)
    a = builder.Shape()

    with open('a.pickle', 'wb+') as f:
        pickle.dump(a, f)

    with open('a.pickle', 'rb+') as f:
        a = pickle.load(f)

    display.DisplayShape(a)

def test_trihedron():
    from OCC.Core.AIS import AIS_Trihedron
    from OCC.Core.Geom import Geom_Axis2Placement
    from OCC.Core.gp import gp_YOZ

    ais = AIS_Trihedron(Geom_Axis2Placement(gp_YOZ()))
    display.Context.Display(ais, True)

if __name__ == '__main__':
    display, start, *_ = init_display()
    box = make_box(10, 10, 10)
    ais_box = AIS_Shape(box)
    viewer:V3d_Viewer = display.Viewer
    view:V3d_View = display.View
    context:AIS_InteractiveContext = display.Context
    test_trihedron()

    # display.View_Iso()
    display.FitAll()
    start()

