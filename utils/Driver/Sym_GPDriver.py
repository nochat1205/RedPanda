from utils.OCCUtils import (
    FromText,
    TFunction_Logbook,
    TDataStd_Real,
    TDF_Label,
    TDF_LabelList,
    TDataXtd_Point,
    gp_Pnt,
    TNaming_NamedShape,
    TNaming_Builder,
    TCollection_AsciiString,
    TDF_Tool
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
from utils.logger import Logger

from OCC.Core.BRepTopAdaptor import BRepTopAdaptor_HVertex
from OCC.Core.BRep import BRep_Tool
from OCC.Extend.ShapeFactory import make_vertex

class Sym_PntDriver(Sym_Driver):
    _type = 'Point'
    _guid = Sym_PntDriver_GUID
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TNaming_NamedShape)
        self.Attributes["value"] = self.myAttr
        self.Arguments = {
            'theXp': Argument(self.tagResource, Sym_RealDriver.ID), 
            'theYp': Argument(self.tagResource, Sym_RealDriver.ID),
            'theZp': Argument(self.tagResource, Sym_RealDriver.ID),
        }

    def Execute(self, theLabel: TDF_Label, log: TFunction_Logbook) -> int:
        super().Execute(theLabel, log)

        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        pnt = gp_Pnt(dict_param["theXp"], dict_param["theYp"], dict_param["theZp"])
        pnt = make_vertex(pnt)

        AttrType = self.Attributes['value'].Type
        builder = TNaming_Builder(theLabel)
        builder.Generated(pnt)

        entry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, entry)

        NS = TNaming_NamedShape()
        if not theLabel.FindAttribute(NS.GetID(), NS):
            Logger().warn(f"Entry:{entry} execute error")
            return 1
        if NS.Get() is None:
            Logger().warn(f"Entry:{entry} execute error")
            return 1

        Logger().info(f"Entry:{entry} Make Point Success")
        return 0

    def GetValue(self, theLabel:TDF_Label)->any:
        storedValue = self.GetStoredValue(theLabel)

        if storedValue:
            pnt = BRep_Tool.Pnt(storedValue )
            return pnt

        entry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, entry)
        Logger().warn(f"Entry:{entry}({self.Type}) get Value None")

        return None

    from utils.decorator import classproperty
    @classproperty
    def ID(self):
        return Sym_PntDriver._guid #

    @classproperty
    def Type(self):
        return Sym_PntDriver._type
