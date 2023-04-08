import typing
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QListView,
    QScrollArea,
)
from RedPanda.RD_Singleton import Singleton
from RedPanda.RPAF.DataDriver import (
    BaseDriver,
    Argument
)
from RedPanda.RPAF.DriverTable import DataDriverTable
from RedPanda.RPAF.RD_Label import Label

from .Ui_LabelView import Ui_Dialog
from .Logic_Construct import Logic_Construct

class LabelView(QWidget):
    def __init__(self, parent: typing.Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        self.commit_bt = self.ui.commit_bt

        self.scrollArea = self.ui.scrollArea
        self.scrollArea.setFrameStyle(QScrollArea.NoFrame)

        self.__content = Logic_Construct()
        self.scrollArea.setWidget(self.__content)

    def Run(self, data):
        print("RUn")
        self.__content.BuildView(data)


# class BaseDataWidget(QWidget):
#     def __init__(self, parent: typing.Optional['QWidget'] = None) -> None:
#         super().__init__(parent)

#     def Run(self, theLabel: Label=None):
#         aDriver = DataDriverTable.Get().GetDriver(self.RelativeDriver())
#         if theLabel:
#             aDriver = theLabel.GetDriver()

#         view = QListView()
        

#     def GetValue(self):
#         raise NotImplementedError()

#     @staticmethod
#     def RelativeDriver():
#         from RedPanda.RPAF.DataDriver import TransformDriver
#         return TransformDriver.ID


# class DataWidgetRegister(Singleton):
#     def __init__(self) -> None:
#         if isinstance:
#             return 
#         self.__widget_Dict = dict()

#     def Registered(self, id, widget:type[BaseDataWidget]):
#         self.__widget_Dict[id] = widget

#     def __getitem__(self, key):
#         if key not in self.widget_Dict:
#             return BaseDataWidget
#         return self.widget_Dict[key]

