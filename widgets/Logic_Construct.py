from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QAbstractItemView,
    QTreeWidgetItem
)
from utils.Sym_ParamBuilder import (
    Sym_NewBuilder,
    ArrayParam
)
from utils.Driver.Sym_Driver import Param
from utils.logger import Logger



class Logic_Construct(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.treeItems = dict()
        self.treeRoots = dict()

        self.tree = self
        self.tree.setStyle(QtWidgets.QStyleFactory.create('QStyleFactory'))
        self.tree.setStyle(QtWidgets.QStyleFactory.create('window'))

        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['name', 'data'])

        self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tree.itemDoubleClicked.connect(self.onClickItem)
        self.tree.itemChanged.connect(self.onArrayItemChange)
 
    def _setPolicy(self):
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.tree.setSizePolicy(sizePolicy)

    def BuildView(self, data:Sym_NewBuilder):
        self.receiveData = data
        self._objectName = data.type
        self.driverId = data.TFunctionID

        self._Clear()

        self._setRootItem('Parent', data.parent_param)
        self._setRootItem('Name', data.name_param)
        self.SetTree(data.shape_param)
        Logger().info(f'ParamTree:{self.tree}')
        self.tree.expandAll()

    def onArrayItemChange(self, item: QTreeWidgetItem, column: int):
        if column == 1:
            Logger().info(f"change item:{item.text(0)}, col:{column} to text:{item.text(column)}")
            if item.data(2, QtCore.Qt.ItemDataRole.UserRole):
                size = int(item.text(1))
                count = item.childCount()
                name = item.data(2, QtCore.Qt.ItemDataRole.UserRole+1)
                subParam = item.data(2, QtCore.Qt.ItemDataRole.UserRole+2)
                if count < size:
                    for ind in range(count, size):
                        self._setTreeItem(f'{ind}', subParam, item)
                elif count > size: # TODO: have preblem
                    for ind in range(size, count):
                        item.removeChild(item.child(ind))

        return  

    def onClickItem(self, item: QTreeWidgetItem, column: int):
        if column == 1:
            self.tree.editItem(item, column)

    def _setTreeItem(self, theName, theParams:dict, father=None, readOnly=False):
        item = QtWidgets.QTreeWidgetItem(father)
        father = item
        item.setText(0, theName)

        if isinstance(theParams, Param):
            param = theParams
            item.setText(1, param.Default)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

        elif isinstance(theParams, ArrayParam):
            arrayParam: ArrayParam = theParams
            item.setText(1, str(arrayParam._size))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            item.setData(2, QtCore.Qt.ItemDataRole.UserRole, True)
            item.setData(2, QtCore.Qt.ItemDataRole.UserRole+1, 'Pnt')
            item.setData(2, QtCore.Qt.ItemDataRole.UserRole+2, arrayParam._subParam)

        elif isinstance(theParams, dict):
            for name, param in theParams.items():
                self._setTreeItem(name, param, father)
        else:
            Logger().warn(f"SetTreeItem unknow theParams type{type:(theParam)}")

        return father

    def _setRootItem(self, name:str, param:Param):
        item = QtWidgets.QTreeWidgetItem(self.tree)
        item.setText(0, name)
        item.setText(1, param.Default)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        
        self.tree.editItem(item, 1)
        self.treeRoots[name] = item


    def SetTree(self, theParams:dict):
        father = self.tree
        item = self._setTreeItem('Shape', theParams, self.tree)
        self.treeRoots['Shape'] = item


    def _Clear(self):
        root = self.tree.invisibleRootItem()
        for item in self.treeRoots.values():
            (item.parent() or root).removeChild(item)
        self.treeRoots.clear()
        self.treeItems.clear()
