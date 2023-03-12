from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot
)

from OCC.Core.AIS import (
    AIS_InteractiveContext, 
    AIS_Shape,
    AIS_Shaded, 
    AIS_ViewCube
)
from OCC.Core.V3d import V3d_View

import typing



from utils.logger import Logger
from utils.OCCUtils import *
from utils.Sym_Application import Sym_Application
from utils.Driver.Sym_Driver import (
    Sym_Driver,
    GetDriver
)
from utils.Sym_DocUpdateData import Sym_NewShapeData

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

        Logger().debug('NewShape:'+name)

        self._main_doc.NewCommand()
        aLabel = TDF_TagSource.NewChild(self._main_doc.Main())
        TDataStd_Name.Set(aLabel, FromText(TCollection_ExtendedString, name))

        Logger().debug("name")
        aDriver = GetDriver(theGuid)
        Logger().debug("Init1")
        log = TFunction_Logbook()

        aDriver.Init(aLabel)
        Logger().debug("Init2")

        def _initValue(aLabel:TDF_Label, aDriver, aParams):
            aDriver:Sym_Driver
            if len(aDriver.Arguments) == 0:
                    aType = aDriver.Attributes['value'].Type
                    aType.Set(aLabel, FromText(aType, aParams))
            else:
                for name, value in aParams.items():
                    _initValue(aLabel.FindChild(aDriver.Arguments[name].Tag),
                               GetDriver(aDriver.Arguments[name].DriverID), 
                               value)

            Logger().debug("1:"+aDriver.Type)
            aDriver.Execute(aLabel, log)
            Logger().debug("2:"+aDriver.Type)
            return

        _initValue(aLabel, aDriver, theParam['Shape'])
        Logger().debug("Init3")

        anAisPresentation = TPrsStd_AISPresentation.Set(aLabel, TNaming_NamedShape.GetID())
        anAisPresentation.Display(True)
        NS = TNaming_NamedShape()
        flag = aLabel.FindAttribute(TNaming_NamedShape.GetID(), NS)
        Logger().debug("Construct:"+ str(flag) )

        self._myContext.Display (AIS_Shape(NS.Get()), False)
        Logger().debug("run")
        # TODO:
        self._myContext.UpdateCurrentViewer()

        self._main_doc.CommitCommand()

        self.sig_DocUpdate.emit()

    @pyqtSlot(TDF_Label, dict)
    def ShapeChange(self, theLabel, theParam):
        return 

