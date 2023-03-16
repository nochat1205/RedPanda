
from utils.OCCUtils import (
    FromText,
    TFunction_Logbook,
    TDataStd_Real,
    TDF_Label,
    TDF_LabelList,
    TDataStd_Integer,
    TFunction_Function,
    TColgp_Array1OfPnt
)

from utils.GUID import *
from utils.Sym_Attribute import Sym_GuidAttr
from utils.Driver.Sym_Driver import (
    Sym_Driver,
    GetDriver,
    Param,
    Argument
)
from typing import Union
from utils.decorator import classproperty
from utils.logger import Logger


def GetValueWith(id:Standard_GUID, theLabel:TDF_Label)->any:
    aDriver:Sym_Driver = GetDriver(id)
    return aDriver.GetValue(theLabel)

class Sym_RealDriver(Sym_Driver): # base
    """
    func说明: 不会被继承(增加新属性), 可以使用self
    """

    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TDataStd_Real, "0.0")
        self.Attributes["value"] = self.myAttr

    @classproperty
    def ID(self):
        return Sym_RealDriver_GUID #
    @classproperty
    def Type(self):
        return "real"

class Sym_IntDriver(Sym_Driver):
    """
    func说明: 不会被继承(增加新属性), 可以使用self
    """

    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TDataStd_Integer, "0")
        self.Attributes["value"] = self.myAttr

    @classproperty
    def ID(self):
        return Sym_IntDriver_GUID #

    @classproperty
    def Type(self):
        return "Int"

class Sym_IdDriver(Sym_Driver):

    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(Sym_GuidAttr, "0")
        self.Attributes["value"] = self.myAttr

    @classproperty
    def ID(self):
        return Sym_IdDriver_GUID #

    @classproperty
    def Type(self):
        return "GUID"

class Sym_ArrayDriver(Sym_Driver):
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TDataStd_Integer)
        self.Attributes['size'] = self.myAttr

        self._ArrayFirstTag = 125
        self._SubTypeId = Sym_PntDriver_GUID

    def Init(self, theLabel:TDF_Label, theData: dict)->bool:
        if super()._base_init(theLabel):
            return True

        Logger().info(f'Array size:{len(theData)} data:{theData}')
        TDataStd_Integer.Set(theLabel, len(theData))
        aDriver = GetDriver(self._SubTypeId)
        for name, pnt in theData.items():
            tag = int(name)+self._ArrayFirstTag
            aLabel = theLabel.FindChild(tag)
            aDriver.Init(aLabel, pnt)

        Logger().info('Array Init success.')
        return True

    def GetValue(self, theLabel: TDF_Label):
        aDriver = GetDriver(self._SubTypeId)
    
        aInt = TDataStd_Integer()
        size = 0
        if theLabel.FindAttribute(aInt.GetID(), aInt):
            size = aInt.Get()

        array = TColgp_Array1OfPnt(1, size)
        for i in range(size):
            childLabel = theLabel.FindChild(i+self._ArrayFirstTag, False)
            value = aDriver.GetValue(childLabel)
            array.SetValue(i+1, value)
        Logger().debug(f"Return array{array}")
        return array

    @classproperty
    def ID(self):
        return Sym_ArrayDriver_GUID #

    @classproperty
    def Type(self):
        return "array"

