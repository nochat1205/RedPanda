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
from RedPanda.OCCUtils import (
    TDF_Label,
    TDF_Tool,
    TCollection_AsciiString,
    TDocStd_Document,
    TDF_ChildIterator,
)

from RedPanda.Driver.Sym_Driver import (
    GetDriver,
    GetEntry,
    GetFunctionID
)
from RedPanda.Sym_ParamBuilder import (
    Sym_ChangeBuilder
)
from RedPanda.logger import Logger

class ModelTree(QtWidgets.QTreeWidget):
    sig_select = pyqtSignal(Sym_ChangeBuilder)
    def __init__(self, *args):
        super(ModelTree, self).__init__(*args)
        self.tree = self
        self.tree.expandAll()# 节点全部展开
        self.tree.setStyle(QtWidgets.QStyleFactory.create('windows'))#有加号
        self.tree.setColumnCount(2) # 设置列数
        self.tree.setHeaderLabels(['name', 'type'])# 设置树形控件头部的标题

        self.items = list()
        self.main_doc = None
        self.dataRoot = None
        self._Selected_item = None
        self.item_defaultBackground = None

        # 设置根节点
        self.root = QTreeWidgetItem(self.tree)
        self._Selected_item = self.root
        self.item_defaultBackground = self.root.background(0)    
        self.root.setText(0, 'Main')
        # self.root.setIcon(0, QIcon('sync.ico'))

        tool_root = QTreeWidgetItem(self.root)
        tool_root.setText(0, '辅助工具')
        # wcs_root.setIcon(0, QIcon('sync.ico'))
        tool_root.setCheckState(0, Qt.Checked)
        self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置树形控件的列的宽度
        self.tree.setColumnWidth(0, 150)



        self.itemDoubleClicked.connect(self.onItemDoubleClicked)

        # todo 优化2 设置根节点的背景颜色
        #brush_red = QBrush(Qt.red)
        #root.setBackground(0, brush_red)
        #brush_blue = QBrush(Qt.blue)
        #root.setBackground(1, brush_blue)
        # 加载根节点的所有属性与子控件
        # self.tree.addTopLevelItem(root)

    def onItemDoubleClicked(self, item: QTreeWidgetItem, column: int) -> None:
        self._Selected_item.setBackground(0, self.item_defaultBackground)
        self._Selected_item = item
        if self.IsNamedShape(item):
            aLabel = self.GetLabel(item)
            name = aLabel.GetLabelName()
            Logger().info(f'Selected Item:{name}')

            self._Selected_item.setBackground(0, QBrush(Qt.GlobalColor.lightGray))
            self.sig_select.emit(Sym_ChangeBuilder(aLabel))

    @pyqtSlot(TDocStd_Document)
    def Show(self, doc:TDocStd_Document):
        self.main_doc = doc
        self.Update()

    @pyqtSlot()
    def Update(self):
        self.ClearItems()
        self.Create_ModelTree(self.main_doc)
        self.tree.expandAll()

    def ClearItems(self):
        self._Selected_item = self.root
        if self.dataRoot:
            self.root.removeChild(self.dataRoot)
        self.items.clear()

    def Create_ModelTree(self, doc:TDocStd_Document):
        # 设置根节点
        rootLabel = doc.Main()

        def treeNode(theLabel:TDF_Label, father):
            name = theLabel.GetLabelName()
            if len(name) <= 0:
                return

            anEntry = GetEntry(theLabel)
            # Logger().info(f'Entry:{anEntry} name:{name}')
            aDriver = GetDriver(theLabel)

            item = QTreeWidgetItem(father)
            father = item
            self.items.append(item)

            item.setText(0, f'{anEntry} {name}')
            if aDriver:
                item.setText(1, f'{aDriver.Type}')
            self.SetDataLabel(item, theLabel)

            item.setCheckState(0, Qt.Checked)

            it_child = TDF_ChildIterator(theLabel)
            while it_child.More():
                treeNode(it_child.Value(), father)
                it_child.Next()

            return father

        self.dataRoot = treeNode(rootLabel, self.root)

    @staticmethod
    def SetDataLabel(item:QTreeWidgetItem, theLabel:TDF_Label):
        if GetFunctionID(theLabel):
            item.setData(2, Qt.ItemDataRole.UserRole+1, True)
        item.setData(2, Qt.ItemDataRole.UserRole, theLabel)

    @staticmethod
    def IsNamedShape(item:QTreeWidgetItem):
        return item.data(2, Qt.ItemDataRole.UserRole+1)

    @staticmethod
    def GetLabel(item:QTreeWidgetItem):
        return item.data(2, Qt.ItemDataRole.UserRole)
