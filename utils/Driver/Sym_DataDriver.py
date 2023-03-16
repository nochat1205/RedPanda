
from utils.OCCUtils import (
    FromText,
    TFunction_Logbook,
    TDataStd_Real,
    TDF_Label,
    TDF_LabelList,
    TDataStd_Integer,
    TFunction_Function,
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

    def Init(self, L: TDF_Label) -> bool:
        if super().Init(L):
            return True

        TDataStd_Real.Set(L, '0.0')
        return False


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

    def Init(self, L: TDF_Label) -> bool:
        if super().Init(L):
            return True

        TDataStd_Integer.Set(L, 0)
        return False

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

    def Init(self, L: TDF_Label) -> bool:
        if super().Init(L):
            return True

        Sym_GuidAttr.Set(L, Standard_GUID() )
        return False

    @classproperty
    def ID(self):
        return Sym_IdDriver_GUID #

    @classproperty
    def Type(self):
        return "GUID"

class Sym_ArrayDriver(Sym_Driver):
    def __init__(self) -> None:
        super().__init__()
        # self.Attributes['value'] = self.myAttr
        self._ArrayFirstTag = 125
        self._SubTypeId = Standard_GUID()
        self.Arguments = {
            'size': Argument(self.tagResource, Sym_IntDriver.ID),
        }

    def Init(self, L: TDF_Label) -> bool:
        if super().Init(L):
            return True

        return False

    def ChangeValue(self, theLabel: TDF_Label, real_param:Union[dict, str]):
        return super().ChangeValue(theLabel, real_param)

    def GetValue(self, theLabel: TDF_Label):
        
        return

    @classproperty
    def ID(self):
        return Sym_ArrayDriver_GUID #

    @classproperty
    def Type(self):
        return "array"

