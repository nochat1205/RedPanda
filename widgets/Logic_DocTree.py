# _*_ coding: utf-8 _*_
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QKeySequence as QKSec
from PyQt5.QtGui import QIcon,QBrush
from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget

from OCC.Core.TDF import TDF_Label
from OCC.Core.XCAFDoc import (
    XCAFDoc_DocumentTool
)
from OCC.Core.TDocStd import TDocStd_Document
from PyQt5.QtCore import pyqtSlot

class ModelTree(QtWidgets.QTreeWidget):
    def __init__(self, *args):
        super(ModelTree, self).__init__(*args)
        self.tree = self
        self.tree.expandAll()# 节点全部展开
        self.tree.setStyle(QtWidgets.QStyleFactory.create('windows'))#有加号
        self.tree.setColumnCount(1)# 设置列数
        self.tree.setHeaderLabels(['控件', 'type'])# 设置树形控件头部的标题

        # self.tree_root_dict={}
        # self.tree_root_child_dict = {}

        self.items = list()
        self.main_doc = None
        self.dataRoot = None
    
        # 设置根节点
        self.root = QTreeWidgetItem(self.tree)
        self.root.setText(0, 'Main')
        # self.root.setIcon(0, QIcon('sync.ico'))

        tool_root = QTreeWidgetItem(self.root)
        tool_root.setText(0, '辅助工具')
        # wcs_root.setIcon(0, QIcon('sync.ico'))
        tool_root.setCheckState(0, Qt.Checked)

        # todo 优化2 设置根节点的背景颜色
        #brush_red = QBrush(Qt.red)
        #root.setBackground(0, brush_red)
        #brush_blue = QBrush(Qt.blue)
        #root.setBackground(1, brush_blue)
        # 设置树形控件的列的宽度
        self.tree.setColumnWidth(0, 150)
        # 加载根节点的所有属性与子控件
        # self.tree.addTopLevelItem(root)

    @pyqtSlot(TDocStd_Document)
    def Show(self, doc:TDocStd_Document):
        self.main_doc = doc
        self.Update()

    @pyqtSlot()
    def Update(self):
        self.ClearItems()
        self.Create_ModelTree(self.main_doc)

    def ClearItems(self):
        if self.dataRoot:
            self.root.removeChild(self.dataRoot)
        self.items.clear()

    def Create_ModelTree(self, doc:TDocStd_Document):
        # 设置根节点
        rootLabel = doc.Main()
        from OCC.Core.TDF import (
            TDF_ChildIterator
        )

        def treeNode(label:TDF_Label, father):
            name = label.GetLabelName()
            if len(name) <= 0:
                return 

            item = QTreeWidgetItem(father)
            father = item
            item.setText(0, name)
            item.setCheckState(0, Qt.Checked)
            self.items.append(item)

            it_child = TDF_ChildIterator(label)
            while it_child.More():
                treeNode(it_child.Value(), father)
                it_child.Next()

            return father
        
        self.dataRoot = treeNode(rootLabel, self.root)

    def Create_Child(self):
        pass

    def Updata_Root(self):
        pass

    def Updata_Child(self):
        pass
