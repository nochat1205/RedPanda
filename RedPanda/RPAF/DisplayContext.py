from OCC.Core.AIS import AIS_ColoredShape
from OCC.Core.TopoDS import TopoDS_Shape
from .RD_Label import Label

class DisplayCtx(object):
    
    def __init__(self, aLabel:Label) -> None:
        self.label = aLabel
        self.d = dict()
        self.aisToLabel = dict()
        self.bounds = (-10, 10, -10, 10)
        self.shapeToLabel_d:dict[TopoDS_Shape, Label] = dict()

    def __getitem__(self, key):
        return self.d.get(key, None)

    def __setitem__(self, key:tuple[Label, str], value):
        self.d[key] = value
        # self.aisToLabel[value] = key[0]

    def GetLabel(self, ais:AIS_ColoredShape):
        from RedPanda.RPAF.DataDriver import ShapeRefDriver
        shape = ais.Shape()
        if shape in self.shapeToLabel_d:
            aLabel = self.shapeToLabel_d[shape]
            aDriver = aLabel.GetDriver()
            if aDriver and aDriver.ID == ShapeRefDriver.ID:
                return aDriver.GetRefLabel(aLabel)
            return aLabel
        return None

    def SetShape(self, key, shape):
        from OCC.Core.TopAbs import TopAbs_EDGE
        from OCC.Core.BRepLib import breplib_BuildCurve3d
        if shape.ShapeType() == TopAbs_EDGE:
            breplib_BuildCurve3d(shape)

        if key in self.d:
            # ref sub
            if key[1] == 'shape':
                old = self.d[key].Shape()
                if old in self.shapeToLabel_d:
                    self.shapeToLabel_d.pop(old)
                self.shapeToLabel_d[shape] = key[0]

            context = self.d[key].GetContext()
            if context:
                context.Remove(self.d[key], False)

            self.d[key].SetShape(shape)

    def values(self):
        return self.d.values()

    def GetBound(self):
        return self.bounds
