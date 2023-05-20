# _*_ coding: utf-8 _*_
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QKeySequence as QKSec
from PyQt5.QtGui import QIcon,QBrush
from PyQt5.QtCore import  Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QTreeWidgetItem, 
    QTreeWidget,
    QAbstractItemView,
    
)
from OCC.Core.TDF import (
    TDF_ChildIterator
)
from RedPanda.logger import Logger
from RedPanda.RPAF.Document import Document
from RedPanda.RPAF.RD_Label import Label
from RedPanda.RPAF.DataDriver import DataDriver
from RedPanda.RPAF.DataDriver.BaseDriver import DataLabelState

class ModelTree(QtWidgets.QTreeWidget):
    sig_labelSelect = pyqtSignal(Label)
    sig_labelCheck = pyqtSignal(Label, bool)
    def __init__(self, *args):
        super(ModelTree, self).__init__(*args)
        self.tree = self
        self.tree.expandAll()# 节点全部展开
        self.tree.setStyle(QtWidgets.QStyleFactory.create('windows'))#有加号
        self.tree.setColumnCount(3) # 设置列数
        self.tree.setHeaderLabels(['name', 'type', 'state'])# 设置树形控件头部的标题

        self.item_lookup = dict()
        self.main_doc = None
        self.dataRoot = None
        self._Selected_item = None
        self.item_defaultBackground = None

        # 设置根节点
        self.root = QTreeWidgetItem(self.tree)
        self._Selected_item = self.root
        self.item_defaultBackground = self.root.background(0)    
        self.root.setText(0, 'RedPanda')


        # 设置树形控件的列的宽度
        self.tree.setColumnWidth(0, 150)

        self.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.itemChanged.connect(self.OnItemChange)

        # todo 优化2 设置根节点的背景颜色
        #brush_red = QBrush(Qt.red)
        #root.setBackground(0, brush_red)
        #brush_blue = QBrush(Qt.blue)
        #root.setBackground(1, brush_blue)

    def ClearItems(self):
        self._Selected_item = self.root
        if self.dataRoot:
            self.root.removeChild(self.dataRoot)
        self.items.clear()


    def Create_ModelTree(self, doc:Document):
        # 设置根节点
        rootLabel = doc.Main()

        def treeNode(theLabel:Label, father):
            name = theLabel.GetLabelName()
            if len(name) <= 0:
                return

            aDriver:DataDriver = theLabel.GetDriver()

            item = QTreeWidgetItem(father)
            father = item
            self.items.append(item)

            item.setText(0, f'{theLabel.GetEntry()} {name}')
            if aDriver:
                item.setText(1, f'{aDriver.Type}')
                flag = 'OK' if DataLabelState.IsOK(theLabel) else 'Error'
                item.setText(2, f'{flag}')
            self.SetDataLabel(item, theLabel)

            item.setCheckState(0, Qt.Unchecked)

            it_child = TDF_ChildIterator(theLabel)
            while it_child.More():
                treeNode(it_child.Value(), father)
                it_child.Next()

            return father

        self.dataRoot = treeNode(rootLabel, self.root)

    @staticmethod
    def SetDataLabel(item:QTreeWidgetItem, theLabel:Label):
        if theLabel.GetFunctionID():
            item.setData(2, Qt.ItemDataRole.UserRole+1, True)
        item.setData(2, Qt.ItemDataRole.UserRole, theLabel)

    @staticmethod
    def IsNamedShape(item:QTreeWidgetItem):
        return item.data(2, Qt.ItemDataRole.UserRole+1)

    @staticmethod
    def GetLabel(item:QTreeWidgetItem):
        return item.data(2, Qt.ItemDataRole.UserRole)

    # -- new -- 
    @pyqtSlot(Label)
    def Update(self, theLabel):
        self.running = True
        item = self.item_lookup[theLabel]

        name = theLabel.GetLabelName()
        item.setText(0, f'{theLabel.GetEntry()} {name}')

        aDriver:DataDriver = theLabel.GetDriver()
        if aDriver:
            item.setText(1, f'{aDriver.Type}')
            item.setText(2, f'{aDriver.GetStateMsg(theLabel)}')

        self.SetDataLabel(item, theLabel)
        item.setCheckState(0, Qt.Unchecked)
        self.running = False

    @pyqtSlot(Label, Label)
    def Create_TreeItem(self, theLabel:Label, fatherLabel=None):
        self.running = True
        if fatherLabel is None:
            fatheritem = self.root
        else:
            fatheritem = self.item_lookup[fatherLabel]

        item = QTreeWidgetItem(fatheritem)
        self._regist_LabelItem(theLabel, item)
        self.Update(theLabel)

        if fatherLabel is None:
            from OCC.Core.TDF import TDF_ChildIterator
            it = TDF_ChildIterator(theLabel)
            while it.More():
                self.Create_TreeItem(it.Value(), theLabel)
                print('label:', it.Value().GetEntry())
                it.Next()

        self.expandAll()
        self.running = False
        return item

    def _regist_LabelItem(self, label, item):
        self.item_lookup[label] = item
        # self.item_lookup[item] = label

    def onItemDoubleClicked(self, item: QTreeWidgetItem, column: int) -> None:
        self._Selected_item.setBackground(0, self.item_defaultBackground)
        self._Selected_item = item

        if self.IsNamedShape(item):
            aLabel = self.GetLabel(item)
            name = aLabel.GetLabelName()
            Logger().info(f'Selected Item:{name}')

            self._Selected_item.setBackground(0, QBrush(Qt.GlobalColor.lightGray))
            self.sig_labelSelect.emit(aLabel)

    def OnItemChange(self, item:QTreeWidgetItem, col):
        if self.running:
            return 

        if col == 0:
            aLabel = self.GetLabel(item)
            if aLabel is None:
                return 

            if item.checkState(col) == Qt.Checked:
                self.sig_labelCheck.emit(aLabel, True)
            elif item.checkState(col) == Qt.Unchecked:
                self.sig_labelCheck.emit(aLabel, False)
