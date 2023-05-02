import os,sys
sys.path.append(os.getcwd()) 

from OCC.Core.AIS import AIS_InteractiveObject
from OCC.Core.PrsMgr import PrsMgr_PresentationManager
from OCC.Core.Prs3d import Prs3d_Presentation
from OCC.Core.SelectMgr import SelectMgr_Selection


# StdPrs makes it easy to display topological shapes.
class MyAisObject(AIS_InteractiveObject):
    def __init__(self) -> None:
        super().__init__() # error
        self.myDrawer = None
        self.SetDisplayMode(0)
        self.SetHilightMode(1)

        # Selection and presentation are two independent mechanisms in AIS.
        # Presentation rendering is done with help of OpenGL or a similar low-level graphics library, while selection doesn't depend on a graphic driver at all. 

    def Compute(self, 
                thePrsMgr:PrsMgr_PresentationManager, 
                thePrs:Prs3d_Presentation, 
                theMode):
        from OCC.Core.TopoDS import TopoDS_Shape
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        from OCC.Core.StdPrs import StdPrs_ShadedShape, StdPrs_WFShape

        # defining an object presentation
        if not self.AcceptDisplayMode(theMode): 
            return
            # reject non-zero display modes
        aShape:TopoDS_Shape  = BRepPrimAPI_MakeCylinder (100.0, 100.0);
        if theMode == 0:

            StdPrs_ShadedShape.Add (thePrs, aShape, self.myDrawer)
            StdPrs_WFShape.Add (thePrs, aShape, self.myDrawer) # add wireframe
        elif theMode == 1:
            from OCC.Core.Bnd import Bnd_Box
            from OCC.Core.BRepBndLib import brepbndlib
            from OCC.Core.Prs3d import Prs3d_BndBox

            aBox = Bnd_Box()
            brepbndlib.Add(aShape, aBox)
            Prs3d_BndBox.Add(thePrs, aBox, self.myDrawer)
            
            
        
        pass
    

    def ComputeSelection(self, 
                         theSelection: SelectMgr_Selection, 
                         theMode: int) -> None:
        # defining a selectable (pickable) volume.
        return super().ComputeSelection(theSelection, theMode)

    def AcceptDisplayMode(self, theMode: int) -> bool:
        accept = (0, 1)
        return theMode in accept


    
