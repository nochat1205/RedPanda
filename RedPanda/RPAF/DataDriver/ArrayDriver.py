from OCC.Core.BRep import BRep_Tool
from RedPanda.RPAF.RD_Label import Label

from RedPanda.decorator import classproperty

from .BaseDriver import (
    ArrayDriver,
    ShapeRefDriver,
    Param,
)

from ..Attribute import TDataStd_Integer
from ..RD_Label import Label
from ..DriverTable import DataDriverTable

class EdgeArrayDriver(ArrayDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Attributes['size'] = Param(TDataStd_Integer.GetID())
        self._SubTypeId = ShapeRefDriver.ID

    def myValue(self, theLabel:Label):
        aDriver = DataDriverTable.Get().GetDriver(self._SubTypeId)
        size = self.GetSize(theLabel)

        edge_li = list()
        for i in range(size):
            childLabel = theLabel.FindChild(i+self._ArrayFirstTag, False)
            value = aDriver.GetValue(childLabel)
            edge_li.append(value)

        return edge_li



    @classproperty
    def ID(self):
        from ..GUID import Sym_EdgeArrDriver_GUID
        return Sym_EdgeArrDriver_GUID #

    @classproperty
    def Type(self):
        return "EdgeArray"
