from PyQt5.QtWidgets import QTreeWidgetItem

from widgets.Logic_Construct import Logic_Construct
from utils.logger import Logger

class Sym_NewShapeData(object):
    def __init__(self, theInput:Logic_Construct):
        self.driverID = theInput.driverId
        self.dict_params:dict = self.GetParams(theInput.treeRoots["Shape"])
        self.ParentPath = theInput.treeRoots['Parent'].text(1)
        self.name = theInput.treeRoots["Name"].text(1)
        Logger().debug(self.ParentPath)
        Logger().debug(self.name)
        Logger().debug(self.dict_params)

    @staticmethod
    def GetParams(item: QTreeWidgetItem):
        def loadTreeItem(item: QTreeWidgetItem):
            data = {}
            if item.childCount() == 0:
                data[item.text(0)] = item.text(1)
            else:
                child_dict = dict()
                for ind in range(item.childCount()):
                    child_item = item.child(ind)
                    child_dict.update(loadTreeItem(child_item))
                data[item.text(0)] = child_dict
            return data

        return loadTreeItem(item)
