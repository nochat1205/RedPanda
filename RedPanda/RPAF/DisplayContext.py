
from OCC.Core.AIS import AIS_Shape


from .RD_Label import Label

class DisplayCtx(object):
    
    def __init__(self, aLabel:Label) -> None:
        self.d = dict()
        self.aisToLabel = dict()
        self.bounds = (0, 1, 0, 1)

    def __getitem__(self, key):
        return self.d[key]

    def __setitem__(self, key:tuple[Label, str], value):
        self.d[key] = value
        self.aisToLabel[value] = key[0]
        print('id:', id(value), ' ', hash(value))

    def GetLabel(self, ais):
        return self.aisToLabel.get(ais, None)

    def values(self):
        return self.d.values()

    def GetBound(self):
        return self.bounds
