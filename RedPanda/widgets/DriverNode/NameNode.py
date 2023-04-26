from __future__ import annotations
from RedPanda.RPAF.RD_Label import Label
from RedPanda.RPAF.DataDriver.BaseDriver import DataDriver, VarDriver, ShapeRefDriver, ArrayDriver
from RedPanda.RPAF.DataDriver.ShapeBaseDriver import BareShapeDriver
from RedPanda.logger import Logger

from PyQt5.QtWidgets import (
    QTreeWidgetItem, QLineEdit, QTreeWidget, QSpinBox
)
from PyQt5.QtCore import (
    pyqtSignal, pyqtSlot, QObject,
    QSignalMapper
)



# 数值显示组件
class myLine(QLineEdit):
    sig_change = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editingFinished.connect(
            lambda:self.SigChange.emit())

    def UpdateValue(self, text:str):
        self.blockSignals(True)
        self.setText(text)
        self.blockSignals(False)

    def GetText(self):
        return self.text()

    @property
    def SigChange(self):
        return self.sig_change

class mySpinBox(QSpinBox):
    sig_change = pyqtSignal()
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.editingFinished.connect(
            lambda:self.SigChange.emit()
        )

    def UpdateValue(self, int):
        self.blockSignals(True)
        self.setValue(int(int))
        self.blockSignals(False)

    def GetText(self):
        return self.text

    @property
    def SigChange(self):
        return self.sig_change

'''
    1. 务必区分用户输入和程序更改
    2. 向Contruct view 注册
'''
class MyItem(QTreeWidgetItem):
    '''
        name, value, state
    '''
    def __init__(self, name, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label:Label = label # 所表示的节点
        self.driver:DataDriver = label.GetDriver()

        self.setTitle(name)

    def setTitle(self, title:str):
        self.setText(0, title)

    def SigChange(self):
        raise NotImplemented()

# properties item
class NameItem(MyItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setui()

    def setui(self):
        line = myLine()
        self.textContainer:myLine = line
        self.textContainer.setText(self.label.GetLabelName())

        tree:QTreeWidget = self.treeWidget()
        tree.setItemWidget(self, 1, line)

    def onLainUpdate(self): # 程序更新不触发事件
        self.textContainer.setText(self.label.GetLabelName())

    def GetText(self):
        return self.textContainer.text()

# data label item
class AFItemFactory:
    @staticmethod
    def GetItem(name:str, aLabel:Label, parent):
        aDriver = aLabel.GetDriver()
        if isinstance(aDriver, ArrayDriver):
            return ArrayItem(name, aLabel, parent)

        elif isinstance(aDriver, ShapeRefDriver):
            return VarItem(name, aLabel, parent)

        elif isinstance(aDriver, VarDriver):
            return VarItem(name, aLabel, parent)

        elif isinstance(aDriver, DataDriver):
            return CompuItem(name, aLabel, parent)

        else:
            Logger().warn('None Driver')
            return None

class AFItem(MyItem): # afItem 区分节点
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textContainer = None

        self._setui()
        self._register()

    def _setui(self):
        raise NotImplemented()

    def _register(self):
        from ..Logic_Construct import Logic_Construct
        self.treeWidget().Rigister(self.label, self)

    @property
    def TextContainer(self):
        return self.textContainer

    @property
    def SigChange(self):
        raise NotImplemented()

    def GetText(self):
        return self.textContainer.GetText()

    def Update(self):
        raise NotImplemented()

    def _setState(self):
        self.setText(2, self.driver.GetStateMsg(self.label))

class VarItem(AFItem):
    def _setui(self):
        # data
        line = myLine()
        line.UpdateValue(self.driver.GetTextValue(self.label))

        tree:QTreeWidget = self.treeWidget()
        tree.setItemWidget(self, 1, line)
        self.textContainer:myLine = line

        # state
        self._setState()

    @property
    def SigChange(self):
        return self.textContainer.SigChange

    def Update(self):
        self.textContainer.UpdateValue (self.driver.GetTextValue(self.label))
        self._setState()

class ArrayItem(AFItem):
    @property
    def SigChange(self):
        return self.textContainer.SigChange

    def _setui(self):
        # data
        spbox:mySpinBox = mySpinBox()

        spbox.setMinimum(0)
        spbox.setMaximum(20)
        spbox.setSingleStep(1)

        tree:QTreeWidget = self.treeWidget
        tree.setItemWidget(self, 1, spbox)
    
        self.textContainer:mySpinBox = spbox
        
        # setState
        self._setState()
    
        # set child
        self._setChild()


    def _setChild(self):
        dt = self.driver.GetNamedArgument(self.label)
        for name, sub in dt.items():
            AFItemFactory.GetItem(name, sub, self)

        return 

    def Update(self):
        # update self
        aLabel = self.label
        self.driver:ArrayDriver
        nowsize = self.driver.GetSize()
        self.textContainer.UpdateValue(nowsize)

        self._setState()

        childItemSize = self.childCount()
        if nowsize > childItemSize:
            for ind in range(childItemSize, nowsize):
                name, sub = self.driver.GetChildAndName(aLabel, ind)
                AFItemFactory.GetItem(name, sub, self)

        elif nowsize < childItemSize:
            sub_list = self.driver.GetArguLabel(self.label)
            for ind in range(childItemSize):
                child:AFItem = self.child(ind)
                if child.label not in sub_list:
                    self.treeWidget.RemoveItem(child.label)

class CompuItem(AFItem):
    @property
    def SigChange(self):
        return None

    def _setui(self):
        self._setState()
        
        self._setChild()
        return 

    def _setChild(self):
        dt = self.driver.GetNamedArgument(self.label)
        for name, sub in dt.items():
            AFItemFactory.GetItem(name, sub, self)

    def Update(self):
        self._setState()                
