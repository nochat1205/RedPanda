from OCC.Core.TDocStd import TDocStd_Application

from .DriverTable import DataDriverTable
from .DataDriver import *

class Application(TDocStd_Application):
    def __init__(self) -> None:
        super(Application, self).__init__()
        # Instantiate a Driver and add it to the DriverTable
        DataDriverTable.Get().AddDriver(RealDriver.ID,
                                              RealDriver())
        DataDriverTable.Get().AddDriver(PntDriver.ID,
                                              PntDriver())
        DataDriverTable.Get().AddDriver(TransformDriver.ID,
                                              TransformDriver())
        DataDriverTable.Get().AddDriver(BoxDriver.ID,
                                              BoxDriver())
    
        DataDriverTable.Get().AddDriver(ShapeRefDriver.ID,
                                              ShapeRefDriver())
        DataDriverTable.Get().AddDriver(CutDriver.ID,
                                              CutDriver())
        DataDriverTable.Get().AddDriver(PntArrayDriver.ID,
                                              PntArrayDriver())
        DataDriverTable.Get().AddDriver(BezierDriver.ID,
                                              BezierDriver())
        DataDriverTable.Get().AddDriver(BezierDriver.ID,
                                              BezierDriver())
        DataDriverTable.Get().AddDriver(TransShapeDriver .ID,
                                              TransShapeDriver())

    def AddDocument(self, doc):
        self.InitDocument(doc)
        super(TDocStd_Application, self).Open(doc)


