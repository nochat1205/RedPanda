import os,sys
from typing import Optional

from OCC.Core.V3d import Prs3d_Drawer
sys.path.append(os.getcwd()) 

from OCC.Core.AIS import AIS_InteractiveObject
from OCC.Core.PrsMgr import Prs3d_Drawer, PrsMgr_PresentationManager
from OCC.Core.Prs3d import Prs3d_Presentation, Prs3d_PresentationShadow
from OCC.Core.SelectMgr import SelectMgr_Selection
from OCC.Core.Prs3d import Prs3d_Drawer
from OCC.Core.Graphic3d import Graphic3d_NameOfMaterial_Silver
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.gp import gp_Trsf
from OCC.Core.TopLoc import TopLoc_Loaction

from OCC.Core.SelectMgr import SelectMgr_EntityOwner
'''
Primitive arrays
Prs3d_Presentation might be filled in by the following primitives:

Triangles
    - Graphic3d_ArrayOfTriangles
    - Graphic3d_ArrayOfTriangleFans
    - Graphic3d_ArrayOfTriangleStrips
Lines
    - Graphic3d_ArrayOfSegments
    - Graphic3d_ArrayOfPolylines
Points or Markers
    - Graphic3d_ArrayOfPoints
'''


# StdPrs makes it easy to display topological shapes.
class MyAisObject(AIS_InteractiveObject):
    MyDispMode_Main = 0
    MyDispMode_Highlight = 1
    def __init__(self) -> None:
        super().__init__() # error
        self.myDrawer:Prs3d_Drawer = Prs3d_Drawer()
        self.SetDisplayMode(self.MyDispMode_Main)
        self.SetHilightMode(self.MyDispMode_Highlight)
        
        self.myDrawer.SetupOwnShadingAspect()
        self.myDrawer.ShadingAspect().SetMaterial(Graphic3d_NameOfMaterial_Silver)
        # self.myDrawer.SetWireAspect(Prse)

        # Selection and presentation are two independent mechanisms in AIS.
        # Presentation rendering is done with help of OpenGL or a similar low-level graphics library, while selection doesn't depend on a graphic driver at all. 

    def Compute(self, 
                thePrsMgr:PrsMgr_PresentationManager, 
                thePrs:Prs3d_Presentation, # Graphic3d_Structure
                theMode):
        from OCC.Core.gp import gp_Pnt
        from OCC.Core.TopoDS import TopoDS_Shape
        from OCC.Core.StdPrs import StdPrs_ShadedShape, StdPrs_WFShape
        from OCC.Core.Graphic3d import (
            Graphic3d_ArrayOfSegments,
            Graphic3d_ArrayFlags_None,
            Graphic3d_Aspects,
            Graphic3d_TypeOfShadingModel_Unlit
        )
        from OCC.Core.Quantity import Quantity_NOC_RED, Quantity_Color

        # defining an object presentation
        if not self.AcceptDisplayMode(theMode): 
            return
            # reject non-zero display modes

        anAspects = Graphic3d_Aspects()
        anAspects.SetShadingModel(Graphic3d_TypeOfShadingModel_Unlit)
        anAspects.SetColor(Quantity_Color(Quantity_NOC_RED))
        
        aRadius = 100
        aHeight = 100
        aShape:TopoDS_Shape  = BRepPrimAPI_MakeCylinder (aRadius, aHeight)
        if theMode == self.MyDispMode_Main:
            StdPrs_ShadedShape.Add (thePrs, aShape, self.myDrawer)
            StdPrs_WFShape.Add (thePrs, aShape, self.myDrawer) # add wireframe
            aSegs = Graphic3d_ArrayOfSegments(4, 4*2,
                                              Graphic3d_ArrayFlags_None)
            aSegs.AddVertex(gp_Pnt(0, -aRadius, 0))
            aSegs.AddVertex(gp_Pnt(0, -aRadius, aHeight))
            aSegs.AddVertex(gp_Pnt(0,  aRadius, aHeight))
            aSegs.AddVertex(gp_Pnt(0,  aRadius, 0))
            aSegs.AddEdges(1, 2)
            aSegs.AddEdges(2, 3)
            aSegs.AddEdges(3, 4)
            aSegs.AddEdges(4, 1)

            # Create a new Graphic3d_Group using Prs3d_Presentation::NewGroup();
            aGroupSegs = thePrs.NewGroup()
            # Specify presentation aspects using Graphic3d_Group::SetGroupPrimitivesAspect()
            aGroupSegs.SetPrimitivesAspect(anAspects)
            # Create and add an array of primitives using Graphic3d_Group::AddPrimitiveArray().
            aGroupSegs.AddPrimitiveArray(aSegs)

        elif theMode == 1:
            from OCC.Core.BRepBndLib import brepbndlib
            from OCC.Core.Prs3d import Prs3d_BndBox

            aBox = Bnd_Box()
            aBox.Add(aShape)


            brepbndlib.Add(aShape, aBox)
            Prs3d_BndBox.Add(thePrs, aBox, self.myDrawer)
        
        pass
    

    def ComputeSelection(self, 
                         theSelection: SelectMgr_Selection, 
                         theMode: int) -> None:
        from OCC.Core.Select3D import Select3D_SensitiveBox, Select3D_SensitivePrimitiveArray
        from OCC.Core.StdPrs import StdPrs_ToolTriangulatedShape
        from OCC.Core.StdSelect import StdSelect_BRepSelectionTool
        from OCC.Core.TopAbs import TopAbs_SHAPE
        from OCC.Core.Prs3d import Prs3d_ToolCylinder
        '''
    This method should fill in the SelectMgr_Selection argument 
    with SelectMgr_SensitiveEntity entities defining selectable elements 
    - triangulations, polylines, points and their composition. 
    Select3D_SensitiveBox is probably the simplest way to define selectable volume 
    - by it's bounding box:

You may see this object in methods like AIS_InteractiveContext::DetectedOwner(), 
Owners are stored within the list of selection objects AIS_Selection 
and it received by methods like AIS_InteractiveContext::SetSelected() 
and AIS_InteractiveContext::AddOrRemoveSelected().

From the Selector's point of view, AIS_InteractiveObject is just 
a drawer for SelectMgr_EntityOwner.
        '''


        # defining a selectable (pickable) volume.
        aRadius = 100
        aHeight = 100
        anOwer = SelectMgr_EntityOwner(self)
        
        aShape = BRepPrimAPI_MakeCylinder(aRadius, aHeight).Shape()

        # aBox = Bnd_Box()
        # aBox.Add(aShape)
        # aSensBox = Select3D_SensitiveBox(anOwer, aBox)
        # theSelection.Add(aSensBox)
        '''
        In a similar way as StdPrs_ShadedShape is a presentation builder for TopoDS_Shape, 
        the StdSelect_BRepSelectionTool can be seen as a standard selection builder for shapes:

        '''
        aDefl = StdPrs_ToolTriangulatedShape.GetDeflection(aShape, self.myDrawer)
        '''
        Internally, StdSelect_BRepSelectionTool iterates over sub-shapes 
        and appends to the Selection (theSel) entities like 
        Select3D_SensitiveTriangulation (for faces) and 
        Select3D_SensitiveCurve (for edges).


        '''

        StdSelect_BRepSelectionTool.Load(theSelection, self, aShape, TopAbs_SHAPE,
                                         aDefl, self.myDrawer.DeviationAngle(),
                                         self.myDrawer.IsAutoTriangulation())
        '''
        Previously, we have used Prs3d_ToolCylinder to triangulate a cylinder, 
        so let's try to construct Select3D_SensitivePrimitiveArray from the same triangulation:
        '''
        aTris = Prs3d_ToolCylinder.Create(aRadius, aRadius, aHeight, 25, 25, gp_Trsf())
        aSenTri = Select3D_SensitivePrimitiveArray(anOwer)
        aSenTri.InitTriangulation(aTris.Attributes(), aTris.Indices(), TopLoc_Loaction())
        theSelection.Add(aSenTri)


    def AcceptDisplayMode(self, theMode: int) -> bool:
        accept = (self.MyDispMode_Main, self.MyDispMode_Highlight)
        return theMode in accept

