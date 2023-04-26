from OCC.Core.TDocStd import TDocStd_Application
from OCC.Core.TDF import TDF_TagSource

from RedPanda.logger import Logger
from RedPanda.Core.data import RP_ExtendStr

from .DriverTable import DataDriverTable
from .DataDriver import *
from .GUID import RP_GUID
from .Attribute import TDataStd_Name


class Application(TDocStd_Application):
    def __init__(self) -> None:
        super(Application, self).__init__()
        self.main_doc = None
        self.doc_li = list()
        self.RegisterDriver()
        

    def RegisterDriver(self):
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

        from .DataDriver.VertexDriver import Pnt2dDriver
        DataDriverTable.Get().AddDriver(Pnt2dDriver .ID,
                                              Pnt2dDriver())

        from .DataDriver.ShapeBaseDriver import Ax2dDriver
        DataDriverTable.Get().AddDriver(Ax2dDriver .ID,
                                              Ax2dDriver())

        from .DataDriver.Geom2dDriver import EllipseDriver
        DataDriverTable.Get().AddDriver(EllipseDriver .ID,
                                              EllipseDriver())

    def AddDocument(self, doc):
        self.InitDocument(doc)
        super(TDocStd_Application, self).Open(doc)
        self.doc_li.append(doc)
        self.main_doc = doc

    def Update(self, theLabel, str)->set:
        touched_set = set()
        update_set = set()

        # change
        aDriver:DataDriver = aLabel.GetDriver()
        aDriver.Change(theLabel, str)

        # link change
        update_set.add(theLabel)
        touched_set.add(theLabel)
        while len(update_set) > 0:
            aLabel = update_set.pop()
            aDriver = aLabel.GetDriver()
            if aDriver:    
                aDriver.Execute(aLabel)

                label_set = aDriver.GetRefMeLabel(aLabel)
                update_set |= label_set
                touched_set |= label_set

        return touched_set

    def NewDataLabel(self, driverID:RP_GUID):
        self._main_doc.NewCommand()
        Logger().info("-- NewConmand --")        
        Logger().info("-- Add New Shape --")

        aDriver:DataDriver = DataDriverTable.Get().GetDriver(driverID)
        mainLabel = TDF_TagSource.NewChild(self._main_doc.Main())
        TDataStd_Name.Set(mainLabel, RP_ExtendStr('New '+aDriver.Type))
        aDriver.Init(mainLabel)

        self._main_doc.CommitCommand()

        Logger().info("-- commit command --")
        return mainLabel

