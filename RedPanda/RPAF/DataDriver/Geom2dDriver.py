from OCC.Core.Geom2d import Geom2d_Ellipse
from RedPanda.decorator import classproperty
from RedPanda.Core.topogy import EdgeAnalyst

from .BaseDriver import Argument, ShapeRefDriver
from .ShapeBaseDriver import BareShapeDriver, Ax2dDriver
from .VarDriver import RealDriver
from ..RD_Label import Label

class PCurveDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['surface'] = Argument(self.tagResource, ShapeRefDriver.ID)

    def myValue(self, theLabel):
        edge = super().GetValue()
        analyster = EdgeAnalyst(edge)
        face = self.Arguments['surface'].Value(theLabel)
        crv = analyster.pcurve(face)
        return crv

class EllipseDriver(PCurveDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Ax'] = Argument(self.tagResource, Ax2dDriver.ID)
        self.Arguments['Major'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['Minor'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['u0'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['u1'] = Argument(self.tagResource, RealDriver.ID)
        

    def myExecute(self, theLabel: Label) -> int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            aLabel = theLabel.FindChild(argu.Tag)
            dict_param[name] = aLabel.GetAttrValue(self.Attributes['value'].id)
        ellipse1 = Geom2d_Ellipse()

        return super().Execute(theLabel)

    def Type(self):
        return 'EllipseDriver'


    @classproperty
    def ID(self):
        from ..GUID import Sym_EllipseDriver_GUID
        return   Sym_EllipseDriver_GUID#

    @classproperty
    def Type(self):
        return "Ellipse"
