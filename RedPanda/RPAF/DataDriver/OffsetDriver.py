from OCC.Core.TNaming import TNaming_Builder, TNaming_NamedShape
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.gp import gp_Ax1, gp_Trsf, gp_Ax2, gp_Ax3
from OCC.Core.AIS import AIS_ColoredShape, AIS_Shaded, AIS_Plane, AIS_TOPL_XYPlane
from OCC.Core.Geom import Geom_Axis2Placement

from RedPanda.RPAF.DisplayContext import DisplayCtx
from RedPanda.logger import Logger
from RedPanda.RPAF.RD_Label import Label
from RedPanda.decorator import classproperty

from .BaseDriver import (
    ShapeRefDriver,
    Argument,
    DataLabelState,
)
from .VarDriver import IntDriver, RealDriver

from .ShapeBaseDriver import (
    BareShapeDriver,
)
from .VertexDriver import PntDriver

class ThickSoldDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Shape'] = Argument(self.tagResource, ShapeRefDriver.ID)
        self.Arguments['CutFace'] = Argument(self.tagResource, ShapeRefDriver.ID)
        self.Arguments['Offset'] = Argument(self.tagResource, RealDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeThickSolid
        from OCC.Core.TopExp import TopExp_Explorer
        from OCC.Core.TopAbs import TopAbs_EDGE
        from OCC.Core.TopoDS import topods, TopoDS_ListOfShape
        from RedPanda.Core.data import RP_TOLERANCE
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        try:
            shape = dict_param['Shape']
            face = dict_param['CutFace']
            offset = dict_param['Offset']
            builder = BRepOffsetAPI_MakeThickSolid()
            lis = TopoDS_ListOfShape()
            lis.Append(face)

            builder.MakeThickSolidByJoin(shape, lis, -offset, RP_TOLERANCE*10)
            
            shape = builder.Shape()
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1
        

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0


    @classproperty
    def ID(self):
        from ..GUID import Sym_ThickDriver_GUID
        return  Sym_ThickDriver_GUID #

    @classproperty
    def Type(self):
        return "ThickSolid"


from .TopoDriver import EdgeArrayDriver
class ThruSecDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Wires'] = Argument(self.tagResource, EdgeArrayDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
        from OCC.Core.TopExp import TopExp_Explorer
        from OCC.Core.TopAbs import TopAbs_WIRE, TopAbs_VERTEX

        from RedPanda.Core.data import RP_TOLERANCE
    

        edges:list[TopoDS_Shape] = self.Arguments['wires'].Value(theLabel)
        try:
            builder = BRepOffsetAPI_ThruSections()
            for shape in edges:
                if shape.ShapeType() == TopAbs_WIRE:
                    builder.AddWire(shape)
                elif shape.ShapeType() == TopAbs_VERTEX:
                    builder.AddVertex(shape)
            builder.CheckCompatibility(False)
            shape = builder.Shape()
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0


    @classproperty
    def ID(self):
        from ..GUID import Sym_ThruSecDriver_GUID
        return  Sym_ThruSecDriver_GUID #

    @classproperty
    def Type(self):
        return "ThruSec"

