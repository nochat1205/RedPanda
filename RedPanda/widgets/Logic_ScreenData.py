from RedPanda.Core.Euclid import RP_Pnt

from RedPanda.widgets.Ui_ScreenData import Ui_ScreenData

from PyQt5 import QtWidgets

class Logic_ScreenData(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super(Logic_ScreenData, self).__init__(parent)
        self.ui = Ui_ScreenData()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

    def show(self, pnt:RP_Pnt):
        self.ui.lineEdit.setText(str(pnt.X()))
        self.ui.lineEdit_2.setText(str(pnt.Y()))
        self.ui.lineEdit_3.setText(str(pnt.Z()))
