
from OCC.Core.AIS import AIS_Shape


from .RD_Label import Label

class DisplayCtx(object):
    
    def __init__(self, aLabel:Label) -> None:
        self.d = dict()

        self.u0 = 0
        self.u1 = 1

        self.v0 = 0
        self.v1 = 1

    def __getitem__(self, key):
        return self.d[key]

    def __setitem__(self, key, value):
        self.d[key] = value

    def values(self):
        return self.d.values()

    def GetBound(self):
        return (self.u0, self.u1, self.v0, self.v1)