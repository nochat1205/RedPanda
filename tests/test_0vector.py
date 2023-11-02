from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display
from OCC.Extend.ShapeFactory import points_to_bspline

from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.AIS import AIS_Shape, AIS_InteractiveContext
from OCC.Core.V3d import V3d_Viewer
from OCC.Core.SelectMgr import (
    SelectMgr_SelectableObject,
    SelectMgr_Selection,
    SelectMgr_ViewerSelector,
    SelectMgr_SelectionManager,
)
from OCC.Core.PrsMgr import (
    PrsMgr_PresentationManager,
    PrsMgr_ListOfPresentableObjects,
    PrsMgr_ListOfPresentableObjectsIter,
    PrsMgr_DisplayStatus_Erased
)
def decorator_run(fun):
    def decorated_fun(*args, **kwargs):
        print(f'Before {fun.__name__}')
        shape = fun(*args, **kwargs)
        print(f'end {fun.__name__}')
        return shape 
    return decorated_fun

@decorator_run

from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display
from OCC.Extend.ShapeFactory import points_to_bspline

from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.AIS import AIS_Shape, AIS_InteractiveContext
from OCC.Core.V3d import V3d_Viewer
from OCC.Core.SelectMgr import (
    SelectMgr_SelectableObject,
    SelectMgr_Selection,
    SelectMgr_ViewerSelector,
    SelectMgr_SelectionManager,
)
from OCC.Core.PrsMgr import (
    PrsMgr_PresentationManager,
    PrsMgr_ListOfPresentableObjects,
    PrsMgr_ListOfPresentableObjectsIter,
    PrsMgr_DisplayStatus_Erased
)
def test_bezier0():
    p1 = gp_Pnt(0, 0, 0)
    p2 = gp_Pnt(0, 1, 0)
    p3 = gp_Pnt(0, 4, 0)
    p = gp_Pnt()
    try:
        line = points_to_bspline([p1, p2, p3])
    except Exception as error:
        print(error)
    return line

def test_aisp_line():


    display, start, *_ = init_display()
    line = test_bezier0()

    builder = BRepBuilderAPI_MakeEdge(line)
    edge = builder.Edge()
    ais = AIS_Shape(edge)
    ctx:AIS_InteractiveContext = display.Context

    ais.ViewAffinity().SetVisible(True)


    viewer = ctx.CurrentViewer()
    viewer.StructureManager().RegisterObject(ais, ais.ViewAffinity())


    prsManager = ctx.MainPrsMgr()
    prsManager.Display(ais, ais.DisplayMode())


    assert ais.GlobalSelectionMode() == 0
    # error exist
    selector:SelectMgr_SelectionManager = ctx.SelectionManager()
    if not selector.Contains(ais):
        selector.Load(ais)

    # print(line.FirstParameter(), line.LastParameter()) # hava a nan nan bound.
    print('next line cause error')


    # selector.Activate(ais, ais.GlobalSelectionMode())
    
    # selMode = ais.GlobalSelectionMode()
    # if True:
    #     it = PrsMgr_ListOfPresentableObjectsIter(ais.Children())
    #     while it.More():
    #         aChild:SelectMgr_SelectableObject = SelectMgr_SelectableObject.DownCast(it.Value())
    #         if aChild.DisplayStatus() != PrsMgr_DisplayStatus_Erased:
    #             selector.Activate(aChild, selMode)
    #         print('pass prsNext')
    #         it.Next()
        
    #     assert ais.HasOwnPresentations()
    #     # compute
    #     aNewSel = SelectMgr_Selection(selMode)
    #     ais.AddSelection(aNewSel, selMode)
        
    #     viewSel:SelectMgr_ViewerSelector = selector.Selector()
        # mySelector->AddSelectionToObject (theObject, aNewSel);
        # aNewSel->UpdateBVHStatus (SelectMgr_TBU_None);

    # print('pass Selector Activate')

    # start()

def test_PerformCurve():
    from OCC.Core.gp import gp_Pnt2d
    from OCC.Core.GCPnts import GCPnts_TangentialDeflection
    from OCC.Core.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Curve2d
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.GC import GC_MakeArcOfCircle
    from OCC.Core.GCE2d import GCE2d_MakeArcOfCircle

    curve = test_bezier0()

    p = gp_Pnt()

    curve = GC_MakeArcOfCircle(p, p, p).Value()
    edge = BRepBuilderAPI_MakeEdge(curve).Edge()
    adaptor = BRepAdaptor_Curve(edge)
    curve, u0, u1 = BRep_Tool.Curve(edge)

    print(f'Curve parameter=({u0}, {u1})')
    print(f'adapt parameter=({adaptor.FirstParameter()}, {adaptor.LastParameter()})')
    import math
    assert math.isnan(u0)
    assert math.isnan(u1)
    # assert adaptor.FirstParameter() == float('nan')
    # assert adaptor.LastParameter() == float('nan')

def test_arcOfCircle2d():
    from OCC.Core.gp import gp_Pnt2d
    from OCC.Core.GCE2d import GCE2d_MakeArcOfCircle

    p_li = [
        gp_Pnt2d(0, 0),
        gp_Pnt2d(0, 2),
        gp_Pnt2d(0, 1),
    ]

    try:
        builder = GCE2d_MakeArcOfCircle(*p_li)
    except Exception as error:
        print(str(error), '\n->Error')

if __name__ == '__main__':
    test_aisp_line()
