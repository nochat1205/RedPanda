from widgets.Ui_ConstructView import Ui_ConstructView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot
)
from PyQt5 import QtWidgets, QtCore

from OCC.Core.TFunction import TFunction_Driver
from OCC.Core.Standard import Standard_GUID

from utils.Sym_ParamBuilder import (
    Sym_NewBuilder,
    Sym_ChangeBuilder,
)



from utils.Sym_DocUpdateData import Sym_NewShapeData
from widgets.Logic_Construct import Logic_Construct

class Logic_ConstructView(QtWidgets.QWidget):
    sig_NewShape = pyqtSignal(Sym_NewShapeData)

    def __init__(self, parent=None):
        super(Logic_ConstructView, self).__init__(parent)
        self.ui = Ui_ConstructView()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        self.guid = None

        self.Constructer:Logic_Construct = self.ui.widget
        # connect
        self.ui.pushButton_2.clicked.connect(self.commit)

    @pyqtSlot(Sym_NewBuilder)
    def NewConstruct(self, Data:Sym_NewBuilder):
        self.Constructer.BuildView(Data)

    @pyqtSlot()
    def commit(self):
        data = Sym_NewShapeData(self.Constructer)
        self.sig_NewShape.emit(data)
