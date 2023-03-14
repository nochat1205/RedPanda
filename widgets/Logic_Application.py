from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot
)

from OCC.Core.V3d import V3d_View

import typing



from utils.OCCUtils import (
    AIS_InteractiveContext, 
    AIS_Shape,
    AIS_Shaded, 
    AIS_ViewCube,
    TDocStd_Document,
    TCollection_ExtendedString,
    TDataStd_Name,
    TPrsStd_AISViewer,
    V3d_Viewer,
    TCollection_AsciiString,
    TDF_TagSource,
    FromText,
    TDF_Label,
    TFunction_Logbook,
    TDF_Tool,
    TNaming_NamedShape,
    TPrsStd_AISPresentation
    
)
from utils.Sym_Application import Sym_Application
from utils.Driver.Sym_Driver import (
    Sym_Driver,
    GetDriver
)
from utils.Sym_DocUpdateData import Sym_NewShapeData
from utils.logger import Logger

class Logic_Application(QObject):
    sig_DocChanged = pyqtSignal(TDocStd_Document)
    sig_DocUpdate = pyqtSignal()

    def __init__(self, theDisplay, parent=None) -> None:
        super().__init__(parent)
        self._DocApp = Sym_Application() # save construct driver
        self._main_doc = TDocStd_Document(TCollection_ExtendedString("Standard"))

        self._myViewer:V3d_Viewer = theDisplay.Viewer
        self._myContext:AIS_InteractiveContext = theDisplay.Context
        self._myView:V3d_View = theDisplay.View
 
        self._list_doc = list()

    def InitAIS_IC(self):
        self._myContext.EraseAll(False)
        self._myContext.Display(AIS_ViewCube(), False)

    def NewDocument(self, theFormat:str):
        doc = TDocStd_Document(TCollection_ExtendedString(theFormat))
        self._DocApp.AddDocument(doc)
        TDataStd_Name.Set(doc.Main(), TCollection_ExtendedString("Debug"))

        # load and read instant read
        TPrsStd_AISViewer.New(doc.Main(), self._myViewer)
        TPrsStd_AISViewer.Find(self._main_doc.Main(), self._myContext)

        self._myContext.SetDisplayMode(AIS_Shaded, True)
        self.InitAIS_IC()

        # Set the maximum number of available "undo" actions
        doc.SetUndoLimit(10)

        self._main_doc = doc
        self.sig_DocChanged.emit(self._main_doc)      

    @pyqtSlot(Sym_NewShapeData)
    def NewShape(self, data:Sym_NewShapeData):
        theGuid = data.driverID
        name = data.name
        theParam = data.dict_params

        self._main_doc.NewCommand()
        Logger().info("-- NewConmand --")        
        Logger().info("-- Add New Shape --")
        Logger().info("Type:"+str(theGuid))
        Logger().info("Name:"+name)
        Logger().info("Param:"+str(theParam))
        Logger().warn("Test")

        mainLabel = TDF_TagSource.NewChild(self._main_doc.Main())
        aEntry = TCollection_AsciiString()
        TDF_Tool.Entry(mainLabel, aEntry)
        Logger().info('Entry:'+aEntry.PrintToString())

        TDataStd_Name.Set(mainLabel, FromText(TCollection_ExtendedString, name))

        aDriver = GetDriver(theGuid)
        log = TFunction_Logbook()

        aDriver.Init(mainLabel)
    
        def _initValue(aLabel:TDF_Label, aDriver:Sym_Driver, aParams):
            aDriver:Sym_Driver

            if len(aDriver.Arguments) == 0:
                aDriver.ChangeValue(aLabel, aParams)
            else:
                aEntry = TCollection_AsciiString()
                TDF_Tool.Entry(mainLabel, aEntry)
                for name, value in aParams.items():
                    Logger().info(f"Entry{aEntry} init {name}")
                    _initValue(aLabel.FindChild(aDriver.Arguments[name].Tag),
                               GetDriver(aDriver.Arguments[name].DriverID), 
                               value)
        
            aDriver.Execute(aLabel, log)
            return

        _initValue(mainLabel, aDriver, theParam['Shape'])

        anAisPresentation = TPrsStd_AISPresentation.Set(mainLabel, TNaming_NamedShape.GetID())
        anAisPresentation.Display(True)
        NS = TNaming_NamedShape()
        flag = mainLabel.FindAttribute(TNaming_NamedShape.GetID(), NS)
    
        ais_Shape = AIS_Shape(NS.Get())
        self._myContext.Display (ais_Shape, False)

        # TODO:
        self._myContext.UpdateCurrentViewer()

        self._main_doc.CommitCommand()

        self.sig_DocUpdate.emit()

    @pyqtSlot(TDF_Label, dict)
    def ShapeChange(self, theLabel, theParam):
        return 

