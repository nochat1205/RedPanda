
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot, QObject


from .logger import Logger
from .widgets.Logic_MainWindow import MainWindow,Logic_Application
from .RPAF.GUID import RP_GUID
from .RPAF.RD_Label import Label
from .RD_Object import RDObjectManager
from .RPAF.Application import Application

class MainApplication(QObject):
    """
    """
    def Run(self, argv):
        Logger().debug("Application Start")
        app = QApplication(argv)
        self.myWin.show()

        return app.exec_()

    def __init__(self) -> None:
        self.myWin = MainWindow()
        self.docApp =  Application()
        self.docTree = self.myWin.DocTree()
        self.DataLabel_manager =  RDObjectManager()

        self.SetUpUi()

    def SetUpUi(self):
        self.MakeShapeMenu()

    @pyqtSlot(RP_GUID)
    def Process_NewLabel(self, id):
        # 1. doc new
        aLabel:Label = self.docApp.NewDataLabel(id)
        # 2
        obj = self.DataLabel_manager.Add(aLabel)

        # 3. doc tree update
        item = self.docTree.Create_TreeItem(aLabel, aLabel.Father())
        obj.tree_item = item

    @pyqtSlot(RP_GUID)
    def Process_NewDocument(self, format):
        from .RPAF.Document import Document
        doc:Document = self.logic_app.NewDocument(format)
        alabel = doc.Main()

        # 2 
        obj = self.DataLabel_manager.Add(alabel)
        # 3
        item = self.docTree.Create_TreeItem(alabel)
        obj.tree_item = item

    def Process_SaveDocument(self):
        ...

    @pyqtSlot(Label)
    def Process_ShowLabel(self, theLabel:Label):
        
        pass

    def Process_ChangeLabel(self, theLabel, str):
        # 1. update
        label_set = self.docApp.Update(theLabel, str)
        # 2. 

    def SignalAndSlot(self):
        # new Shape
        self.myWin.sig_NewDataLabel.connect(self.Process_NewLabel)
        self.myWin.sig_NewDocument.connect(self.Process_NewDocument)
        self.docTree.sig_labelSelect.connect(self.Process_ShowLabel)

    # function 
    def MakeShapeMenu(self):
        from RedPanda.RPAF.DataDriver import (
            BezierDriver,
            BoxDriver,
            CutDriver,
        )

        self.myWin.add_driver_to_menu('PrimAPI', 'Box', BoxDriver.ID)
        self.myWin.add_driver_to_menu('AlgoAPI', 'Cut', CutDriver.ID)
        self.myWin.add_driver_to_menu('GeomAPI', 'bezier', BezierDriver.ID)
