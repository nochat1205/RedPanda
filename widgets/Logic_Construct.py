from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout


from utils.Sym_ParamBuilder import Sym_NewBuilder
from utils.Driver.Sym_Driver import Param

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

        self.treeRoots[theName] = item

        if "value" in theParams:
            item.setText(1, theParams["value"].Default)
            # item.setText(2, str(theParams['value'].Type))

        self.tree.openPersistentEditor(item, 1)
        self.treeItems['name'] = item
        father = item

        if 'children' in theParams:
            for name, param in theParams["children"].items():
                self._setTreeItem(name, param, father)

    def SetTree(self, theParams:dict):
        father = self.tree
        for name, param in theParams.items():
            if isinstance(param, Param):
                item = QtWidgets.QTreeWidgetItem(father)
                item.setText(0, name)
                item.setText(1, param.Default)
    
                self.tree.openPersistentEditor(item, 1)
                self.treeRoots[name] = item

                self.treeRoots['name'] = item
            elif name == "Shape":
                self._setTreeItem('Shape', theParams["Shape"], self.tree)
    
        self.tree.expandAll()

    def _Clear(self):
        for root in self.treeRoots.values():
            self.tree.removeChild(root)
        self.treeRoots.clear()
        self.treeItems.clear()