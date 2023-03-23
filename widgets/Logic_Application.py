from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot
)

from OCC.Core.V3d import V3d_View

import typing



from RedPanda.OCCUtils import (
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
    TPrsStd_AISPresentation,
    TopoDS_Shape,
    TopLoc_Location,
    gp_Trsf,
    AIS_WireFrame,
    TDF_ChildIterator,
    
)
from RedPanda.Sym_Application import Sym_Application
from RedPanda.Driver.Sym_Driver import (
    Sym_Driver,
    GetDriver
)
from OCC.Core.XmlDrivers import (
    xmldrivers_DefineFormat
)
from RedPanda.Sym_DocUpdateData import (
    Sym_NewShapeData,
    Sym_ChangeData
)
from RedPanda.logger import Logger

class Logic_Application(QObject):
    sig_DocChanged = pyqtSignal(TDocStd_Document)
    sig_DocUpdate = pyqtSignal()

    def __init__(self, theDisplay, parent=None) -> None:
        super().__init__(parent)
        self._DocApp = Sym_Application() # save construct driver

        xmldrivers_DefineFormat(self._DocApp)        
        self._main_doc = TDocStd_Document(TCollection_ExtendedString("Standard"))

        self._myViewer:V3d_Viewer = theDisplay.Viewer
        self._myContext:AIS_InteractiveContext = theDisplay.Context
        self._myView:V3d_View = theDisplay.View
 
        self._list_doc = list()

    def InitAIS_IC(self):
        self._myContext.EraseAll()

    def NewDocument(self, theFormat:str):
        doc = TDocStd_Document(TCollection_ExtendedString(theFormat))
        self._DocApp.AddDocument(doc)
        TDataStd_Name.Set(doc.Main(), TCollection_ExtendedString("Debug"))

        # load and read instant read
        TPrsStd_AISViewer.New(doc.Main(), self._myViewer)
        TPrsStd_AISViewer.Find(self._main_doc.Main(), self._myContext)

        self._myContext.SetDisplayMode(AIS_Shaded, True)

        # Set the maximum number of available "undo" actions
        doc.SetUndoLimit(10)

        self._main_doc = doc
        self.sig_DocChanged.emit(self._main_doc)

    @pyqtSlot(Sym_NewShapeData)
    def NewShape(self, data:Sym_NewShapeData):
        aParentPath = data.ParentPath
        theGuid = data.driverID
        name = data.name
        theParam = data.value_dict

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

        # init the label with driver and set value
        aDriver = GetDriver(theGuid)
        aDriver.Init(mainLabel, theParam)
        # Logic_Application._initValue(mainLabel, aDriver, theParam['Shape'])

        # Presetaion
        Logic_Application.Presentation(mainLabel)
        self.UpdateCurrentViewer()

        self._main_doc.CommitCommand()

        Logger().info("-- commit command --")
        self.sig_DocUpdate.emit()
        self._DocApp.SaveAs(self._main_doc, TCollection_ExtendedString("./resource/a.xml"))

    @pyqtSlot(Sym_ChangeData)
    def ChangeDoc(self, data:Sym_ChangeData):
        aParentPath = data.ParentPath
        aLabel = TDF_Label()
        name = data.name
        theParam = data.value_dict
        Logger().debug('run')

        label_set = set()
        TDF_Tool.Label(self._main_doc.GetData(), aParentPath, aLabel)
        aDriver = GetDriver(aLabel)

        Logger().info("-- NewConmand --")        
        Logger().info("-- Change Shape --")
        Logger().info(f"Id:{aDriver.ID}")
        Logger().info(f"Name:{name}")
        Logger().info(f"Param:{theParam}")

        self._main_doc.NewCommand()
        aDriver.Change(aLabel, theParam)
        self.UpdatePresent(aLabel)

        label_set = Sym_Driver.BroadcastImpacted(aLabel)

        while len(label_set) > 0:
            aLabel = label_set.pop()
            aDriver = GetDriver(aLabel)
            if aDriver:    
                aDriver.Execute(aLabel)
                self.UpdatePresent(aLabel)

                label_set |= Sym_Driver.BroadcastImpacted(aLabel)

        self.UpdateCurrentViewer()
        self._main_doc.CommitCommand()
        Logger().info("-- commit command --")

    @staticmethod
    def UpdatePresent(theLabel:TDF_Label):
        anAisPresentation = TPrsStd_AISPresentation.Set(theLabel, TNaming_NamedShape.GetID())
        anAisPresentation.Update()


    @staticmethod
    def Presentation(theLabel:TDF_Label):
        anAisPresentation = TPrsStd_AISPresentation.Set(theLabel, TNaming_NamedShape.GetID())
        anAisPresentation.SetMode(AIS_Shaded)
        anAisPresentation.Display(True)

        if TPrsStd_AISViewer.Has(theLabel):
            Logger().info(f"Label:{theLabel.GetLabelName()} update presentation")

    @pyqtSlot(TDF_Label, dict)
    def ShapeChange(self, theLabel, theParam):
        return 

    def UpdateCurrentViewer(self):
        from OCC.Core.AIS import (
            AIS_ListOfInteractive,
            AIS_InteractiveObject,
            AIS_ListIteratorOfListOfInteractive
        )
        from RedPanda.Sym_Attribute import Sym_ShapeRef

        it = TDF_ChildIterator(self._main_doc.Main())
        while it.More():
            anAisPresentation = TPrsStd_AISPresentation.Set(it.Value(), TNaming_NamedShape.GetID())
            aLabel:TDF_Label = anAisPresentation.Label()
            ref = Sym_ShapeRef()
            if aLabel.FindAttribute(Sym_ShapeRef.GetID(), ref):
                if ref.NbChildren() > 0:
                    anAisPresentation.SetMode(AIS_WireFrame)
                    TPrsStd_AISViewer.Update(aLabel)
            it.Next()

        # anAisObjectsList = AIS_ListOfInteractive()
        # self._myContext.DisplayedObjects(anAisObjectsList) # TODO:
        # anIter = AIS_ListIteratorOfListOfInteractive(anAisObjectsList)
        # while anIter.More():
        #     anAisObject:AIS_InteractiveObject = anIter.Value()
        #     if anAisObject is None:
        #         Logger().warn("anAisObject is None")
        #     # Get the main label of the selected object
        #     anAisPresentation:TPrsStd_AISPresentation = TPrsStd_AISPresentation.DownCast(anAisObject.GetOwner())
        #     if anAisPresentation:
        #         aLabel:TDF_Label = anAisPresentation.Label()
        #         ref = Sym_ShapeRef()
        #         if aLabel.FindAttribute(Sym_ShapeRef.GetID(), ref):
        #             if ref.NbChildren() == 0:
        #                 anAisObject.SetDisplayMode(AIS_Shaded)
        #                 TPrsStd_AISViewer.Update(aLabel)
        #     anIter.Next()

        # self._myContext.UpdateCurrentViewer()
