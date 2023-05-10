from OCC.Core.TNaming import TNaming_Builder

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
        from OCC.Core.BRepLib import breplib_BuildCurve3d
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        edges = dict_param['edges']
        try:
            builder = BRepBuilderAPI_MakeWire()
            for edge in edges:
                breplib_BuildCurve3d(edge)
                builder.Add(edge)
            wire = builder.Wire()
        except Exception as error:
            DataLabelState.SetError(theLabel, 'wire array Error', True)
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
