
__all__ = ['PntDriver']

from RedPanda.logger import Logger
from RedPanda.decorator import classproperty

from RedPanda.RPAF.GUID import *
from RedPanda.Core.topogy import (
    make_vertex,
    VertexAnalyst
)
from RedPanda.Core.Euclid import (
    RP_Pnt,
    RP_Pnt_Array
)

from RedPanda.Core.data import RP_AsciiStr

from .BaseDriver import (
    DataDriver,
    Argument,
    Param
)
from ..Attribute import (
    TNaming_NamedShape,
    TNaming_Builder,
    TDataStd_Integer
)
from .BaseDriver import (
    ArrayDriver
)
from .VarDriver import (
    RealDriver,
)
from .ShapeBaseDriver import BareShapeDriver

from ..RD_Label import Label
from ..DriverTable import DataDriverTable


class PntDriver(BareShapeDriver):
    _type = 'Point'
    _guid = Sym_PntDriver_GUID
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TNaming_NamedShape.GetID())
        self.Attributes["value"] = self.myAttr
        self.Arguments = {
            'theXp': Argument(self.tagResource, RealDriver.ID), 
            'theYp': Argument(self.tagResource, RealDriver.ID),
            'theZp': Argument(self.tagResource, RealDriver.ID),
        }

    def Execute(self, theLabel: Label) -> int:
        param_dict = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            param_dict[name] = argu.Value(theLabel)

        pnt = RP_Pnt(param_dict["theXp"], param_dict["theYp"], param_dict["theZp"])
        pnt = make_vertex(pnt)

        AttrType = self.Attributes['value'].Type
        builder = TNaming_Builder(theLabel)
        builder.Generated(pnt)

        return 0

    @classproperty
    def ID(self):
        return PntDriver._guid #

    @classproperty
    def Type(self):
        return PntDriver._type

class PntArrayDriver(ArrayDriver):
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TDataStd_Integer.GetID())
        self.Attributes['size'] = self.myAttr

        self._ArrayFirstTag = 125
        self._SubTypeId = Sym_PntDriver_GUID

    def GetValue(self, theLabel: Label):
        aDriver = DataDriverTable.Get().GetDriver(self._SubTypeId)
    
        size = self.GetSize()

        pnt_li = list()
        for i in range(size):
            childLabel = theLabel.FindChild(i+self._ArrayFirstTag, False)
            value = aDriver.GetValue(childLabel)
            pnt_li.append(value)

        return pnt_li

    @classproperty
    def ID(self):
        return Sym_ArrayDriver_GUID #

    @classproperty
    def Type(self):
        return "array"

