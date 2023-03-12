from utils.OCCUtils import (
    TDF_Data,
    TDF_Label,
    gp_Trsf,
    TopLoc_Location,
    gp_Pnt
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
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox

def Trsf()->    TopLoc_Location:
    tr = gp_Trsf()
    tr.SetTranslation(gp_Pnt(1, 0, 0), gp_Pnt(0, 0, 1))
    loc = TopLoc_Location(tr)
    print(loc.DumpJsonToString())
    return loc

loc = Trsf()
print(loc.DumpJsonToString())
