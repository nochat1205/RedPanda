from utils.OCCUtils import (
    FromText,
    TFunction_Logbook,
    TDataStd_Real,
    TDF_Label,
    TDF_LabelList,
    gp_Pnt,
    gp_Trsf,
    gp_Vec,
    gp_Lin,
    gp_Ax1,
    gp_Dir,
    gp_XYZ,
    TNaming_NamedShape,
    TopLoc_Location,
    BRepPrimAPI_MakeBox,
    BRepBuilderAPI_Transform,
    TopoDS_Shape,
    TNaming_Builder,
    XCAFDoc_Location,
    TCollection_AsciiString,
    TDF_Tool,

)
from OCC.Core.Message import Message_ProgressRange

from utils.GUID import *

from utils.Driver.Sym_Driver import (
    Sym_Driver,
    GetDriver,
    Argument,
    Param,
)

from utils.Driver.Sym_DataDriver import (
    Sym_RealDriver,
)
from utils.Driver.Sym_GPDriver import (
    Sym_PntDriver,
)
from utils.logger import Logger

from utils.decorator import classproperty

class Sym_TransformDriver(Sym_Driver):
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(XCAFDoc_Location) # 存储形式
        self.Attributes['value'] = self.myAttr
        self.Arguments = {
            'angle': Argument(self.tagResource, Sym_RealDriver.ID), 
            'rotateAxis': Argument(self.tagResource, Sym_PntDriver.ID),
            'position': Argument(self.tagResource, Sym_PntDriver.ID),
        }

    def Execute(self, theLabel:TDF_Label)->int:
        super().Execute(theLabel)

        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        pnt:gp_Pnt = dict_param['rotateAxis']
        if pnt.IsEqual(gp_Pnt(), 0.0001):
            pnt.SetX(1.0)

        coord:gp_XYZ = pnt.XYZ()
        dir = gp_Dir(coord)
        ax1 = gp_Ax1(gp_Pnt(), dir)

        angle = dict_param['angle']
        position = dict_param['position']

        TrsfRotation = gp_Trsf()
        TrsfRotation.SetRotation(ax1, angle)
        TrsfTrans = gp_Trsf()
        TrsfTrans.SetTranslation(gp_Pnt(), position)
        TRSF:gp_Trsf =  TrsfTrans * TrsfRotation


        loc = TopLoc_Location(TRSF)
        XCAFDoc_Location.Set(theLabel, loc)

        entry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, entry)

        Logger().info(f"Entry:{entry} Make {self.Type} Success")

        return 0

    def GetValue(self, theLabel:TDF_Label)->gp_Trsf: # TODO: 用location 存在问题, 无法正确传出???
        """ 从存储形式中获取实际数据
            ref self.myAttr
        """
        aEntry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, aEntry)
        storedValue:TopLoc_Location = self.GetStoredValue(theLabel)
        if storedValue:            
            Logger().debug(f"Entry:{aEntry} get Trsf:{storedValue.DumpJsonToString()}")

            return storedValue.Transformation()

        Logger().warn(f"Entry:{aEntry} not found transfrom")

        return None

    @classproperty
    def ID(self):
        return  Sym_TransformDriver_GUID#

    @classproperty
    def Type(self):
        return "Transform"

class Sym_BoxDriver(Sym_Driver):
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(TNaming_NamedShape)
        self.Attributes['value'] = self.myAttr
        self.Arguments = {
            'transform': Argument(self.tagResource, Sym_TransformDriver.ID), 
            'l': Argument(self.tagResource, Sym_RealDriver.ID),
            'h': Argument(self.tagResource, Sym_RealDriver.ID),
            'w': Argument(self.tagResource, Sym_RealDriver.ID),
        }

    def Execute(self, theLabel:TDF_Label)->int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            aLabel = theLabel.FindChild(argu.Tag)
            aDriver:Sym_Driver = GetDriver(argu.DriverID)
            dict_param[name] = aDriver.GetValue(aLabel)

        Logger().info(f"Driver:{self.Type} Execute {dict_param}")

        trsf:gp_Trsf = dict_param['transform']
        dx = dict_param['l']
        dy = dict_param['h']
        dz = dict_param['w']

        api = BRepPrimAPI_MakeBox(dx, dy, dz)
        api.Build()
        if not api.IsDone():
            Logger().warn("MakeBox Failed.")
            Logger().warn(dict_param.__str__())
            Logger().warn(str(dx)+":"+str(dy)+":"+str(dz))
            return 1

        shape = api.Shape()

        api = BRepBuilderAPI_Transform(shape, trsf)
        api.Build()
        if not api.IsDone():
            Logger().warn("Transform Failed")
            return 1

        shape = api.Shape()

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)


        entry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, entry)


        NS = TNaming_NamedShape()
        if not theLabel.FindAttribute(NS.GetID(), NS):
            Logger().warn(f"Entry:{entry} execute error")
            return 1

        if NS.Get() is None:
            Logger().warn(f"Entry:{entry} execute error")
            return 1

        return 0

    @classproperty
    def ID(self):
        return  Sym_BoxDriver_GUID #

    @classproperty
    def Type(self):
        return "Box"
