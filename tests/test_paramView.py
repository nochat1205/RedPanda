from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QTreeWidget,QTreeView,
    QAbstractItemView, QTreeWidgetItem, QSpinBox
)
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem
class MyListView(QTreeWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setStyle(QtWidgets.QStyleFactory.create('windows'))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setColumnCount(3)
        self.setHeaderLabels(['name', 'value', 'commentEdit', 'commentTextChanged'])
        self.itemChanged.connect(self.onItemChanged)
        self._setData = False
        self.item_dict = {}

    def ShowDate(self, rows):
        self._setData = True
        for ind, row in enumerate(rows):
            self.item_dict[ind] = QTreeWidgetItem(self)
            item = self.item_dict[ind]
            item.setText(0, row[0])
            spin = QSpinBox()
            spin.setMinimum(0)
            spin.setMaximum(10)
            spin.setSingleStep(1)
            spin.setValue(row[1])
            
            spin.editingFinished.connect(self.onEditFinished)
            spin.valueChanged.connect()
            
            self.setItemWidget(item, 1, spin)
            
            item.setText(2, str(spin.parentWidget()))

        self._setData = False

    def onItemChanged(self, item:QTreeWidgetItem, col):
        return

    @pyqtSlot()
    def onEditFinished(self):
        if self._setData: return
        spin_box = self.sender()
        item = self.itemAt(spin_box.pos())
        item.setText(2, f'EditFinished value = {spin_box.value()}')

class Block(QTreeWidgetItem):
    pass

def TestWidget():
    treeW = QTreeWidget()
    node = Block(treeW)
    node1 = Block(node)
    node2 = node.child(0)
    print(type(node))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    # data = [
    #     ['QT', 1],
    #     ['Tree', 2],
    #     ['Item', 3],
    # ]
    # widget = MyListView(None)
    # widget.ShowDate(data)
    # widget.show()
    # code = app.exec_()
    # sys.exit(code)
    TestWidget()