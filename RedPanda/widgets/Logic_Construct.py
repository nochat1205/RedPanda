from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QAbstractItemView,
    QTreeWidgetItem,
    QSizePolicy
)
from RedPanda.Sym_ParamBuilder import (
    ArrayParam
)
from RedPanda.logger import Logger
from RedPanda.Sym_ParamBuilder import NodeParam

class BaseNode(QtWidgets.QTreeWidgetItem):
    _IsArray:bool = False
    _IsShapeData: bool = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.IsChanged = False

    def IsArray(self):
        return self._IsArray

    def IsShapeData(self):
        return self._IsShapeData

    def SetChanged(self):
        self.IsChanged = True

    def IsChanged(self):
        return self.IsChanged

class ArrayNode(BaseNode):
    _IsArray:bool = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def Load(self, theName, theParams:ArrayParam, father=None, readOnly=False):
        arrayParam: ArrayParam = theParams
        
        self.setText(0, theName)
        

        self.setText(1, str(arrayParam._size))
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

        self._typename = 'Pnt'
        self.sub_param = ArrayParam


class Logic_Construct(QtWidgets.QTreeWidget):
    ArrayParamData_col = 2
    ChangeFlag_col = 3
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

        sizePolicy = QSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)

 
    def _setPolicy(self):
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.tree.setSizePolicy(sizePolicy)

    def BuildView(self, data):
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
            return
            Logger().info(f"change item:{item.text(0)}, col:{column} to text:{item.text(column)}")
            self._setChangeFlag(item) # TODO: 分开
            if item.data(self.ArrayParamData_col, QtCore.Qt.ItemDataRole.UserRole):
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


        if isinstance(theParams, NodeParam):
            item = QtWidgets.QTreeWidgetItem(father)
            father = item
            item.setText(0, theName)

            param = theParams
            item.setText(1, param.value)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

        elif isinstance(theParams, ArrayParam):
            arrayParam: ArrayParam = theParams
            item = ArrayNode(father)

            item.setText(1, str(arrayParam._size))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            item.setData(self.ArrayParamData_col, 
                         QtCore.Qt.ItemDataRole.UserRole, True)
            item.setData(self.ArrayParamData_col, 
                         QtCore.Qt.ItemDataRole.UserRole+1, 'Pnt')
            item.setData(self.ArrayParamData_col, 
                         QtCore.Qt.ItemDataRole.UserRole+2, arrayParam._subParam)

        elif isinstance(theParams, dict):
            item = QtWidgets.QTreeWidgetItem(father)
            father = item
            item.setText(0, theName)
            for name, param in theParams.items():
                self._setTreeItem(name, param, father)
        else:
            Logger().warn(f"SetTreeItem unknow theParams type{type(theParams)}")

        return item

    def _setRootItem(self, name:str, param:NodeParam):
        item = QtWidgets.QTreeWidgetItem(self.tree)
        item.setText(0, name)
        item.setText(1, param.value)
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

    @staticmethod
    def _isChange(item: BaseNode):
        return item.IsChanged()

    @staticmethod
    def isShapeData(item: BaseNode):
        return item.IsShapeData()

    def _setChangeFlag(self, item: BaseNode):
        if 'Shape' not in self.treeRoots:
            return
        if not self.isShapeData(item):
            return

        root = self.treeRoots['Shape']
        while not self._isChange(item):
            Logger().info(f'item:{item.text(0)} set change flag')
            item.SetChanged()
            if root == item:
                break

            item = item.parent()
