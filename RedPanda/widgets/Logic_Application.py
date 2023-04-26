import typing

from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot
)

from OCC.Core.TDF import (
    TDF_TagSource,
    TDF_Tool,
    TDF_ChildIterator
)

from OCC.Core.V3d import V3d_View,V3d_Viewer
from OCC.Core.AIS import (
    AIS_InteractiveContext,
    AIS_Shaded, AIS_WireFrame
)
from OCC.Core.XmlDrivers import (
    xmldrivers_DefineFormat
)

from RedPanda.logger import Logger

from RedPanda.Core.data import RP_ExtendStr
from RedPanda.RPAF.Application import Application
from RedPanda.RPAF.Document import Document
from RedPanda.RPAF.RD_Label import Label
from RedPanda.RPAF.Attribute import (
    TDataStd_Name,
    TPrsStd_AISPresentation,
    TPrsStd_AISViewer,
    FromText,
    TNaming_NamedShape,
    Attr_ShapeRef
)
from RedPanda.RPAF.DataDriver.BaseDriver import (
    DataDriver,
)
from RedPanda.RPAF.DriverTable import DataDriverTable

from RedPanda.Sym_DocUpdateData import (
    Sym_NewShapeData,
    Sym_ChangeData
)

class Logic_Application(QObject):
    sig_DocChanged = pyqtSignal(Document)
    sig_DocUpdate = pyqtSignal()

    def __init__(self, theDisplay, parent=None) -> None:
        super().__init__(parent)
        self._DocApp = Application() # save construct driver

        xmldrivers_DefineFormat(self._DocApp)        
        self._main_doc = Document(RP_ExtendStr("Standard"))

        self._myViewer:V3d_Viewer = theDisplay.Viewer
        self._myContext:AIS_InteractiveContext = theDisplay.Context
        self._myView:V3d_View = theDisplay.View

    def InitAIS_IC(self):
        self._myContext.EraseAll()

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

        TDataStd_Name.Set(mainLabel, RP_ExtendStr(name))

        # init the label with driver and set value
        aDriver = DataDriverTable.Get().GetDriver(theGuid)
        aDriver.Init(mainLabel, theParam)
        # Logic_Application._initValue(mainLabel, aDriver, theParam['Shape'])

        # Presetaion
        Logic_Application.Presentation(mainLabel)
        self.UpdateCurrentViewer()

        self._main_doc.CommitCommand()

        Logger().info("-- commit command --")
        self.sig_DocUpdate.emit()
        self._DocApp.SaveAs(self._main_doc, RP_ExtendStr("./resource/a.xml"))

    @pyqtSlot(Sym_ChangeData)
    def ChangeDoc(self, data:Sym_ChangeData):
        aParentPath = data.ParentPath
        aLabel = Label()
        name = data.name
        theParam = data.value_dict
        Logger().debug('run')

        label_set = set()
        TDF_Tool.Label(self._main_doc.GetData(), aParentPath, aLabel)
        aDriver = aLabel.GetDriver()

        Logger().info("-- NewConmand --")        
        Logger().info("-- Change Shape --")
        Logger().info(f"Id:{aDriver.ID}")
        Logger().info(f"Name:{name}")
        Logger().info(f"Param:{theParam}")

        self._main_doc.NewCommand()
        aDriver.Change(aLabel, theParam)
        self.UpdatePresent(aLabel)

        aDriver:DataDriver = aLabel.GetDriver()
        label_set = aDriver.GetRefMeLabel(aLabel)

        while len(label_set) > 0:
            aLabel = label_set.pop()
            aDriver = aLabel.GetDriver()
            if aDriver:    
                aDriver.Execute(aLabel)
                self.UpdatePresent(aLabel)

                label_set |= aDriver.GetRefMeLabel(aLabel)

        self.UpdateCurrentViewer()
        self._main_doc.CommitCommand()
        Logger().info("-- commit command --")

        self.sig_DocUpdate.emit()
        self._DocApp.SaveAs(self._main_doc, RP_ExtendStr("./resource/a.xml"))

    @staticmethod
    def UpdatePresent(theLabel:Label):
        anAisPresentation = TPrsStd_AISPresentation.Set(theLabel, TNaming_NamedShape.GetID())
        anAisPresentation.Update()

    @staticmethod
    def Presentation(theLabel:Label):
        anAisPresentation = TPrsStd_AISPresentation.Set(theLabel, TNaming_NamedShape.GetID())
        anAisPresentation.SetMode(AIS_Shaded)
        anAisPresentation.Display(True)

        if TPrsStd_AISViewer.Has(theLabel):
            Logger().info(f"Label:{theLabel.GetLabelName()} update presentation")

    @pyqtSlot(Label, dict)
    def ShapeChange(self, theLabel, theParam):
        return 

    def UpdateCurrentViewer(self):
        from OCC.Core.AIS import (
            AIS_ListOfInteractive,
            AIS_InteractiveObject,
            AIS_ListIteratorOfListOfInteractive
        )

        it = TDF_ChildIterator(self._main_doc.Main())
        while it.More():
            anAisPresentation = TPrsStd_AISPresentation.Set(it.Value(), TNaming_NamedShape.GetID())
            aLabel:Label = anAisPresentation.Label()
            ref = Attr_ShapeRef()
            if aLabel.FindAttribute(Attr_ShapeRef.GetID(), ref):
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
        #         ref = Attr_ShapeRef()
        #         if aLabel.FindAttribute(Attr_ShapeRef.GetID(), ref):
        #             if ref.NbChildren() == 0:
        #                 anAisObject.SetDisplayMode(AIS_Shaded)
        #                 TPrsStd_AISViewer.Update(aLabel)
        #     anIter.Next()

        # self._myContext.UpdateCurrentViewer()

    # --- New  ---
    from RedPanda.RPAF.GUID import RP_GUID
    @pyqtSlot(RP_GUID)
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
        return Label

    @pyqtSlot(str)
    def NewDocument(self, theFormat:str):
        doc = Document(RP_ExtendStr(theFormat))
        self._DocApp.AddDocument(doc)
        TDataStd_Name.Set(doc.Main(), str(doc))

        # load and read instant read
        # TPrsStd_AISViewer.New(doc.Main(), self._myViewer)
        # TPrsStd_AISViewer.Find(self._main_doc.Main(), self._myContext)

        # self._myContext.SetDisplayMode(AIS_Shaded, True)

        # Set the maximum number of available "undo" actions
        doc.SetUndoLimit(10)

        self._main_doc = doc
        # self.sig_DocChanged.emit(self._main_doc)
        return doc
