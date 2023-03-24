from RedPanda.widgets.Ui_ConstructView import Ui_ConstructView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot
)
from PyQt5 import QtWidgets, QtCore

from OCC.Core.TFunction import TFunction_Driver
from OCC.Core.Standard import Standard_GUID

from RedPanda.Sym_ParamBuilder import (
    Sym_NewBuilder,
    Sym_ChangeBuilder,
)
from RedPanda.Sym_DocUpdateData import (
    Sym_NewShapeData,
    Sym_ChangeData
)
from RedPanda.widgets.Logic_Construct import Logic_Construct

class Logic_ConstructView(QtWidgets.QWidget):
    sig_NewShape = pyqtSignal(Sym_NewShapeData)
    sig_ChangeShape = pyqtSignal(Sym_ChangeData)

    def __init__(self, parent=None):
        super(Logic_ConstructView, self).__init__(parent)
        self.ui = Ui_ConstructView()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        self.guid = None
        self.IsNew = False
        self.Constructer:Logic_Construct = self.ui.widget
        # connect
        self.ui.pushButton_2.clicked.connect(self.commit)
        self.ui.pushButton.clicked.connect(self.Change)

    @pyqtSlot(Sym_NewBuilder)
    def NewConstruct(self, data:Sym_NewBuilder):
        self.IsNew = True
        self.Constructer.BuildView(data)

    @pyqtSlot()
    def commit(self):
        if self.IsNew:
            data = Sym_NewShapeData(self.Constructer)
            self.sig_NewShape.emit(data)

    @pyqtSlot(Sym_ChangeBuilder)
    def ShowShape(self, data:Sym_ChangeBuilder):
        self.IsNew = False
        self.Constructer.BuildView(data)

    @pyqtSlot()
    def Change(self):
        if not self.IsNew:
            data = Sym_ChangeData(self.Constructer)
            self.sig_ChangeShape.emit(data)
