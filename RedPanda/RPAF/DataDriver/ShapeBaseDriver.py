from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TPrsStd import TPrsStd_NamedShapeDriver, TPrsStd_AISPresentation

from RedPanda.logger import Logger
from RedPanda.decorator import classproperty
from RedPanda.Core.Euclid import *
from RedPanda.Core.topogy import VertexAnalyst

from ..Attribute import XCAFDoc_Location, TNaming_NamedShape
from ..RD_Label import Label
from ..GUID import Sym_TransformDriver_GUID
from ..DriverTable import DataDriverTable

from .BaseDriver import (
    DataDriver,
    Param,
    Argument,
    DataEnum,
)
from .VarDriver import (
    RealDriver,
)
class BareShapeDriver(DataDriver):
    OutputType = DataEnum.Shape
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TNaming_NamedShape.GetID())
        self.Attributes['value'] = self.myAttr

    def myInit(self, theLabel: Label, theData):
        TPrsStd_AISPresentation.Set(theLabel, TNaming_NamedShape.GetID())
        for name, argu in self.Arguments.items():
            argu:Argument
            aLabel = theLabel.FindChild(argu.Tag)
            aDriver = DataDriverTable.Get().GetDriver(argu.DriverID)
            aDriver.Init(aLabel, theData[name])

        if self.Execute(theLabel) != 0:
            return False

        return True

    def myChange(self, theLabel: Label, theData):
        for name, subData in theData.items():
            argu:Argument = self.Arguments[name]
            aLabel = theLabel.FindChild(argu.Tag)
            aDriver:DataDriver = aLabel.GetDriver()
            if not aDriver.Change(aLabel, subData):
                Logger().debug(f'Entry:{aLabel.GetEntry()} err')
                return False

        if self.Execute(theLabel) != 0:
            return False

        return True

    def GetValue(self, theLabel: Label):
        return self.Attributes['value'].GetValue(theLabel)

from .VertexDriver import (
    PntDriver
)

class TransformDriver(DataDriver):
    OutputType = DataEnum.Shape

    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(XCAFDoc_Location.GetID()) # 存储形式
        self.Attributes['value'] = self.myAttr

        self.Arguments['angle'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['rotateAxis'] = Argument(self.tagResource, PntDriver.ID)
        self.Arguments['position'] = Argument(self.tagResource, PntDriver.ID)

    def Execute(self, theLabel:Label)->int:
        super().Execute(theLabel)

        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        pnt:VertexAnalyst = VertexAnalyst(dict_param['rotateAxis'])
        if pnt.as_pnt == RP_Pnt():
            pnt.x = 1.0

        dir = pnt.as_dir
        ax1 = RP_Ax1(RP_Pnt(), dir)

        angle = dict_param['angle']
        position = VertexAnalyst(dict_param['position']).as_vec

        TrsfRotation = RP_Trsf()
        TrsfRotation.SetRotation(ax1, angle)
        TrsfTrans = RP_Trsf()
        TrsfTrans.SetTranslation(position)
        TRSF:RP_Trsf =  TrsfTrans * TrsfRotation


        loc = TopLoc_Location(TRSF)
        XCAFDoc_Location.Set(theLabel, loc)

        return 0

    def GetValue(self, theLabel:Label)->RP_Trsf: # TODO: 用location 存在问题, 无法正确传出???
        storedValue:TopLoc_Location = super().GetValue(theLabel)
        if storedValue: 
            return storedValue.Transformation()

        return None

    def myChange(self, theLabel: Label, theData):
        for name, subData in theData.items():
            argu:Argument = self.Arguments[name]
            aLabel = theLabel.FindChild(argu.Tag)
            aDriver:DataDriver = aLabel.GetDriver()
            if not aDriver.Change(aLabel, subData):
                Logger().debug(f'Entry:{aLabel.GetEntry()} err')
                return False

        if self.Execute(theLabel) != 0:
            return False

        return True

    @classproperty
    def ID(self):
        return  Sym_TransformDriver_GUID#

    @classproperty
    def Type(self):
        return "Transform"

class ShapeDriver(BareShapeDriver):
    OutputType = DataEnum.Shape
    ViewType = '3D'
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['transform'] = Argument(self.tagResource, TransformDriver.ID)

    # from OCC.Core.AIS import AIS_InteractiveContext
    # def Update(self, theLabel:Label, theContext:AIS_InteractiveContext):
    #     from OCC.Core.AIS import AIS_Shape

    #     aShape = theLabel.GetAttrValue(TNaming_NamedShape.GetID())
    #     if aShape is None:
    #         return False

    #     aloc = aShape.Location()
    #     aisShape:AIS_Shape = AIS_Shape()
    #     if AIS is None:
    #         aisShape = AIS_Shape(aShape)
    #     else:
    #         aisShape = AIS_Shape.DownCast(AIS)
    #         if aisShape is None:
    #             aisShape = AIS_Shape(aShape)
    #         else:
    #             oldShape = AIS_Shape.Shape()
    #             if oldShape != aShape:
    #                 aisShape.ResetTransformation()
    #                 aisShape.SetShape(aShape)
    #                 aisShape.UpdateSelection()
    #                 aisShape.SetToUpdate()
    #     AIS = aisShape
    #     return True

    # def myInit(self, theLabel: Label, theData):
    #     for name, argu in self.Arguments.items():
    #         argu:Argument
    #         aLabel = theLabel.FindChild(argu.Tag)
    #         aDriver = DataDriverTable.Get().GetDriver(argu.DriverID)
    #         aDriver.Init(aLabel, theData[name])
    #     if self.Execute(theLabel) != 0:
    #         return False

    #     return True

    # def myChange(self, theLabel: Label, theData):
    #     for name, subData in theData.items():
    #         argu:Argument = self.Arguments[name]
    #         aLabel = theLabel.FindChild(argu.Tag)
    #         aDriver:DataDriver = aLabel.GetDriver()
    #         if not aDriver.Change(aLabel, subData):
    #             Logger().debug(f'Entry:{aLabel.GetEntry()} err')
    #             return False

    #     if self.Execute(theLabel) != 0:
    #         return False

    #     return True

    # def GetValue(self, theLabel: Label):
    #     return self.Attributes['value'].GetValue(theLabel)
