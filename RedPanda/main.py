
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import pyqtSlot, QObject


from .logger import Logger
from .widgets.Logic_MainWindow import MainWindow,Logic_Application
from .RPAF.GUID import RP_GUID
from .RPAF.RD_Label import Label
from .RD_Object import RDObjectManager
from .RPAF.Application import Application
from .RPAF.Document import Document

from .widgets.Logic_LabelView import LabelView

class MainApplication():
    """
    """
    @staticmethod
    def Run(argv):
        Logger().info("Application Start")
        qapp = QApplication(argv)
        app = MainApplication()
        app.myWin.show()

        return qapp.exec_()

    def __init__(self) -> None:
        self.myWin = MainWindow()
        self.docApp =  Application()
        self.docTree = self.myWin.DocTree()
        self.DataLabel_manager =  RDObjectManager()

        self.SetUpUi()
        self.SignalAndSlot()

    def SetUpUi(self):
        self.MakeShapeMenu()

    def SignalAndSlot(self):
        # new Shape
        self.myWin.sig_SaveNewDocument.connect(self.Process_SaveDocument)
        self.myWin.sig_NewDocument.connect(self.Process_NewDocument)
        self.docTree.sig_labelSelect.connect(self.Process_ShowLabel)
        self.myWin.sig_NewDataLabel.connect(self.Process_NewLabel)

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

    def Process_NewLabel(self, id:RP_GUID):
        # 1. doc new
        aLabel:Label = self.docApp.NewDataLabel(id)
        # 2
        obj = self.DataLabel_manager.Add(aLabel)

        # 3. doc tree update
        item = self.docTree.Create_TreeItem(aLabel, aLabel.Father())
        obj.tree_item = item

    def Process_NewDocument(self, format:str):
        print('New Document')
        doc:Document = self.docApp.NewDocument(format)
        alabel = doc.Main()

        # 2 
        obj = self.DataLabel_manager.Add(alabel)
        # 3
        item = self.docTree.Create_TreeItem(alabel)
        obj.tree_item = item

    def Process_SaveDocument(self):
        ...

    def Process_ShowLabel(self, theLabel:Label):
        # 1
        labelView = LabelView()

        self.DataLabel_manager[theLabel].viewer = labelView
        labelView.ShowLabel(theLabel)

        labelView.sig_change.connect(self.Process_ChangeLabel)
        result = labelView.exec_()  
        if result:
            self.DataLabel_manager[theLabel].viewer = None

    def Process_ChangeLabel(self, theLabel, str):
        # 1. update
        label_set = self.docApp.Update(theLabel, str)
        # 2. 

    def Process_exit():
        pass

