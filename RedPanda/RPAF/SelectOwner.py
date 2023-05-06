
from OCC.Core.StdSelect import StdSelect_BRepOwner
from RedPanda.RPAF.RD_Label import Label

class SelectOwner(StdSelect_BRepOwner):
    def __init__(self, theLabel:Label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.myLabel = theLabel

    def Label(self):
        return self.myLabel



