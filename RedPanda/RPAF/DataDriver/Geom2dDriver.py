from OCC.Core.Geom2d import Geom2d_Ellipse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_Plane
from OCC.Core.AIS import AIS_Shape
from OCC.Core.TNaming import TNaming_Builder
from OCC.Core.BRep import BRep_Tool
from OCC.Extend.ShapeFactory import make_edge2d, make_edge
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.AIS import AIS_Shaded
from OCC.Core.PrsDim import PrsDim_DiameterDimension
from OCC.Core.BRepLib import breplib_BuildCurve3d
from OCC.Core.XCAFPrs import XCAFPrs_AISObject


from RedPanda.RPAF.RD_Label import Label

from RedPanda.decorator import classproperty
from RedPanda.Core.topogy import EdgeAnalyst
from RedPanda.Core.Euclid import RP_Ax3

from .BaseDriver import Argument, ShapeRefDriver, DataLabelState
from .ShapeBaseDriver import BareShapeDriver, Ax2dDriver
from .VarDriver import RealDriver
from ..RD_Label import Label
from ..DisplayContext import DisplayCtx

class PCurveDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['surface'] = Argument(self.tagResource, ShapeRefDriver.ID)

    def myValue(self, theLabel):
        edge = self.Attributes['value'].GetValue(theLabel)
        return edge

    def myValue2d(self, theLabel):
        from OCC.Core.BRep import BRep_Tool
        edge = self.myValue(theLabel)
        face = self.Arguments['surface'].Value(theLabel)
        curve, p0, p1 = BRep_Tool.CurveOnSurface(edge, face)
        return curve

