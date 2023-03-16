from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout


from utils.Sym_ParamBuilder import Sym_NewBuilder
from utils.Driver.Sym_Driver import Param
from utils.logger import Logger

class Logic_Construct(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree = self
        self.tree.setStyle(QtWidgets.QStyleFactory.create('QStyleFactory'))
        self.tree.setStyle(QtWidgets.QStyleFactory.create('window'))

        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['name', 'data', 'type'])
        # self._setPolicy()

        self.treeItems = dict()
        self.treeRoots = dict()

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
        self.SetTree(data.params)

    def _setTreeItem(self, theName, theParams:dict, father=None, readOnly=False):
        item = QtWidgets.QTreeWidgetItem(father)
        item.setText(0, theName)
        if "value" in theParams:
            item.setText(1, theParams["value"].Default)
            # item.setText(2, str(theParams['value'].Type))

        self.tree.openPersistentEditor(item, 1)
        self.treeItems[theName] = item

        father = item
        if 'children' in theParams:
            for name, param in theParams["children"].items():
                self._setTreeItem(name, param, father)
        return father

    def _setRootItem(self, name:str, param:Param, father):
        item = QtWidgets.QTreeWidgetItem(father)
        item.setText(0, name)
        item.setText(1, param.Default)

        self.tree.openPersistentEditor(item, 1)
        self.treeRoots[name] = item


    def SetTree(self, theParams:dict):
        father = self.tree
        self._setRootItem('Name', theParams['Name'], father)
        self._setRootItem('Parent', theParams['Parent'], father)
        if 'Shape' in theParams:
            Logger().debug("run")
            item = self._setTreeItem('Shape', theParams["Shape"], self.tree)
            self.treeRoots['Shape'] = item

        self.tree.expandAll()

    def _Clear(self):
        root = self.tree.invisibleRootItem()
        for item in self.treeRoots.values():
            (item.parent() or root).removeChild(item)
        Logger().debug("Len:"+str())
        self.treeRoots.clear()
        self.treeItems.clear()
