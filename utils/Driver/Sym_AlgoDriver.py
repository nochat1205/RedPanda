from utils.OCCUtils import (
    TDF_Label,
    TNaming_NamedShape,
    TFunction_Logbook,
    BRepAlgoAPI_Cut,
    TNaming_Builder,
    TCollection_AsciiString,
    TDF_Tool,
)

from utils.Driver.Sym_Driver import (
    Sym_Driver,
    Sym_ShapeRefDriver,
    Param,
    Argument
)
from utils.decorator import (
    classproperty
)
from utils.logger import (
    Logger
)
from utils.GUID import Sym_CutDriver_GUID

class Sym_CutDriver(Sym_Driver):
    def __init__(self) -> None:
        
        Logger().debug("before init "+str(self.ID))
        super().__init__()
        Logger().debug("end init "+str(self.ID))
        self.myAttr = Param(TNaming_NamedShape)
        self.Attributes['value'] = self.myAttr
        self.Arguments = {
            'beCutShape': Argument(self.tagResource, Sym_ShapeRefDriver.ID),
            'cutShape': Argument(self.tagResource, Sym_ShapeRefDriver.ID)
        }

    def Execute(self, theLabel: TDF_Label) -> int:
        super().Execute(theLabel)
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            value = argu.Value(theLabel)
            dict_param[name] = value

        shape0 = dict_param['beCutShape']
        shape1 = dict_param['cutShape']

        api = BRepAlgoAPI_Cut(shape0, shape1)
        api.Build()
        if not api.IsDone():
            Logger().warn("Transform Failed")
            Logger().warn(f"Param:{dict_param}")
            return 1

        shape = api.Shape()
        
        builder = TNaming_Builder(theLabel)
        builder.Generated(dict_param['beCutShape'], shape)

        entry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, entry)

        NS = TNaming_NamedShape()
        if not theLabel.FindAttribute(NS.GetID(), NS):
            Logger().warn(f"Entry:{entry} execute error")
            return 1
        if NS.Get() is None:
            Logger().warn(f"Entry:{entry} execute error")
            return 1
        return 0

    @classproperty
    def ID(self):
        return  Sym_CutDriver_GUID #

    @classproperty
    def Type(self):
        return "Cut"
