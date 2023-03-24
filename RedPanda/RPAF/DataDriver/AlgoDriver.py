
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
    ShapeDriver,
    Argument,
    Param,
    ShapeRefDriver
)
from .VarDriver import (
    RealDriver,
)
from .VertexDriver import (
    PntDriver,
)


class CutDriver(ShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        Logger().debug("end init "+str(self.ID))
        self.myAttr = Param(TNaming_NamedShape.GetID())
        self.Attributes['value'] = self.myAttr
        self.Arguments = {
            'beCutShape': Argument(self.tagResource, ShapeRefDriver.ID),
            'cutShape': Argument(self.tagResource, ShapeRefDriver.ID)
        }

    def Execute(self, theLabel: Label) -> int:
        super().Execute(theLabel)
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            value = argu.Value(theLabel)
            dict_param[name] = value

        shape0 = dict_param['beCutShape']
        shape1 = dict_param['cutShape']

        shape = boolean_cut(shape0, shape1)

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0

    @classproperty
    def ID(self):
        return  Sym_CutDriver_GUID #

    @classproperty
    def Type(self):
        return "Cut"
