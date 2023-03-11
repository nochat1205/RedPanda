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
from utils.Driver.Sym_Driver import Sym_driver
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
        Logger().debug(data)
        theGuid = data.driverID
        theParam = data.dict_params

        self._main_doc.NewCommand()
        aLabel = TDF_TagSource.NewChild(self._main_doc.Main())
        self._myFunction = TFunction_Function.Set(aLabel, theGuid)
        aLogBook: TFunction_Logbook = TFunction_Logbook.Set(aLabel)

        aDriver = Sym_driver()
        if not TFunction_DriverTable.Get().FindDriver(theGuid, aDriver):
            Logger().error("driver with "+theGuid.ToCString()+" no found")

        TDataStd_Name.Set(aLabel, TCollection_ExtendedString(aDriver.type))
        # set child
        Dict_Param = aDriver.Dict_Param
        for name, param in Dict_Param.items():
            childTag = param['tag']
            value = FromText(param["type"], theParam[name])
            param["type"].Set(aLabel.FindChild(childTag), value)

        aDriver.Init(aLabel)
        if aDriver.Execute(aLogBook):
            Logger().error("Create {} function execute failed\n".format(aDriver.type))

        anAisPresentation = TPrsStd_AISPresentation.Set(aLabel, TNaming_NamedShape.GetID())
        anAisPresentation.Display(True)
        NS = TNaming_NamedShape()
        shape = aDriver.Label().FindAttribute(TNaming_NamedShape.GetID(), NS)

        self._myContext.Display (AIS_Shape(NS.Get()), False)
        self._myView.FitAll()
        # self._myView.Redraw()

        # TODO:
        self._myContext.UpdateCurrentViewer()

        self._main_doc.CommitCommand()
        Logger().debug("Created a {} with name: {}".format(aDriver.type, theParam))
        self.sig_DocUpdate.emit()

    @pyqtSlot(TDF_Label, dict)
    def ShapeChange(self, theLabel, theParam):
        return 

