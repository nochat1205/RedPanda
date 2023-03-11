
from utils.OCCUtils import (
    FromText,
    TFunction_Logbook,
    TDataStd_Real,
    TDF_Label,
    TDF_LabelList
)

from utils.GUID import *

from utils.Driver.Sym_Driver import (
    Sym_Driver,
    GetDriver,
    Param,
    Argument
)
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

        attr = self.myAttr
        aType = attr.Type
        aType.Set(L, FromText(aType, attr.Default) )
        return False

    def Execute(self, theLabel:TDF_Label, log: TFunction_Logbook) -> int:
        return 0

    def GetValue(self, theLabel:TDF_Label)->any:
        atype = self.Attributes['value'].Type
        value = atype()
        if theLabel.FindAttribute(atype.GetID(), value):
            return value.Get()

        return super().GetValue(theLabel)

    
    from utils.decorator import classproperty
    @classproperty
    def ID(self):
        return Sym_RealDriver_GUID #
    @classproperty
    def Type(self):
        return "real"

