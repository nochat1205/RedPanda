from OCC.Core.TDocStd import TDocStd_Application

from .DriverTable import DataDriverTable

class Application(TDocStd_Application):
    def __init__(self) -> None:
        super(Application, self).__init__()
        # Instantiate a TOcafFunction_BoxDriver and add it to the TFunction_DriverTable
        DataDriverTable.Get().AddDriver(Sym_RealDriver.ID,
                                              Sym_RealDriver())
        DataDriverTable.Get().AddDriver(Sym_PntDriver.ID,
                                              Sym_PntDriver())
        DataDriverTable.Get().AddDriver(Sym_TransformDriver.ID,
                                              Sym_TransformDriver())
        DataDriverTable.Get().AddDriver(Sym_BoxDriver.ID,
                                              Sym_BoxDriver())
    
        DataDriverTable.Get().AddDriver(Sym_ShapeRefDriver.ID,
                                              Sym_ShapeRefDriver())
        DataDriverTable.Get().AddDriver(Sym_CutDriver.ID,
                                              Sym_CutDriver())

        DataDriverTable.Get().AddDriver(Sym_ArrayDriver.ID,
                                              Sym_ArrayDriver())
        DataDriverTable.Get().AddDriver(Sym_BezierDriver.ID,
                                              Sym_BezierDriver())

    def AddDocument(self, doc):
        self.InitDocument(doc)
        super(TDocStd_Application, self).Open(doc)


