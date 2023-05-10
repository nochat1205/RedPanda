
from RedPanda.logger import Logger
from RedPanda.decorator import classproperty
from RedPanda.RPAF.GUID import *

from RedPanda.Core.Make import (
    boolean_cut
)

from ..Attribute import (
    XCAFDoc_Location,
    TNaming_NamedShape,
    TNaming_Builder,
)
from ..RD_Label import Label
from .BaseDriver import (
    Argument,
    Param,
    ShapeRefDriver,
    DataLabelState
)
from .ShapeBaseDriver import BareShapeDriver

class CutDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TNaming_NamedShape.GetID())
        self.Attributes['value'] = self.myAttr
        self.Arguments['beCutShape'] = Argument(self.tagResource, ShapeRefDriver.ID),
        self.Arguments['cutShape'] = Argument(self.tagResource, ShapeRefDriver.ID)


    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        shape0 = dict_param['beCutShape']
        shape1 = dict_param['cutShape']
        try:
            shape = BRepAlgoAPI_Cut(shape0, shape1).Shape()
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1
        if shape:
            builder = TNaming_Builder(theLabel)
            builder.Generated(shape)

            return 0

        return 1

    @classproperty
    def ID(self):
        return  Sym_CutDriver_GUID #

    @classproperty
    def Type(self):
        return "Cut"

class FuseDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Attributes['value'] = Param(TNaming_NamedShape.GetID())
        self.Arguments['Shape0'] = Argument(self.tagResource, ShapeRefDriver.ID)
        self.Arguments['Shape1'] = Argument(self.tagResource, ShapeRefDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        shape0 = dict_param['Shape0']
        shape1 = dict_param['Shape1']
        try:
            shape = BRepAlgoAPI_Fuse(shape0, shape1).Shape()
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1
        if  shape is None:
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0

    @classproperty
    def Type(self):
        return 'Fuse'

    @classproperty
    def ID(self):
        from ..GUID import Sym_FuseDriver_GUID
        return Sym_FuseDriver_GUID