class Ellipse2dDriver(PCurveDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Ax'] = Argument(self.tagResource, Ax2dDriver.ID)
        self.Arguments['Major'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['Minor'] = Argument(self.tagResource, RealDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)
        
        try:
            
            ellipse1 = Geom2d_Ellipse(dict_param['Ax'], 
                                    dict_param['Major'], dict_param['Minor'])
            
            face = BRep_Tool.Surface(dict_param['surface'])
            edge  = make_edge(ellipse1, face)
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(edge)
        return 0

    def Prs2d(self, theLabel: Label):
        ais_dict = DisplayCtx(theLabel)
        ais = XCAFPrs_AISObject(theLabel)
        ais_dict[(theLabel, 'shape')] = ais

        return ais_dict

    def UpdatePrs2d(self, theLabel: Label, ais_dict:DisplayCtx):
        if not DataLabelState.IsOK(theLabel):
            return False
        
        # 1
        face = self.Arguments['surface'].Value(theLabel)
        surface = BRep_Tool.Surface(face)
        ais_dict.bounds = surface.Bounds()

        # 2
        geom2d = self.myValue2d(theLabel)

        edge = make_edge2d(geom2d)
        breplib_BuildCurve3d(edge)

        ais = ais_dict[(theLabel, 'shape')]
        ais.SetShape(edge)
        ais.UpdateSelection()
        ais.SetToUpdate()

        return True

    def Prs3d(self, theLabel):

        ais_dict = DisplayCtx(theLabel)

        ais = XCAFPrs_AISObject(theLabel)
        ais_dict[(theLabel, 'shape')] = ais
        ais.SetDisplayMode(AIS_Shaded)

        aLabel = theLabel.Argument('surface')
        ais = XCAFPrs_AISObject(aLabel)
        ais_dict[(aLabel, 'shape')] = ais

        return ais_dict

    def UpdatePrs3d(self, theLabel, ais_dict):
        if not DataLabelState.IsOK(theLabel):
            return False

        ais = ais_dict[(theLabel, 'shape')]
        ais.SetShape(self.Attributes['value'].GetValue(theLabel))
        ais.SetDisplayMode(AIS_Shaded)

        ais.UpdateSelection()
        ais.SetToUpdate()

        ais = ais_dict[(theLabel.Argument('surface'), 'shape')]
        shape = self.Arguments['surface'].Value(theLabel)
        ais .SetShape(shape)
        ais.UpdateSelection()
        ais.SetToUpdate()

        return True

    def Type(self):
        return 'EllipseDriver'

    @classproperty
    def ID(self):
        from ..GUID import Sym_EllipseDriver_GUID
        return   Sym_EllipseDriver_GUID 

    @classproperty
    def Type(self):
        return "Ellipse"


class Build3dDriver(PCurveDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['edge2d'] = Argument(self.tagResource, ShapeRefDriver.ID)
    
    def myExecute(self, theLabel: Label) -> int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        try:
            surface = BRep_Tool.Surface(dict_param['surface'])
            edge2d = dict_param['edge2d']
            breplib_BuildCurve3d(edge2d)
            curve, u, v = BRep_Tool.CurveOnPlane(edge2d, Geom_Plane(RP_Ax3()), TopLoc_Location())
            
            edge = BRepBuilderAPI_MakeEdge(curve, surface).Edge()
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(edge)

        return 0

    def Prs2d(self, theLabel:Label):
        ais_dict = DisplayCtx(theLabel)
        aLabel = theLabel.Argument('edge2d')
        ais = AIS_Shape(TopoDS_Shape())
        ais_dict[(aLabel, 'shape')] = ais
        print('prs2d:', aLabel.GetEntry())

        return ais_dict

    def UpdatePrs2d(self, theLabel: Label, ais_dict:DisplayCtx):
        if not DataLabelState.IsOK(theLabel):
            return False

        # 1
        face = self.Arguments['surface'].Value(theLabel)
        surface = BRep_Tool.Surface(face)
        ais_dict.bounds = surface.Bounds()
        
        # 2
        aLabel = theLabel.Argument('edge2d')
        edge2d = self.Arguments['edge2d'].Value(theLabel)
        breplib_BuildCurve3d(edge2d)
        ais = ais_dict[(aLabel, 'shape')]
        ais.SetShape(edge2d)
        ais.UpdateSelection()
        ais.SetToUpdate()

        return True

    def Prs3d(self, theLabel):

        ais_dict = DisplayCtx(theLabel)

        
        ais = XCAFPrs_AISObject(theLabel)
        ais_dict[(theLabel, 'shape')] = ais


        aLabel = theLabel.Argument('surface')
        ais = AIS_Shape(TopoDS_Shape())
        ais_dict[(aLabel, 'shape')] = ais
        ais.SetDisplayMode(AIS_Shaded)


        return ais_dict

    def UpdatePrs3d(self, theLabel:Label, ais_dict):
        if not DataLabelState.IsOK(theLabel):
            return False
        # 1
        ais = ais_dict[(theLabel, 'shape')]
        ais.SetShape(self.Attributes['value'].GetValue(theLabel))
        ais.SetDisplayMode(AIS_Shaded)
        ais.UpdateSelection()
        ais.SetToUpdate()
        
        # 2
        aLabel = theLabel.Argument('surface')
        shape = self.Arguments['surface'].Value(theLabel)
        ais = ais_dict[(aLabel, 'shape')]
        ais .SetShape(shape)
        ais.UpdateSelection()
        ais.SetToUpdate()

        return True

    @classproperty
    def Type(self):
        return 'BuildEdge3d'

    @classproperty
    def ID(self):
        from ..GUID import Sym_Build3dEdgeDriver_GUID
        return Sym_Build3dEdgeDriver_GUID

class BareShape2dDriver(BareShapeDriver):
    pass

class Shape2dDriver(BareShape2dDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Ax'] = Argument(self.tagResource, Ax2dDriver.ID)


class Elps2dDriver(Shape2dDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Major'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['Minor'] = Argument(self.tagResource, RealDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        try:
            elps = Geom2d_Ellipse(dict_param['Ax'], 
                                  dict_param['Major'],
                                  dict_param['Minor'])
            edge = make_edge2d(elps)
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(edge)

        return 0

    @classproperty
    def Type(self):
        return 'Ellipse2d'

    @classproperty
    def ID(self):
        from ..GUID import Sym_Elps2dDriver_GUID
        return Sym_Elps2dDriver_GUID

class TrimmedCurveDriver(Shape2dDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['edge2d'] = Argument(self.tagResource, ShapeRefDriver.ID)
        self.Arguments['u1'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['u2'] = Argument(self.tagResource, RealDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        try:
            edge2d = dict_param['edge2d']
            breplib_BuildCurve3d(edge2d)
            curve, u, v = BRep_Tool.CurveOnPlane(edge2d, Geom_Plane(RP_Ax3()), TopLoc_Location())
            edge = make_edge2d(curve, dict_param['u1'], dict_param['u2'])
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(edge)

        return 0

    @classproperty
    def Type(self):
        return 'TrimmedCurve2d'

    @classproperty
    def ID(self):
        from ..GUID import Sym_TrimmedCurve2d_GUID
        return Sym_TrimmedCurve2d_GUID


