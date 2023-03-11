from widgets.Ui_DocView import Ui_DocView


from PyQt5 import QtWidgets

class Logic_DocView(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super(Logic_DocView, self).__init__(parent)
        self.ui = Ui_DocView()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

