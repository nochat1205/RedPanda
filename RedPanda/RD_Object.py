from collections import namedtuple

from RedPanda.logger import logging
from RedPanda.RPAF.RD_Label import Label
from RedPanda.RPAF.Document import Document
from RedPanda.RPAF.DriverTable import DataDriverTable
# namedtuple('LabelContext', ['Entry', 'Label', 'Driver', 'widget', 'WidgetItem'])
class RDObject(object):
    """ stored all message which is relative to label on runtime. 

    Args:
        object (_type_): _description_
    """
    def __init__(self, theLabel:Label):
        self.label = theLabel.Data()

        self.doc = Document.Get(self.label)

        self.viewer = None
        self.tree_item = None
        self.shape = None

        self._secondary_prs = []

    def GetDriver(self):
        return self.Label.GetDriver()

    def GetTreeItem(self):
        return self.tree_item

    def UpdatePresentation(self):
        return

class RDObjectManager(object):
    def __init__(self) -> None:
        self.RDObject_dict:dict[Label, RDObject] = dict()

    def Add(self, theLabel:Label)->RDObject:
        self.RDObject_dict[theLabel] = RDObject(theLabel)
        return self.RDObject_dict[theLabel]

    def __getitem__(self, key):
        return self.RDObject_dict[key]
