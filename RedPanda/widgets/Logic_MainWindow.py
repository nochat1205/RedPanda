
from typing import Callable

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QProgressBar
)
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from RedPanda.utils.ModelFileRead import read_step_file_with_names_colors, OpenFile


from OCC.Core.TColStd import (
    TColStd_ListOfInteger,
    TColStd_ListIteratorOfListOfInteger
)
from OCC.Core.TDF import (
    TDF_AttributeIterator,
    TDF_ChildIterator,
    TDF_Label,
    TDF_Attribute
)
from RedPanda.RPAF.Document import Document
from RedPanda.RPAF.GUID import RP_GUID

from RedPanda.widgets.Ui_Main import Ui_MainWindow
from RedPanda.widgets.Logic_DocTree import ModelTree
from RedPanda.widgets.Logic_Application import Logic_Application
from RedPanda.logger import Logger


class MainWindow(QMainWindow):
    ''' 主页面ui,
    包含: LabelView. toolbar

    '''
    sig_NewDataLabel = pyqtSignal(RP_GUID)
    sig_NewDocument = pyqtSignal(str)
    sig_OpenXml = pyqtSignal()
    sig_SaveDocument = pyqtSignal()
    sig_ActivateOperator = pyqtSignal(str)
    sig_OpenRPXml = pyqtSignal()
    sig_OpenPickleShape = pyqtSignal()
    sig_saveShape = pyqtSignal()

    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        self._modelMenu_dict = dict()
        self._menu_dict = dict() # other menu

        self.setupUi()

        self.ui.retranslateUi(self)

    def setupMenu(self):
        self._menu_dict['menubar'] = self.menuBar
        self._menu_dict['start'] = self._start_menu
        self._menu_dict['open'] = self.ui.menuopen

        self.ui.actionxml.triggered.connect(self.onNewDocument)
        self.add_function_to_menu('start', 'save', 
                                  lambda:self.sig_SaveDocument.emit())
        self.add_function_to_menu('open', 'openxml', 
                                  lambda:self.sig_OpenXml.emit())
        self.add_function_to_menu('open', 'Open rp xml',
                                  lambda: self.sig_OpenRPXml.emit())
        self.add_function_to_menu('open', 'Open pickle shape',
                                  lambda: self.sig_OpenPickleShape.emit())
        self.add_function_to_menu('open', 'save pickle shape',
                                  lambda: self.sig_saveShape.emit())


        self.add_menu('operator')
        self.add_function_to_menu('operator', 'viewer', lambda:self.sig_ActivateOperator.emit('viewer'))
        self.add_function_to_menu('operator', 'line', lambda:self.sig_ActivateOperator.emit('line'))

    def setupUi(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Main Struct
        self.logic_Viewer3d = self.ui.logic_View
        self.logic_Viewer3d.InitDriver()

        self.logic_Viewer2d = self.ui.logic_View2d
        self.logic_Viewer2d.InitDriver()

        self._menubar = self.ui.menubar
        self._model_menu = self.ui.menu
        self._start_menu = self.ui.start

        self.logic_ViewData = self.ui.logic_ViewData
        self.logic_ConstructView = self.ui.logic_Construct
        self.logic_DocData = self.ui.logic_DocData

        self.logic_DocTree = self.logic_DocData.ui.treeWidget

        # menu
        self.setupMenu()

        return 

    def DocTree(self):
        return self.logic_DocTree

    def Viewer2d(self):
        return self.logic_Viewer2d

    def Viewer3d(self):
        return self.logic_Viewer3d

    def Construct(self):
        return self.logic_ConstructView

    def add_menu(self, menu_name:str):
        _menu = self._menubar.addMenu("&" + menu_name)
        self._menu_dict[menu_name] = _menu

    def add_function_to_menu(self, menu_name: str, action_name:str, _callable: Callable) -> None:
        try:
            _action = QtWidgets.QAction(
                action_name, self
            )
            # if not, the "exit" action is now shown...
            _action.setMenuRole(QtWidgets.QAction.NoRole)
            _action.triggered.connect(_callable)

            self._menu_dict[menu_name].addAction(_action)
        except KeyError:
            raise ValueError("the menu item %s does not exist" % menu_name)

    def add_model_menu(self, menu_name: str) -> None:
        _menu = self._model_menu.addMenu("&" + menu_name)
        self._modelMenu_dict[menu_name] = _menu

    def add_function_to_modelmenu(self, menu_name: str, action_name:str, _callable: Callable) -> None:
        try:
            _action = QtWidgets.QAction(
                action_name, self
            )
            # if not, the "exit" action is now shown...
            _action.setMenuRole(QtWidgets.QAction.NoRole)
            _action.triggered.connect(_callable)

            self._modelMenu_dict[menu_name].addAction(_action)
        except KeyError:
            raise ValueError("the menu item %s does not exist" % menu_name)

    def add_driver_to_menu(self, menu_name: str, action_name:str, driverId):
        if menu_name not in self._modelMenu_dict:
            self.add_model_menu(menu_name)
        self.add_function_to_modelmenu(menu_name, action_name, lambda:self.sig_NewDataLabel.emit(driverId))

    def read_doc(self, doc:Document):
        # read doc
        return
        rootLabel = doc.Main()
        level = 0
        stack_label = list()
        stack_label.append((rootLabel, level))
        def GetAttributeType(attri: TDF_Attribute):
            list_type = TDF_Attribute.__subclasses__()
            for type in list_type:
                try:
                    if attri.ID() == type.GetID():
                        return type
                except :
                    pass
            return TDF_Attribute

        while len(stack_label) != 0:
            label : TDF_Label
            label, level = stack_label.pop()
            it_attr = TDF_AttributeIterator(label)
            while it_attr.More():
                print(" "*(level+1), GetAttributeType(it_attr.Value()))
                it_attr.Next()
                        
            children = list()
            it_child = TDF_ChildIterator(label)

            while it_child.More():
                children.append( (it_child.Value(), level+1) )
                it_child.Next()

            children.reverse()
            stack_label.extend(children)

    def onNewDocument(self):
        self.sig_NewDocument.emit('XmlOcaf')