class MyAisOwner(SelectMgr_EntityOwner):
    def __init__(self, theObj, thePriority=0):
        super().__init__(theObj, thePriority)
    
    def HilightWithColor(self, thePrsMgr: PrsMgr_PresentationManager, theStyle: Prs3d_Drawer, theMode: int  = 0) -> None:
        # void SelectMgr_EntityOwner::HilightWithColor (
        # const Handle(PrsMgr_PresentationManager)& thePrsMgr,
        # const Handle(Prs3d_Drawer)& theStyle,
        # const Standard_Integer theMode)
        # {
        # const Graphic3d_ZLayerId aHiLayer =
        #     theStyle->ZLayer() != Graphic3d_ZLayerId_UNKNOWN
        #     ? theStyle->ZLayer()
        #     : mySelectable->ZLayer();
        # thePrsMgr->Color (mySelectable, theStyle, theMode, NULL, aHiLayer);
        # }
        if self.myPrs.IsNull():
            self.myPrs = Prs3d_Presentation(thePrsMgr.StructureManager)
            anObj:MyAisObject = MyAisObject.DownCast(self.mySelectable)
            anObj.Compute(thePrsMgr, self.myPrs, anObj.MyDispMode_Highlight)
        if thePrsMgr.IsImmediateModeOn():
            from OCC.Core.Graphic3d import Graphic3d_ZlayerId_Top
            aShadow = Prs3d_PresentationShadow(thePrsMgr.StructureManager(), self.myPrs)
            aShadow.SetZLayer(Graphic3d_ZlayerId_Top)
            aShadow.Highlight(theStyle)
            thePrsMgr.AddToImmediateList(aShadow)

        else:
            self.myPrs.Display()

        # return super().HilightWithColor(thePrsMgr, theStyle, theMode)
    
    def Unhilight(self, thePrsMgr: PrsMgr_PresentationManager, theMode: int  = 0) -> None:
        if not self.myPrs.IsNull():
            self.myPrs.Erase()
    
        # return super().Unhilight(thePrsMgr, theMode)




