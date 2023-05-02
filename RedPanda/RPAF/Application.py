from OCC.Core.TDocStd import TDocStd_Application
from OCC.Core.TDF import TDF_TagSource

from RedPanda.logger import Logger
from RedPanda.Core.data import RP_ExtendStr

from .DriverTable import DataDriverTable
from .DataDriver import *
from .GUID import RP_GUID
from .Attribute import TDataStd_Name
from .Document import Document
from .RD_Label import Label


class Application(TDocStd_Application):
    def __init__(self) -> None:
        super(Application, self).__init__()
        self.main_doc = None
        self.doc_li = list()
        self._registerDriver()
        


    def _registerDriver(self):
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

        from .DataDriver.Geom2dDriver import Ellipse2dDriver
        DataDriverTable.Get().AddDriver(Ellipse2dDriver .ID,
                                              Ellipse2dDriver())

    def RegisterDriver(self, driver:DataDriver):
        DataDriverTable.Get().AddDriver(driver.ID, driver)

    def AddDocument(self, doc):
        self.InitDocument(doc)
        super(TDocStd_Application, self).Open(doc)
        self.doc_li.append(doc)
        self.main_doc = doc

    def Update(self, theLabel:Label, str)->set:
        touched_set = set()
        update_set = set()
        Logger().info("-- NewConmand --")
        self._main_doc.NewCommand()
        # change
        aDriver:DataDriver = theLabel.GetDriver()
        aDriver.Change(theLabel, str)

        # link change
        update_set.add(theLabel)
        touched_set.add(theLabel)
        while len(update_set) > 0:
            aLabel = update_set.pop()
            aDriver:DataDriver = aLabel.GetDriver()
            if aDriver:    
                aDriver.Execute(aLabel)

                label_set = aDriver.GetRefMeLabel(aLabel)
                update_set |= label_set
                touched_set |= label_set

        self._main_doc.CommitCommand()
        Logger().info("-- commit command --")

        return touched_set

    def NewDataLabel(self, driverID:RP_GUID):
        self._main_doc.NewCommand()
        Logger().info("-- NewConmand --")        
        Logger().info("-- Add New Shape --")

        aDriver:DataDriver = DataDriverTable.Get().GetDriver(driverID)
        mainLabel = TDF_TagSource.NewChild(self._main_doc.Main())
        aDriver.Init(mainLabel)
        TDataStd_Name.Set(mainLabel, RP_ExtendStr('New '+aDriver.Type))

        self._main_doc.CommitCommand()

        Logger().info("-- commit command --")
        return mainLabel

    def NewDocument(self, theFormat:str):
        doc = Document(RP_ExtendStr(theFormat))
        self.AddDocument(doc)
        TDataStd_Name.Set(doc.Main(), RP_ExtendStr(str(doc)))

        # load and read instant read
        # TPrsStd_AISViewer.New(doc.Main(), self._myViewer)
        # TPrsStd_AISViewer.Find(self._main_doc.Main(), self._myContext)

        # self._myContext.SetDisplayMode(AIS_Shaded, True)

        # Set the maximum number of available "undo" actions
        doc.SetUndoLimit(10)

        self._main_doc = doc
        # self.sig_DocChanged.emit(self._main_doc)
        return doc


    def HaveDoc(self):
        return self.main_doc is not None
