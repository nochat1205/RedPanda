from widgets.Ui_ScreenData import Ui_ScreenData


from PyQt5 import QtWidgets

class Logic_ScreenData(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super(Logic_ScreenData, self).__init__(parent)
        self.ui = Ui_ScreenData()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

