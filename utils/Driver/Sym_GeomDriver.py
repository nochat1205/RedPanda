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

# class Sym_BSplineDriver(Sym_Driver):
#     def __init__(self) -> None:
#         super().__init__()
#         self.Attr = Param(TNaming_NamedShape)
#         self.Attributes['value'] = self.Attr
#         self.Arguments = {
#             Int
#         }

