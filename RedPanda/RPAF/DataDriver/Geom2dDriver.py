from OCC.Core.Geom2d import Geom2d_Ellipse
from OCC.Core.AIS import AIS_Shape
from OCC.Core.TNaming import TNaming_Builder
from OCC.Core.BRep import BRep_Tool
from OCC.Extend.ShapeFactory import make_edge2d, make_edge
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.AIS import AIS_Shaded

from RedPanda.RPAF.RD_Label import Label

from RedPanda.decorator import classproperty
from RedPanda.Core.topogy import EdgeAnalyst


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
        curve, u, v = BRep_Tool.CurveOnSurface(edge, face)
        print(type(curve), type(u), type(v))
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
        ais = AIS_Shape(TopoDS_Shape())
        ais_dict[('self', 'shape')] = ais

        return ais_dict

    def UpdatePrs2d(self, theLabel: Label, ais_dict:DisplayCtx):
        if not DataLabelState.IsOK(theLabel):
            return False
        # 1
        face = self.Arguments['surface'].Value(theLabel)
        surface = BRep_Tool.Surface(face)
        ais_dict.u0, ais_dict.u1, ais_dict.v0, ais_dict.v1 = surface.Bounds()

        # 2
        geom2d = self.myValue2d(theLabel)

        edge = make_edge2d(geom2d)
        ais = ais_dict[('self', 'shape')]
        ais.SetShape(edge)
        ais.UpdateSelection()
        ais.SetToUpdate()
        return True

    def Prs3d(self, theLabel):

        ais_dict = DisplayCtx(theLabel)

        ais = AIS_Shape(TopoDS_Shape())
        ais_dict[('self', 'shape')] = ais
        ais.SetDisplayMode(AIS_Shaded)

        ais2 = AIS_Shape(TopoDS_Shape())
        ais_dict[('surface', 'shape')] = ais2

        return ais_dict

    def UpdatePrs3d(self, theLabel, ais_dict):
        if not DataLabelState.IsOK(theLabel):
            return False

        ais = ais_dict[('self', 'shape')]
        ais.SetShape(self.Attributes['value'].GetValue(theLabel))
        ais.SetDisplayMode(AIS_Shaded)

        ais.UpdateSelection()
        ais.SetToUpdate()

        ais = ais_dict[('surface', 'shape')]
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
