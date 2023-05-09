
from OCC.Core.AIS import AIS_ColoredShape
from OCC.Core.XCAFPrs import XCAFPrs_AISObject

from .RD_Label import Label

class DisplayCtx(object):
    
    def __init__(self, aLabel:Label) -> None:
        self.d = dict()
        self.aisToLabel = dict()
        self.bounds = (0, 10, 0, 10)

    def __getitem__(self, key):
        return self.d[key]

    def __setitem__(self, key:tuple[Label, str], value):
        self.d[key] = value
        # self.aisToLabel[value] = key[0]

    def GetLabel(self, ais:XCAFPrs_AISObject):
        from RedPanda.RPAF.DataDriver import ShapeRefDriver
        aLabel = ais.GetLabel()
        aDriver = aLabel.GetDriver()
        if aDriver and aDriver.ID == ShapeRefDriver.ID:
            return aDriver.GetRefLabel(aLabel)
        return aLabel

    def values(self):
        return self.d.values()

    def GetBound(self):
        return self.bounds
