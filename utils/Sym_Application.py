from OCC.Core.TDocStd import TDocStd_Application

# sym
from utils.OCCUtils import (
    TFunction_DriverTable
)

from utils.Driver.Sym_Driver import (
    Sym_Driver,
    Sym_ShapeRefDriver
)
from utils.Driver.Sym_DataDriver import (
    Sym_RealDriver,
    Sym_IntDriver,
    Sym_ArrayDriver
)
from utils.Driver.Sym_GPDriver import (
    Sym_PntDriver
)
from utils.Driver.Sym_ShapeDriver import (
    Sym_TransformDriver,
    Sym_BoxDriver
)
from utils.Driver.Sym_AlgoDriver import (
    Sym_CutDriver,
    
)
from utils.Driver.Sym_GeomDriver import (
    Sym_BezierDriver,
)

class Sym_Application(TDocStd_Application):
    def __init__(self) -> None:
        super(Sym_Application, self).__init__()
        # Instantiate a TOcafFunction_BoxDriver and add it to the TFunction_DriverTable
        TFunction_DriverTable.Get().AddDriver(Sym_RealDriver.ID,
                                              Sym_RealDriver())
        TFunction_DriverTable.Get().AddDriver(Sym_PntDriver.ID,
                                              Sym_PntDriver())
        TFunction_DriverTable.Get().AddDriver(Sym_TransformDriver.ID,
                                              Sym_TransformDriver())
        TFunction_DriverTable.Get().AddDriver(Sym_BoxDriver.ID,
                                              Sym_BoxDriver())
    
        TFunction_DriverTable.Get().AddDriver(Sym_ShapeRefDriver.ID,
                                              Sym_ShapeRefDriver())
        TFunction_DriverTable.Get().AddDriver(Sym_CutDriver.ID,
                                              Sym_CutDriver())

        TFunction_DriverTable.Get().AddDriver(Sym_ArrayDriver.ID,
                                              Sym_ArrayDriver())
        TFunction_DriverTable.Get().AddDriver(Sym_BezierDriver.ID,
                                              Sym_BezierDriver())

