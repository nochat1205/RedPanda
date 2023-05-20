
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.QtCore import pyqtSlot, QObject, QTimer


from .logger import Logger

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
    timer = None
    @staticmethod
    def Run(argv):
        Logger().info("Application Start")
        qapp = QApplication(argv)
        
        memory_limit =  512*1024*1024 # 512M
        
        timer = QTimer()
        MainApplication.timer = timer
        
        timer.timeout.connect(lambda:
            MainApplication.check_memory_usage(memory_limit))
        timer.start(1000) # 1 seconds

        app = MainApplication()
        app.Show()

        return qapp.exec_()

    @staticmethod
    def check_memory_usage(limit):
        import psutil
        process = psutil.Process()
        memory_usage = process.memory_full_info().rss
        if memory_usage > limit:
            Logger().error('Memory usage exceeded. Terminating')
            print('Memory usage exceeded. Terminating')
            MainApplication.timer.stop()
            QApplication.quit()

    def __init__(self) -> None:
        self.showedLabel_set = set()
        self.ui_myWin = MainWindow()
        self.docApp =  Application()
        self.c_docTree = self.ui_myWin.DocTree()
        self.c_viewer2d:qtViewer2d = self.ui_myWin.Viewer2d()
        self.c_viewer3d:qtViewer3d = self.ui_myWin.Viewer3d()
        self.c_construct = self.ui_myWin.Construct()
        self.c_data = self.ui_myWin.ui.logic_ViewData

        self.SetUpUi()
        self.SignalAndSlot()

    def Show(self):
        self.ui_myWin.show()

    def SetUpUi(self):
        self.SetUpDriver()

    def SignalAndSlot(self):
        # new Shape
        self.ui_myWin.sig_NewDocument.connect(      self.Process_NewDocument)
        self.ui_myWin.sig_SaveDocument.connect(     self.Process_SaveDocument)
        self.ui_myWin.sig_NewDataLabel.connect(     self.Process_NewLabel)
        self.ui_myWin.sig_ActivateOperator.connect( self.Process_ActivateOpera)
        self.ui_myWin.sig_OpenRPXml.connect(        self.Process_OpenDocument)
        self.ui_myWin.sig_saveShape.connect(        self.Process_SaveShape)
        self.ui_myWin.sig_OpenPickleShape.connect(  self.Process_LoadShape)

        self.c_docTree.sig_labelSelect.connect(     self.Process_ShowLabel)
        self.c_docTree.sig_labelCheck.connect(      self.Process_Check)

        self.c_construct.sig_change.connect(        self.Process_ChangeLabel)
        self.c_viewer3d.sig_new_shape.connect(      self.Process_NewLabel)
        self.c_viewer2d.sig_new_shape.connect(      self.Process_NewLabel)
        self.c_viewer2d.sig_point.connect(          self.Process_ShowPoint)


    # register function
    def RegisterShapeDriver(self, menu_name, name,  driver:DataDriver):
        self.docApp.RegisterDriver(driver)
        self.ui_myWin.add_driver_to_menu(menu_name, name, driver.ID)

    def RegisterDriver(self, driver):
        self.docApp.RegisterDriver(driver)

    # function
    def SetUpDriver(self):
        from .RPAF.DataDriver import (
            BezierDriver,
            BoxDriver,
            CutDriver,
        )
        from .RPAF.DataDriver.AlgoDriver import FuseDriver
        from .RPAF.DataDriver.PrimDriver import TransShapeDriver
        from .RPAF.DataDriver.VarDriver import IntDriver
        from .RPAF.DataDriver.GeomDriver import CylSurDriver
        from .RPAF.DataDriver.Geom2dDriver import (
            Ellipse2dDriver, Elps2dDriver, Build3dDriver,
            Segment2dDriver, ArcCircleDriver, TrimmedCurveDriver
        )
        from .RPAF.DataDriver.ShapeBaseDriver import (
            Ax3Driver, Ax2dDriver, ConstShapeDriver
        )
        from .RPAF.DataDriver.VertexDriver import Pnt2dDriver
        from .RPAF.DataDriver.ShapeDriver import (
            RefSubDriver, MirrorDriver, PrismDriver,
            FaceDriver, 
        )
        from .RPAF.DataDriver.FilletDriver import FilletAllDriver
        from .RPAF.DataDriver.ArrayDriver import EdgeArrayDriver
        from .RPAF.DataDriver.TopoDriver import (
            WireDriver, CompoudDriver
        )
        from .RPAF.DataDriver.OffsetDriver import (
            ThickSoldDriver, ThruSecDriver
        )

        self.RegisterDriver(Ax3Driver())
        self.RegisterDriver(Ax2dDriver())
        self.RegisterDriver(Pnt2dDriver())
        self.RegisterDriver(RefSubDriver())
        self.RegisterDriver(IntDriver())
        self.RegisterDriver(EdgeArrayDriver())
        self.RegisterDriver(ConstShapeDriver())
        

        self.RegisterShapeDriver('PrimAPI', 'Box', BoxDriver())
        self.RegisterShapeDriver('AlgoAPI', 'Cut', CutDriver())
        self.RegisterShapeDriver('AlgoAPI', 'Fuse', FuseDriver())
        self.RegisterShapeDriver('GeomAPI', 'bezier', BezierDriver())
        self.RegisterShapeDriver('GeomAPI', 'Cyl', CylSurDriver())
        self.RegisterShapeDriver('GeomAPI', 'Ellipse2d', Ellipse2dDriver())
        # self.RegisterShapeDriver('Topo', 'RefSub', RefSubDriver())
        self.RegisterShapeDriver('Topo', 'Build3d', Build3dDriver())
        self.RegisterShapeDriver('Geom2dAPI', 'Ellipse', Elps2dDriver())
        self.RegisterShapeDriver('Geom2dAPI', 'Seg2d', Segment2dDriver())
        self.RegisterShapeDriver('Geom2dAPI', 'ArcCirc2d', ArcCircleDriver())
        self.RegisterShapeDriver('Geom2dAPI', 'Trimmed', TrimmedCurveDriver())
        self.RegisterShapeDriver('Topo', 'Wire', WireDriver())
        self.RegisterShapeDriver('Topo', 'Mirror', MirrorDriver())
        self.RegisterShapeDriver('Topo', 'Face', FaceDriver())
        self.RegisterShapeDriver('Topo', 'Prism', PrismDriver())
        self.RegisterShapeDriver('Fillet', 'FilletAll', FilletAllDriver())
        self.RegisterShapeDriver('Topo', 'Transform', TransShapeDriver())
        self.RegisterShapeDriver('Topo', 'Compu', CompoudDriver())
        self.RegisterShapeDriver('Offset', 'Thick', ThickSoldDriver())
        self.RegisterShapeDriver('Offset', 'ThruSec', ThruSecDriver())


    def Process_NewLabel(self, id:RP_GUID, data=None):
        Logger().info(f'New Data Label {id}')
        # 0 
        if not self.docApp.HaveDoc():
            self.Process_NewDocument()

        # 1. doc new
        aLabel:Label = self.docApp.NewDataLabel(id, data)

        # 2. doc tree update
        item = self.c_docTree.Create_TreeItem(aLabel, aLabel.Father())

        Logger().info(f'New Data Label {id} end')

    def Process_NewDocument(self, format:str='XmlOcaf'):
        Logger().info('New Document')

        doc:Document = self.docApp.NewDocument(format)
        alabel = doc.Main()

        # 2 tree item
        item = self.c_docTree.Create_TreeItem(alabel)
        Logger().info('New Document End')

    def Process_ShowLabel(self, theLabel:Label):        
        Logger().info('Process Show Label Start')

        # 1
        self.showedLabel_set.clear()
        self.showedLabel_set.add(theLabel)
        self.c_construct.ShowLabel(theLabel)
        # 2
        self.c_viewer3d.ShowLabel(theLabel)
        self.c_viewer2d.ShowLabel(theLabel)       
        Logger().info('Process Show Label End')

    def Process_ChangeLabel(self, theLabel, str):
        Logger().info('Process Change Label Start')
        Logger().info(f'Start Change: {theLabel.GetEntry()}, {str}')
        # 1. update
        label_set = self.docApp.Update(theLabel, str)
        # 2.
        labelInDocTree = set() 
        for aLabel in label_set:
            aLabel:Label
            fatherLabel :Label= aLabel.GetDataLabel()
            labelInDocTree.add(fatherLabel)
            if fatherLabel in self.showedLabel_set:
                self.c_construct.UpdataLabel(aLabel)

        # 4 update Tree
        for label in labelInDocTree:
            self.c_docTree.Update(label)

            self.c_viewer3d.UpdateLabel(label)
            # build3d arcOfCircle2d 自由参数会存在问题. 会卡死程序.  或许是没检查GC_xxx.IsDone
            # self.c_viewer2d.UpdateLabel(label)

        Logger().info(f'End Change: {theLabel.GetEntry()}, {str}')
        Logger().info('Process Change Label End')

    def Process_Check(self, theLabel, setChecked):
        from .RPAF.DataDriver.ShapeDriver import BareShapeDriver
        if 'check_li' not in self.__dict__:
            self.check_li = dict()

        if  not setChecked and  theLabel in self.check_li:
            ais = self.check_li[theLabel]
            self.c_viewer2d._display.Context.Remove(ais, True)
            self.check_li.pop(theLabel)
        elif setChecked and theLabel not in self.check_li:
            aDriver = theLabel.GetDriver()            
            if aDriver and isinstance(aDriver, BareShapeDriver):
                ctx = aDriver.Prs2d(theLabel)
                key = (theLabel, 'shape')
                if key in ctx.d:
                    ais = ctx[key]
                    if ais:
                        self.check_li[theLabel] = ais
                        self.c_viewer2d._display.Context.Display(ais, True)

    def Process_ActivateOpera(self, name):
        self.c_viewer2d.ActiveOperator(name)

    def Process_OpenDocument(self):
        return 
        from OCC.Core.TDF import TDF_ChildIterator
        path = QFileDialog.getOpenFileName(self.ui_myWin, '打开文件', './resource',
                                'STP files(*.xml);;(*.rpxml))')

        doc:Document = self.docApp.OpenDoc(path[0])
        # print(doc.Main().GetEntry())
        # print(path[0])
        # aLabel = doc.Main()
        # for ind in range(1, 10):
        #     l = aLabel.FindChild(ind, False)
        #     if not l.IsNull():
        #         print(l.GetEntry())
        self.c_docTree.Create_TreeItem(doc.Main())

    def Process_SaveDocument(self):
        Logger().info('Process Save Document start')
        doc = self.docApp._main_doc
        if doc.File() is None:
            url, tp = QFileDialog.getSaveFileName(self.ui_myWin, '保存文件', './resource',
                                       'STP files(*.xml);;(*.rpxml))')

            doc.SetFile(url)
        self.docApp.SaveDoc()

        Logger().info('Process Save Document end')

    def Process_ShowPoint(self, *tup):
        Logger().info('Process Show Point Start')
        pnt, shape, param = tup
        self.c_data.show(pnt)
        Logger().info('Process Show Point End')

    def Process_LoadShape(self):
        import pickle
        from .RPAF.DataDriver.ShapeBaseDriver import ConstShapeDriver

        Logger().info('Process Load Shape Start')
        path, *_ = QFileDialog.getOpenFileName(self.ui_myWin, '打开文件', './resource',
                                'pickle files(*.rppickle)')
        
        with open(path, 'rb') as f:
            shape = pickle.load(f)
            self.Process_NewLabel(ConstShapeDriver.ID, shape)
        Logger().info('Process Load Shape End')

    def Process_SaveShape(self):
        import pickle
        from .RPAF.DataDriver.ShapeBaseDriver import BareShapeDriver

        Logger().info('Process Save Shape Start')
        if (self.showedLabel_set) == 0:
            return

        aLabel, *_ = self.showedLabel_set
        aDriver = aLabel.GetDriver()
        if not isinstance(aDriver, BareShapeDriver):
            return 

        shape = aDriver.GetValue(aLabel)
        if shape is None:
            return 

        url, tp = QFileDialog.getSaveFileName(self.ui_myWin, '保存文件', './resource',
                                    'pickle files(*.rppickle))')
        with open(url, 'wb+') as f:
            pickle.dump(shape, f)

        Logger().info('Process Save Shape End')

    def Process_exit(self):
        pass
