from utils.OCCUtils import (
    TDF_Label,
    TNaming_NamedShape,
    TFunction_Logbook,
    BRepAlgoAPI_Cut,
    TNaming_Builder,
    TCollection_AsciiString,
    TDF_Tool,
    TColgp_Array1OfPnt,
    Geom_BezierCurve,
    BRepBuilderAPI_MakeEdge,
)

from utils.Driver.Sym_Driver import (
    Sym_Driver,
    Sym_ShapeRefDriver,
    Param,
    Argument
)
from utils.Driver.Sym_DataDriver import (
    Sym_ArrayDriver
)
from utils.decorator import (
    classproperty
)
from utils.logger import (
    Logger
)
from utils.GUID import (
    Sym_BezierDriver_GUID
)
from typing import Union

class Sym_BezierDriver(Sym_Driver):
    def __init__(self) -> None:
        super().__init__()
        self.Attr = Param(TNaming_NamedShape)
        self.Attributes['value'] = self.Attr
        self.Arguments = {
            'pnts': Argument(self.tagResource, Sym_ArrayDriver.ID)
        }

    def Execute(self, theLabel: TDF_Label) -> int:
        super().Execute(theLabel)
        print('Run')

        entry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, entry)
        Logger().debug(f"Entry:{entry} Excute {self.Type}")

        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        pnts:TColgp_Array1OfPnt = dict_param['pnts']
        curve = Geom_BezierCurve(pnts)
        Logger().debug(f"Entry:{entry} Excute {self.Type}")
        api = BRepBuilderAPI_MakeEdge(curve)
        api.Build()
        Logger().debug(f"Entry:{entry} Excute {self.Type}")
        if not api.IsDone():
            Logger().warn(f"Entry:{entry} Make {self.Type} failed")
            return 1

        builder = TNaming_Builder(theLabel)
        builder.Generated(api.Shape())

        Logger().info(f"Entry:{entry} Make {self.Type} Success")
        return 0

    @classproperty
    def Type(self):
        return 'bezier'

    @classproperty
    def ID(self):
        return Sym_BezierDriver_GUID