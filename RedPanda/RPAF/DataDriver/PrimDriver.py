
__all__ = [
    'TransformDriver',
    'BoxDriver',
    'TransShapeDriver'
]

from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.AIS import AIS_Shape, AIS_InteractiveContext

from RedPanda.logger import Logger
from RedPanda.decorator import classproperty
from RedPanda.RPAF.GUID import *


from RedPanda.Core.data import RP_AsciiStr
from RedPanda.Core.Euclid import (
    RP_Pnt,
    RP_Ax1,
    RP_Trsf,
)
from RedPanda.Core.Make import (
    make_box,
    make_transform,
)
from RedPanda.Core.topogy import VertexAnalyst

from ..Attribute import (
    XCAFDoc_Location,
    TNaming_NamedShape,
    TNaming_Builder,
)
from ..RD_Label import Label
from .BaseDriver import (
    DataDriver,
    Argument,
    Param,
    DataEnum,
    ShapeRefDriver
)
from .VarDriver import (
    RealDriver,
)
from .VertexDriver import (
    PntDriver,
)
from .ShapeBaseDriver import ShapeDriver

from ..DriverTable import DataDriverTable

class BoxDriver(ShapeDriver):
    def __init__(self) -> None:
        super().__init__()

        self.Arguments['l'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['h'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['w'] = Argument(self.tagResource, RealDriver.ID)

    def Execute(self, theLabel:Label)->int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        trsf:RP_Trsf = dict_param['transform']
        dx = dict_param['l']
        dy = dict_param['h']
        dz = dict_param['w']

        shape = make_box(dx, dy, dz)

        shape = make_transform(shape, trsf)

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0

    @classproperty
    def ID(self):
        return  Sym_BoxDriver_GUID #

    @classproperty
    def Type(self):
        return "Box"

class TransShapeDriver(ShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['shape'] = Argument(self.tagResource, ShapeRefDriver.ID)

    def Execute(self, theLabel:Label)->int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            aLabel = theLabel.FindChild(argu.Tag)
            dict_param[name] = aLabel.GetAttrValue(self.Attributes['value'].id)


        trsf:RP_Trsf = dict_param['transform']
        shape = dict_param['transform']

        shape = make_transform(shape, trsf)

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0

    @classproperty
    def ID(self):
        return  Sym_TransShapeDriver_GUID #

    @classproperty
    def Type(self):
        return "TransShape"
