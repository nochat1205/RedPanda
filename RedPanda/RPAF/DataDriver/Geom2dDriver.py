from OCC.Core.Geom2d import Geom2d_Ellipse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_Plane
from OCC.Core.TNaming import TNaming_Builder
from OCC.Core.BRep import BRep_Tool
from OCC.Extend.ShapeFactory import make_edge2d, make_edge
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.AIS import AIS_Shaded, AIS_ColoredShape
from OCC.Core.PrsDim import PrsDim_DiameterDimension
from OCC.Core.BRepLib import breplib_BuildCurve3d
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_RED

from RedPanda.logger import Logger
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
        ais = AIS_ColoredShape(TopoDS_Shape())
        ais_dict[(theLabel, 'shape')] = ais

        self.UpdatePrs2d(theLabel, ais_dict)

        return ais_dict

    def myUpdatePrs2d(self, theLabel: Label, ais_dict:DisplayCtx):
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
    

        return True

    def Prs3d(self, theLabel):

        ais_dict = DisplayCtx(theLabel)

        ais = AIS_ColoredShape(TopoDS_Shape())
        ais_dict[(theLabel, 'shape')] = ais
        ais.SetDisplayMode(AIS_Shaded)

        aLabel = theLabel.Argument('surface')
        ais = AIS_ColoredShape(TopoDS_Shape())
        ais_dict[(aLabel, 'shape')] = ais

        self.UpdatePrs3d(theLabel, ais_dict)

        return ais_dict

    def myUpdatePrs3d(self, theLabel, ais_dict):
        if not DataLabelState.IsOK(theLabel):
            return False

        ais_dict.SetShape((theLabel, 'shape'), 
                          self.Attributes['value'].GetValue(theLabel))


        shape = self.Arguments['surface'].Value(theLabel)
        ais_dict.SetShape((theLabel.Argument('surface'), 'shape'), shape)

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
        from OCC.Core.Geom2d import Geom2d_TrimmedCurve
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        try:
            surface = BRep_Tool.Surface(dict_param['surface'])
            edge2d = dict_param['edge2d']
            breplib_BuildCurve3d(edge2d)
            curve, u, v = BRep_Tool.CurveOnPlane(edge2d, Geom_Plane(RP_Ax3()), TopLoc_Location())
            curve = Geom2d_TrimmedCurve(curve, u, v)
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
        ais = AIS_ColoredShape(TopoDS_Shape())
        ais_dict[(aLabel, 'shape')] = ais

        self.UpdatePrs2d(theLabel, ais_dict)

        return ais_dict

    def myUpdatePrs2d(self, theLabel: Label, ais_dict:DisplayCtx):
        # 1
        face = self.Arguments['surface'].Value(theLabel)
        surface = BRep_Tool.Surface(face)
        ais_dict.bounds = surface.Bounds()

        # 2
        aLabel = theLabel.Argument('edge2d')
        edge2d = self.Arguments['edge2d'].Value(theLabel)
        breplib_BuildCurve3d(edge2d)
        ais = ais_dict[(aLabel, 'shape')]
        if ais:
            ais.SetShape(edge2d)
            ais.UpdateSelection()
            ais.SetToUpdate()

        return True

    def Prs3d(self, theLabel):

        ais_dict = DisplayCtx(theLabel)

        
        ais = AIS_ColoredShape(TopoDS_Shape())
        ais_dict[(theLabel, 'shape')] = ais


        aLabel = theLabel.Argument('surface')
        ais = AIS_ColoredShape(TopoDS_Shape())
        ais_dict[(aLabel, 'shape')] = ais
        ais.SetDisplayMode(AIS_Shaded)

        self.UpdatePrs3d(theLabel, ais_dict)

        return ais_dict

    def myUpdatePrs3d(self, theLabel:Label, ais_dict):
        if not DataLabelState.IsOK(theLabel):
            return False
        # 1
        shape = self.Attributes['value'].GetValue(theLabel)
        if shape:
            ais_dict.SetShape((theLabel, 'shape'), shape)
        # 2
        aLabel = theLabel.Argument('surface')
        shape = self.Arguments['surface'].Value(theLabel)
        ais_dict.SetShape((aLabel, 'shape'), shape)

        return True

    @classproperty
    def Type(self):
        return 'BuildEdge3d'

    @classproperty
    def ID(self):
        from ..GUID import Sym_Build3dEdgeDriver_GUID
        return Sym_Build3dEdgeDriver_GUID

