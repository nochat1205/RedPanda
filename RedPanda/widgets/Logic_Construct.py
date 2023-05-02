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
        self.label = None
        self.treeItem = dict()
        self._setingData = False
        self.mtx = False

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

        if self.mtx :
            return 

        self.mtx = True
            
        qobject = self.sender()
        item:AFItem = self.tree.itemAt(qobject.pos())

        self.sig_change.emit(item.label, item.GetText())
        
        self.mtx = False

    def Rigister(self, theLabel, item: AFItem): # for child item
        self.treeItem[theLabel] = item
        if item.SigChange:
            item.SigChange.connect(self.onItemChange)

    def RemoveItem(self, theLabel):
        item:QTreeWidgetItem = self.treeItem[theLabel]

        parentItem = item.parent()
        parentItem.takeChild(parentItem.indexOfChild(item))
        self.treeItem.pop(theLabel)

    def _clear(self):
        self.label = None
        for item in self.treeItem.values():
            parent = item.parent()
            if parent is not None:
                parent.removeChild(item)
            else:
                self.tree.invisibleRootItem().removeChild(item)

            del item

        self.treeItem.clear()

    def ShowLabel(self, theLabel): # 对外
        from .DriverNode.NameNode import AFItemFactory

        self._setDataing = True
        self._clear()
        self.label = theLabel
        item = AFItemFactory.GetItem(theLabel.GetLabelName(), theLabel, self.tree)
        self._setingData = False

        self.tree.expandAll()

    def Update(self, theLabel:Label):
        self.treeItem[theLabel] .Update()



