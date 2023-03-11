from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout


from utils.Sym_ParamBuilder import Sym_NewBuilder

class Logic_Construct(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout:QVBoxLayout = QtWidgets.QVBoxLayout(self)
        self.dict_lineParam: dict[str, QtWidgets.QLineEdit] = {}

    def BuildView(self, data:Sym_NewBuilder):
        self.receiveData = data
        self.objectName = data.type
        self.driverId = data.TFunctionID

        self._Clear()

        self.SetLayout(data.params)

    def _addItem(self, name, param:dict, readOnly=False):
        rowLayout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(self)
        label.setText(name+":")
        rowLayout.addWidget(label)
        lineEdit = QtWidgets.QLineEdit(self)
        lineEdit.setMaximumSize(QtCore.QSize(60, 16777215))
        lineEdit.setObjectName(name)
        lineEdit.setText(param.get("default", ""))
        lineEdit.setReadOnly(readOnly)
        rowLayout.addWidget(lineEdit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        rowLayout.addItem(spacerItem)

        self.dict_lineParam[name] = lineEdit
        self.layout.addLayout(rowLayout)

    def SetLayout(self, theParams:dict):
        for name, param in theParams.items():
            self._addItem(name, param)     

    def _Clear(self):
        self.dict_lineParam.clear()
        list_item = list(range(self.layout.count()))
        list_item.reverse()
        for _ in list_item:
            item = self.layout.itemAt(_)
            self.layout.removeItem(item)
            if item.widget():
                item.widget().deleteLater()

