
__all__ = [
    'RealDriver',
    'IntDriver',
    'IdDriver',
]

from typing import Union
from RedPanda.decorator import classproperty
from RedPanda.logger import Logger
from RedPanda.RPAF.GUID import *
from RedPanda.Core.Euclid import (
    RP_Pnt_Array
)


from ..Attribute import (
    TDataStd_Real,
    TDataStd_Integer,
    Attr_Guid,
)
from ..DriverTable import DataDriverTable
from ..RD_Label import Label
from .BaseDriver import (
    VarDriver,
    Param,
    Argument,
    DataEnum,
    ArrayDriver
)


class RealDriver(VarDriver): # base
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TDataStd_Real.GetID(), "0.0")
        self.Attributes["value"] = self.myAttr

    @classproperty
    def ID(self):
        return Sym_RealDriver_GUID #

    @classproperty
    def Type(self):
        return "real"

class IntDriver(VarDriver):
    """
    func说明: 不会被继承(增加新属性), 可以使用self
    """

    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TDataStd_Integer.GetID(), "0")
        self.Attributes["value"] = self.myAttr

    @classproperty
    def ID(self):
        return Sym_IntDriver_GUID #

    @classproperty
    def Type(self):
        return "Int"

class IdDriver(VarDriver):
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(Attr_Guid.GetID(), "0")
        self.Attributes["value"] = self.myAttr

    @classproperty
    def ID(self):
        return Sym_IdDriver_GUID #

    @classproperty
    def Type(self):
        return "GUID"
