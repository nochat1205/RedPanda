from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QAbstractItemView,
    QTreeWidgetItem,
    QSizePolicy
)
from PyQt5.QtCore import pyqtSignal,pyqtSlot

from RedPanda.RPAF.RD_Label import Label
from .DriverNode.NameNode import AFItem
    
class Logic_Construct(QtWidgets.QTreeWidget):
    sig_change = pyqtSignal(Label, str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.treeItem = dict()
        self._setingData = False

        self.tree = self
        self.tree.setStyle(QtWidgets.QStyleFactory.create('QStyleFactory'))
        self.tree.setStyle(QtWidgets.QStyleFactory.create('window'))

        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['name', 'data', 'state'])

        self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.tree.itemDoubleClicked.connect(self.onClickItem)
        # self.tree.itemChanged.connect(self.onArrayItemChange)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        self.tree.setSizePolicy(sizePolicy)
 
    def _setPolicy(self):
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.tree.setSizePolicy(sizePolicy)

    # --- new ---    
    @pyqtSlot()
    def onItemChange(self):
        if self._setingData: return 
        qobject = self.sender()
        item:AFItem = self.tree.itemAt(qobject.pos())
        self.sig_change.emit(item.label, item.GetText())

    def Rigister(self, theLabel, item: AFItem): # for child item
        self.treeItem[theLabel] = item
        if item.SigChange:
            item.SigChange.connect(self.onItemChange)

    def RemoveItem(self, theLabel):
        item:QTreeWidgetItem = self.treeItem[theLabel]

        parentItem = item.parent()
        parentItem.takeChild(parentItem.indexOfChild(item))
        self.treeItem.pop(theLabel)

    def ShowLabel(self, theLabel): # 对外
        from .DriverNode.NameNode import AFItemFactory
        self._setDataing = True
        AFItemFactory.GetItem(theLabel.GetLabelName(), theLabel, self.tree)
        self._setingData = False

    def Update(self, theLabel:Label):
        self.treeItem[theLabel]:AFItem .Update()
