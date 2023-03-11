
from utils.OCCUtils import (
    TDF_Data,
    TDF_Label,
)
from OCC.Core.TDataStd import (
    TDataStd_Integer
)
from utils.Driver.Sym_ShapeDriver import (
    Sym_BoxDriver
)
from utils.Sym_ParamBuilder import (
    Sym_NewBuilder
)
from utils.Sym_Application import Sym_Application

app = Sym_Application()

dict = Sym_NewBuilder(Sym_BoxDriver()).params
print(dict)
