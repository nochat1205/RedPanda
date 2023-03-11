from utils.OCCUtils import (
    FromText,
    TFunction_Logbook,
    TDataStd_Real,
    TDF_Label,
    TDF_LabelList,
    TDataXtd_Point,
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
    TopoDS_Shape,
    TNaming_Builder
)
from OCC.Core.XCAFDoc import XCAFDoc_Location

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
from utils.decorator import classproperty
class Sym_TransformDriver(Sym_Driver):
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(XCAFDoc_Location)
        self.Attributes['value'] = self.myAttr
        self.Arguments = {
            'angle': Argument(self.tagResource, Sym_RealDriver.ID), 
            'rotateAxis': Argument(self.tagResource, Sym_PntDriver.ID),
            'position': Argument(self.tagResource, Sym_PntDriver.ID),
        }

    def Execute(self, theLabel:TDF_Label, log:TFunction_Logbook)->int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = GetDriver(argu.DriverID).GetValue(theLabel)

        pnt:gp_Pnt = dict_param['rotateAxis']
        coord = pnt.XYZ()
        dir = gp_Dir(coord)
        ax1 = gp_Ax1(gp_Pnt(), dir)

        angle = dict_param['angle']

        position = dict_param['position']

        TRSF = gp_Trsf()
        TRSF.SetRotation(ax1, angle)
        TRSF.SetTranslation(gp_Pnt(), position)
        
        loc = TopLoc_Location(TRSF)
        XCAFDoc_Location.Set(theLabel, loc)
        return 0

    def GetValue(self, theLabel:TDF_Label)->any:
        atype = self.Attributes['value'].Type
        value = atype()
        if theLabel.FindAttribute(atype.GetID(), value):
            return value.Get()

        return value.Get()


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

    def Execute(self, theLabel:TDF_Label, log:TFunction_Logbook)->int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = GetDriver(argu.DriverID).GetValue(theLabel)

        loc:TopLoc_Location = dict_param['transform']
        dx = dict_param['l']
        dy = dict_param['h']
        dz = dict_param['w']

        shape:TopoDS_Shape = BRepPrimAPI_MakeBox(dx, dy, dz).Shape()

        # shape.Located(loc)
        
        # builder = TNaming_Builder(theLabel)
        # builder.Generated(shape)

        return 0



    @classproperty
    def ID(self):
        return  Sym_BoxDriver_GUID #


    @classproperty
    def Type(self):
        return "Box"
