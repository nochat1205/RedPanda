from utils.OCCUtils import (
    FromText,
    TFunction_Logbook,
    TDataStd_Real,
    TDF_Label,
    TDF_LabelList,
    TDataXtd_Point,
    gp_Pnt,
    TDataXtd_Geometry
)

from utils.GUID import *

from utils.Driver.Sym_Driver import (
    Sym_Driver,
    GetDriver,
    Argument,
    Param
)

from utils.Driver.Sym_DataDriver import (
    Sym_RealDriver,
)

class Sym_PntDriver(Sym_Driver):
    _type = 'Point'
    _guid = Sym_PntDriver_GUID
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TDataXtd_Geometry)
        self.Attributes["value"] = self.myAttr
        self.Arguments = {
            'theXp': Argument(self.tagResource, Sym_RealDriver.ID), 
            'theYp': Argument(self.tagResource, Sym_RealDriver.ID),
            'theZp': Argument(self.tagResource, Sym_RealDriver.ID),
        }

    def Execute(self, theLabel: TDF_Label, log: TFunction_Logbook) -> int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            dict_param[name] = GetDriver(argu.DriverID).GetValue(theLabel)

        pnt = gp_Pnt(dict_param["theXp"], dict_param["theYp"], dict_param["theZp"])
        AttrType = self.Attributes['value'].Type
        AttrType.Set(theLabel, pnt)
        return 0

    # def GetValue(self, theLabel:TDF_Label)->any:
    #     atype = self.Attributes['value'].Type
    #     value = atype()
    #     if theLabel.FindAttribute(atype.GetID(), value):
    #         return value.Get()

    #     return value.Get()

    from utils.decorator import classproperty
    @classproperty
    def ID(self):
        return Sym_PntDriver._guid #


    @classproperty
    def Type(self):
        return Sym_PntDriver._type
