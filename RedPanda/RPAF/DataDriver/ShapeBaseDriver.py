from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TPrsStd import TPrsStd_NamedShapeDriver, TPrsStd_AISPresentation
from OCC.Core.TNaming import TNaming_Builder
from OCC.Core.TopoDS import TopoDS_Shape

from RedPanda.logger import Logger
from RedPanda.decorator import classproperty
from RedPanda.Core.Euclid import RP_Ax3, RP_Pnt, RP_Trsf, RP_Ax1
from RedPanda.Core.topogy import VertexAnalyst
from RedPanda.Core.Make import make_plane

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

    def myInit(self, theLabel: Label, theData=None):
        TPrsStd_AISPresentation.Set(theLabel, TNaming_NamedShape.GetID())
        for name, argu in self.Arguments.items():
            argu:Argument
            aLabel = theLabel.FindChild(argu.Tag)
            aDriver = DataDriverTable.Get().GetDriver(argu.DriverID)

            if theData and name in theData:
                aDriver.Init(aLabel, theData[name])
            else: 
                aDriver.Init(aLabel)

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

        if not self.Execute(theLabel):
            return False

        return True

    def myValue(self, theLabel: Label):
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

    def myExecute(self, theLabel:Label)->int:
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

    def myValue(self, theLabel:Label)->RP_Trsf: # TODO: 用location 存在问题, 无法正确传出???
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
        # self.Socket['socket'] = Argument

class Ax3Driver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['P'] = Argument(self.tagResource(), PntDriver.ID)
        self.Arguments['Direction'] = Argument(self.tagResource(), PntDriver.ID)
        self.Arguments['XDirection'] = Argument(self.tagResource(), PntDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        super().Execute(theLabel)

        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        pos = dict_param['P']

        dir:VertexAnalyst = VertexAnalyst(dict_param['Direction'])
        if dir.as_pnt == RP_Pnt():
            dir.z = 1.0
        dir = dir.as_dir

        x_dir = VertexAnalyst(dict_param['XDirection'])
        if x_dir.as_pnt == RP_Pnt():
            x_dir.x = 1.0
        x_dir = x_dir.as_dir()

        ax = RP_Ax3(pos, dir, x_dir)
        plane = make_plane(ax)
        builder = TNaming_Builder()
        builder.Generated(plane)

        return 0

    def myValue(self, theLabel: Label):
        from RedPanda.Core.topogy import FaceAnalyst
        shape:TopoDS_Shape = super().GetValue(theLabel)
        pln = FaceAnalyst(shape).as_pln()
        if pln:
            return pln.Position()
        else:
            return None

    def Type(self):
        return 'Ax3'

from .VertexDriver import Pnt2dDriver
class Ax2dDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['P'] = Argument(self.tagResource, Pnt2dDriver.ID)
        self.Arguments['XDirection'] = Argument(self.tagResource, Pnt2dDriver.ID)

    def myValue(self, theLabel: Label):
        from OCC.Core.gp import gp_Ax2d
        param_dict = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            param_dict[name] = argu.Value(theLabel)

        return gp_Ax2d(param_dict['P'], param_dict['XDirection'])

    @classproperty
    def Type(self):
        return 'Ax2d'

    @classproperty
    def ID(self):
        from ..GUID import Sym_Ax2dDriver_GUID
        return Sym_Ax2dDriver_GUID