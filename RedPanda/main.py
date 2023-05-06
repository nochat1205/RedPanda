
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import pyqtSlot, QObject


from .logger import Logger

from .RD_Object import RDObjectManager
from .RPAF.GUID import RP_GUID
from .RPAF.RD_Label import Label
from .RPAF.Application import Application
from .RPAF.Document import Document
from .RPAF.DataDriver import DataDriver

from .widgets.Logic_MainWindow import MainWindow
from .widgets.Logic_Viewer import qtViewer3d
from .widgets.Logic_Viewer2d import qtViewer2d


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
        
        self.showedLabel = None
        self.myWin = MainWindow()
        self.docApp =  Application()
        self.c_docTree = self.myWin.DocTree()
        self.c_viewer2d:qtViewer2d = self.myWin.Viewer2d()
        self.c_viewer3d:qtViewer3d = self.myWin.Viewer3d()
        self.c_construct = self.myWin.Construct()

        self.DataLabel_manager =  RDObjectManager()

        self.SetUpUi()
        self.SignalAndSlot()

    def SetUpUi(self):
        self.SetUpDriver()
        
        self.test()
    
    def test(self):
        pass
        # self.myWin.add_function_to_menu('menubar', 'drawline')



    def SignalAndSlot(self):
        # new Shape
        self.myWin.sig_SaveNewDocument.connect(self.Process_SaveDocument)
        self.myWin.sig_NewDocument.connect(self.Process_NewDocument)
        self.c_docTree.sig_labelSelect.connect(self.Process_ShowLabel)
        self.myWin.sig_NewDataLabel.connect(self.Process_NewLabel)
        self.c_construct.sig_change.connect(self.Process_ChangeLabel)

    # register function
    def RegisterShapeDriver(self, menu_name, name,  driver:DataDriver):
        self.docApp.RegisterDriver(driver)
        self.myWin.add_driver_to_menu(menu_name, name, driver.ID)

    def RegisterDriver(self, driver):
        self.docApp.RegisterDriver(driver)

    # function 
    def SetUpDriver(self):
        from .RPAF.DataDriver import (
            BezierDriver,
            BoxDriver,
            CutDriver,
        )
        from .RPAF.DataDriver.GeomDriver import CylSurDriver
        from .RPAF.DataDriver.Geom2dDriver import (
            Ellipse2dDriver, Elps2dDriver, Build3dDriver,
            
        )
        from .RPAF.DataDriver.ShapeBaseDriver import Ax3Driver
        from .RPAF.DataDriver.ShapeBaseDriver import Ax2dDriver
        from .RPAF.DataDriver.VertexDriver import Pnt2dDriver
        from .RPAF.DataDriver.ShapeDriver import RefSubDriver


        self.RegisterDriver(Ax3Driver())
        self.RegisterDriver(Ax2dDriver())
        self.RegisterDriver(Pnt2dDriver())
        self.RegisterDriver(RefSubDriver())
        
        self.RegisterShapeDriver('PrimAPI', 'Box', BoxDriver())
        self.RegisterShapeDriver('AlgoAPI', 'Cut', CutDriver())
        self.RegisterShapeDriver('GeomAPI', 'bezier', BezierDriver())
        self.RegisterShapeDriver('GeomAPI', 'Cyl', CylSurDriver())
        self.RegisterShapeDriver('GeomAPI', 'Ellipse2d', Ellipse2dDriver())
        # self.RegisterShapeDriver('Topo', 'RefSub', RefSubDriver())
        self.RegisterShapeDriver('Topo', 'Build3d', Build3dDriver())
        self.RegisterShapeDriver('Geom2dAPI', 'Ellipse', Elps2dDriver())

    def Process_NewLabel(self, id:RP_GUID):
        Logger().info(f'New Data Label {id}')
        # 0 
        if not self.docApp.HaveDoc():
            self.Process_NewDocument()

        # 1. doc new
        aLabel:Label = self.docApp.NewDataLabel(id)
        # 2
        obj = self.DataLabel_manager.Add(aLabel)

        # 3. doc tree update
        item = self.c_docTree.Create_TreeItem(aLabel, aLabel.Father())
        obj.tree_item = item
        Logger().info(f'New Data Label {id} end')

    def Process_NewDocument(self, format:str='XmlOcaf'):
        Logger().info('New Document')

        doc:Document = self.docApp.NewDocument(format)
        alabel = doc.Main()

        # 2 
        obj = self.DataLabel_manager.Add(alabel)
        # 3
        item = self.c_docTree.Create_TreeItem(alabel)
        obj.tree_item = item

        Logger().info('New Document End')

    def Process_SaveDocument(self):
        ...

    def Process_ShowLabel(self, theLabel:Label):
        # 1
        self.showedLabel = theLabel
        self.c_construct.ShowLabel(theLabel)
        # 2
        self.c_viewer3d.ShowLabel(theLabel)
        self.c_viewer2d.ShowLabel(theLabel)

    def Process_ChangeLabel(self, theLabel, str):
        Logger().info(f'Start Change: {theLabel.GetEntry()}, {str}')
        # 1. update
        label_set = self.docApp.Update(theLabel, str)
        # 2.
        labelInDocTree = set() 
        for aLabel in label_set:
            aLabel:Label
            fatherLabel :Label= aLabel.GetDataLabel()
            labelInDocTree.add(fatherLabel)
            if fatherLabel == self.showedLabel:
                self.c_construct.UpdataLabel(aLabel)

        # self.c_viewer2d.Update()
        # self.c_viewer3d.Update()
        # 4
        for label in labelInDocTree:
            self.c_docTree.Update(label)

        Logger().info('update Label')
        self.c_viewer3d.UpdateLabel()
        self.c_viewer2d.UpdateLabel()

        Logger().info(f'End Change: {theLabel.GetEntry()}, {str}')

    def Process_exit(self):
        pass
