from PyQt5 import QtGui, QtWidgets, QtCore
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
        
        self.setup_menu()

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
        if item is None:
            return 
        for ind in range(item.childCount()):
            child = item.child(ind)
            if child:
                self.RemoveItem(child.label)

        parentItem = item.parent()
        parentItem.takeChild(parentItem.indexOfChild(item))
        self.treeItem.pop(theLabel)

    def _clear(self):
        self.label = None
        for item in self.treeItem.values():
            try: # TODO
                parent = item.parent()
                if parent is not None:
                    parent.removeChild(item)
                else:
                    self.tree.invisibleRootItem().removeChild(item)

                del item
            except:
                pass

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
        if theLabel in self.treeItem:
            self.treeItem[theLabel] .Update()

    def setup_menu(self):
        from PyQt5.QtWidgets import QMenu
        # create a Qmenu
        self.menu = QMenu(self)
        menu = self.menu
        # add some actions to the menu
        actioncopy = menu.addAction('copy')
        actioncopy.triggered.connect(self.copy)
        actionpaste = menu.addAction('paste')
        actionpaste.triggered.connect(self.paste)

    def copy(self):
        if 'board' not in self.__dict__:
            self.board = dict()

        item = self.currentItem()
        if item is None:
            return

        def collectData(fitem:QTreeWidgetItem):
            from .DriverNode.NameNode import CompuItem, AFItem
            if not isinstance(fitem, CompuItem):
                return fitem.GetText()

            coldata = dict()
            if fitem is None:
                return coldata
            for ind in range(fitem.childCount()):
                item:AFItem = fitem.child(ind)
                if item is None:
                    continue
                if isinstance(item, CompuItem):
                    data = collectData(item)
                    coldata[item.text(0)] = data
                else:
                    coldata[item.text(0)] = item.GetText()
            
            return coldata

        self.board = collectData(item)

    def paste(self):
        if 'board' not in self.__dict__:
            self.board = dict()

        item = self.currentItem()
        if item is None:
            return

        def pasteData(fitem:QTreeWidgetItem, d:dict):
            from .DriverNode.NameNode import CompuItem, AFItem

            if fitem is None:
                return 

            if (not isinstance(d, dict)) and not isinstance(fitem, CompuItem):
                fitem.SetText(d)
                return

            for ind in range(fitem.childCount()):
                item:AFItem = fitem.child(ind)
                if item is None:
                    continue
    
                name = item.text(0)
                if name not in d:
                    continue

                if isinstance(item, CompuItem):
                    pasteData(item, d[name])
                else:
                    item.SetText(d[name])
        
        pasteData(item, self.board)

    def contextMenuEvent(self, a0) -> None:
        item = self.currentItem()
        if item is not None:
            self.menu.exec(self.mapToGlobal(a0.pos()))
        return super().contextMenuEvent(a0)

