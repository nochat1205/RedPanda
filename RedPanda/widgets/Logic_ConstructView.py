from RedPanda.widgets.Ui_ConstructView import Ui_ConstructView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot
)
from PyQt5 import QtWidgets, QtCore

from OCC.Core.TFunction import TFunction_Driver
from OCC.Core.Standard import Standard_GUID

from .Logic_Construct import Logic_Construct
from RedPanda.RPAF.RD_Label import Label

class Logic_ConstructView(QtWidgets.QWidget):
    sig_change = pyqtSignal(Label, str)

    def __init__(self, parent=None):
        super(Logic_ConstructView, self).__init__(parent)
        self.ui = Ui_ConstructView()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        self.guid = None
        self.IsNew = False
        self.Constructer:Logic_Construct = self.ui.widget
        self.Constructer.sig_change.connect(lambda label, str:self.sig_change.emit(label, str))

    def ShowLabel(self, theLabel):
        self.Constructer.ShowLabel(theLabel)

    def UpdataLabel(self, theLabel):
        self.Constructer.Update(theLabel)