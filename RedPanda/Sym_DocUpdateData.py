from PyQt5.QtWidgets import QTreeWidgetItem

from widgets.Logic_Construct import Logic_Construct
from RedPanda.logger import Logger

class Sym_NewShapeData(object):
    def __init__(self, theInput:Logic_Construct):
        Logger().info('Start Collect New Shape data')
        self.driverID = theInput.driverId        
        self.ParentPath = theInput.treeRoots['Parent'].text(1)
        self.name = theInput.treeRoots["Name"].text(1)
        self.value_dict:dict = self.GetParams(theInput.treeRoots["Shape"])
        Logger().info(f"ParentPath:{self.ParentPath}")
        Logger().info(f"name:{self.name}")
        Logger().info(f"value:{self.value_dict}")
        Logger().info('end Collect New Shape data')

    @staticmethod
    def GetParams(item: QTreeWidgetItem):
        def loadTreeItem(item: QTreeWidgetItem):
            if item.childCount() == 0:
                return item.text(1)
            else:
                child_dict = {}
                for ind in range(item.childCount()):
                    child_item = item.child(ind)
                    child_dict[child_item.text(0)] = loadTreeItem(child_item)
                return child_dict
        return loadTreeItem(item)

class Sym_ChangeData(object):
    def __init__(self, theInput:Logic_Construct):
        Logger().info('Start Collect Change data')
        self.driverID = theInput.driverId        
        self.ParentPath = theInput.treeRoots['Parent'].text(1)
        self.name = theInput.treeRoots["Name"].text(1)
        self.value_dict:dict = self.GetData(theInput.treeRoots["Shape"])
        Logger().info(f"ParentPath:{self.ParentPath}")
        Logger().info(f"name:{self.name}")
        Logger().info(f"value:{self.value_dict}")
        Logger().info('end Collect Change data')

    @staticmethod
    def GetData(item: QTreeWidgetItem):
        def loadTreeItem(item: QTreeWidgetItem):
            if item.childCount() == 0:
                return item.text(1)
            else:
                child_dict = {}
                for ind in range(item.childCount()):
                    child_item = item.child(ind)
                    if Logic_Construct._isChange(child_item):
                        child_dict[child_item.text(0)] = loadTreeItem(child_item)
                return child_dict
        if Logic_Construct._isChange(item):
            return loadTreeItem(item)
        else:
            return {}