from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge2d
from .VertexDriver import Pnt2dDriver
class BareShape2dDriver(BareShapeDriver):

    def Prs3d(self, theLabel)->DisplayCtx:
        

        ais_dict = DisplayCtx(theLabel)
        return ais_dict

    def myUpdatePrs3d(self, theLabel, ais_dict:DisplayCtx):
        return False


    def Prs2d(self, theLabel:Label):
        if 'keyPrs2d_1' not in self.__dict__:
            self.keyPrs2d_1 = (theLabel, 'shape')

        ais_dict = DisplayCtx(theLabel)
        ais = AIS_ColoredShape(TopoDS_Shape())
        ais.SetColor(Quantity_Color(Quantity_NOC_RED))
        ais_dict[self.keyPrs2d_1] = ais

        self.UpdatePrs2d(theLabel, ais_dict)

        return ais_dict
    
    def myUpdatePrs2d(self, theLabel:Label, ais_dict:DisplayCtx):
        if not DataLabelState.IsOK(theLabel):
            return False
        Logger().debug(f"ID:{self.ID}")
        ais:AIS_ColoredShape = ais_dict[self.keyPrs2d_1]
        shape = self.Attributes['value'].GetValue(theLabel)
        breplib_BuildCurve3d(shape)
        if ais and shape:
            ais.SetShape(shape)
            ais.SetColor(Quantity_Color(Quantity_NOC_RED))
            ais.SetToUpdate()
            ais.UpdateSelection()

        return True

class Shape2dDriver(BareShape2dDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Ax'] = Argument(self.tagResource, Ax2dDriver.ID)

class Segment2dDriver(BareShape2dDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['p1'] = Argument(self.tagResource, Pnt2dDriver.ID)
        self.Arguments['p2'] = Argument(self.tagResource, Pnt2dDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.GCE2d import GCE2d_MakeSegment

        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        try:
            seg = GCE2d_MakeSegment(dict_param['p1'], dict_param['p2']).Value()
            edge = BRepBuilderAPI_MakeEdge2d(seg).Edge()
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(edge)
        return 0

    @classproperty
    def Type(self):
        return 'Seg2d'

    @classproperty
    def ID(self):
        from ..GUID import Sym_Seg2dDriver_GUID
        return Sym_Seg2dDriver_GUID

class ArcCircleDriver(BareShape2dDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['p1'] = Argument(self.tagResource, Pnt2dDriver.ID)
        self.Arguments['p2'] = Argument(self.tagResource, Pnt2dDriver.ID)
        self.Arguments['p3'] = Argument(self.tagResource, Pnt2dDriver.ID)
    
    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.GCE2d import GCE2d_MakeArcOfCircle

        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        try:
            builder  = GCE2d_MakeArcOfCircle(
                dict_param['p1'], dict_param['p2'], dict_param['p3'])
            if builder.IsDone():
                seg = builder.Value()
                edge = BRepBuilderAPI_MakeEdge2d(seg).Edge()
            else:
                raise Exception('param error')
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(edge)
        return 0

    @classproperty
    def Type(self):
        return 'ArcCircle'

    @classproperty
    def ID(self):
        from ..GUID import Sym_ArcCir2dDriver_GUID
        return Sym_ArcCir2dDriver_GUID

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

class TrimmedCurveDriver(BareShape2dDriver):
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

