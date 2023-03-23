
__all__ = [
    'TransformDriver',
    'BoxDriver',
    'TransShapeDriver'
]

from OCC.Core.TopLoc import TopLoc_Location

from RedPanda.logger import Logger
from RedPanda.decorator import classproperty
from RedPanda.RDAF.GUID import *


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
    ShapeDriver,
    Argument,
    Param,
    ShapeRefDriver
)
from .VarDriver import (
    RealDriver,
)
from .VertexDriver import (
    PntDriver,
)


class TransformDriver(ShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(XCAFDoc_Location) # 存储形式
        self.Attributes['value'] = self.myAttr
        self.Arguments = {
            'angle': Argument(self.tagResource, RealDriver.ID), 
            'rotateAxis': Argument(self.tagResource, PntDriver.ID),
            'position': Argument(self.tagResource, PntDriver.ID),
        }

    def Execute(self, theLabel:Label)->int:
        super().Execute(theLabel)

        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        pnt:VertexAnalyst = VertexAnalyst(dict_param['rotateAxis'])
        if pnt == RP_Pnt():
            pnt.x = 1.0

        dir = pnt.as_dir
        ax1 = RP_Ax1(RP_Pnt(), dir)

        angle = dict_param['angle']
        position = dict_param['position']

        TrsfRotation = RP_Trsf()
        TrsfRotation.SetRotation(ax1, angle)
        TrsfTrans = RP_Trsf()
        TrsfTrans.SetTranslation(RP_Pnt(), position)
        TRSF:RP_Trsf =  TrsfTrans * TrsfRotation


        loc = TopLoc_Location(TRSF)
        XCAFDoc_Location.Set(theLabel, loc)

        return 0

    def GetValue(self, theLabel:Label)->RP_Trsf: # TODO: 用location 存在问题, 无法正确传出???
        storedValue:TopLoc_Location = super().GetValue(theLabel)
        if storedValue: 
            return storedValue.Transformation()

        return None

    @classproperty
    def ID(self):
        return  Sym_TransformDriver_GUID#

    @classproperty
    def Type(self):
        return "Transform"

class BoxDriver(ShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TNaming_NamedShape)
        self.Attributes['value'] = self.myAttr
        self.Arguments = {
            'transform': Argument(self.tagResource, TransformDriver.ID), 
            'l': Argument(self.tagResource, RealDriver.ID),
            'h': Argument(self.tagResource, RealDriver.ID),
            'w': Argument(self.tagResource, RealDriver.ID),
        }

    def Execute(self, theLabel:Label)->int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            aLabel = theLabel.FindChild(argu.Tag)
            dict_param[name] = aLabel.GetAttrValue(self.Attributes['value'].id)


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
        self.myAttr = Param(TNaming_NamedShape)
        self.Attributes['value'] = self.myAttr
        self.Arguments = {
            'transform': Argument(self.tagResource, TransformDriver.ID), 
            'shape': Argument(self.tagResource, ShapeRefDriver.ID),
        }

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
