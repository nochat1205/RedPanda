from OCC.Core.TNaming import TNaming_Builder
from OCC.Core.TopoDS import TopoDS_Shape

from RedPanda.decorator import classproperty

from .BaseDriver import (
    Argument,
    Param,
    DataLabelState
)
from .ShapeBaseDriver import BareShapeDriver
from .ArrayDriver import EdgeArrayDriver

from ..Attribute import TNaming_NamedShape
from ..RD_Label import Label


class WireDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()

        self.Arguments['edges'] = Argument(self.tagResource, EdgeArrayDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire
        from OCC.Core.BRepLib import breplib
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        edges = dict_param['edges']
        try:
            builder = BRepBuilderAPI_MakeWire()
            for edge in edges:
                breplib.BuildCurve3d(edge)
                builder.Add(edge)
            wire = builder.Wire()
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1 

        builder = TNaming_Builder(theLabel)
        builder.Generated(wire)
        return 0

    @classproperty
    def Type(self):
        return 'Wire'

    @classproperty
    def ID(self):
        from ..GUID import Sym_WireDriver_GUID
        return Sym_WireDriver_GUID

from .TopoDriver import EdgeArrayDriver
class CompoudDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Wires'] = Argument(self.tagResource, EdgeArrayDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.BRepBuilderAPI import TopoDS_Compound
        from OCC.Core.BRep import BRep_Builder

        from RedPanda.Core.data import RP_TOLERANCE
    

        edges:list[TopoDS_Shape] = self.Arguments['wires'].Value(theLabel)
        try:
            builder = BRep_Builder()

            comp = TopoDS_Compound()
            builder.MakeCompound(comp)
            for shape in edges:
                builder.Add(comp, shape)

            shape = comp
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0


    @classproperty
    def ID(self):
        from ..GUID import Sym_CompoudDriver_GUID
        return  Sym_CompoudDriver_GUID #

    @classproperty
    def Type(self):
        return "Compoud"

from .BaseDriver import ShapeRefDriver
class NurbsConvtDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['shape'] = Argument(self.tagResource, ShapeRefDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert

        shape = self.Arguments['shape'].Value(theLabel)
        try:
            builder = BRepBuilderAPI_NurbsConvert(shape)
            shape = builder.Shape()
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0


    @classproperty
    def ID(self):
        from ..GUID import Sym_NurbsConvtDriver_GUID
        return  Sym_NurbsConvtDriver_GUID #

    @classproperty
    def Type(self):
        return "Nurbs"

