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
    BRepBuilderAPI_Transform,
    TopoDS_Shape,
    TNaming_Builder,
    XCAFDoc_Location

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
            aDriver = GetDriver(argu.DriverID)
            aLabel = theLabel.FindChild(argu.Tag)

            dict_param[name] = aDriver.GetValue(aLabel)

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
        
        Logger().debug("Start:"+coord.DumpJsonToString())
        Logger().debug(position.DumpJsonToString())
        Logger().debug(dir.DumpJsonToString())
        Logger().debug("loc:"+loc.ShallowDumpToString())
        XCAFDoc_Location.Set(theLabel, loc)

        return 0

    def GetValue(self, theLabel:TDF_Label)->TopLoc_Location:
        atype = self.Attributes['value'].Type
        value = atype()
        if theLabel.FindAttribute(atype.GetID(), value):
            Logger().debug("XCAFL:"+value.DumpJsonToString())
            loc:TopLoc_Location = value.Get()
            Logger().debug("ValueLoc2:"+loc.DumpJsonToString())
            print(id(loc), id(value.Get()))        
            return value.Get()

        Logger().debug("Return None")
        return TopLoc_Location()


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
        Logger().debug("Run")
        for name, argu in self.Arguments.items():
            argu:Argument
            aLabel = theLabel.FindChild(argu.Tag)
            aDriver:Sym_Driver = GetDriver(argu.DriverID)
            # Logger().debug()
            if name == 'transform':
                Logger().debug("LocLoc3:"+aDriver.GetValue(aLabel).DumpJsonToString())
            dict_param[name] = aDriver.GetValue(aLabel)
            Logger().debug("name:"+name+',tag:'+str(argu.Tag)+',type:'+str(type(dict_param[name]))
                           +',ID:'+str(argu.DriverID))

        loc:TopLoc_Location = dict_param['transform']
        Logger().debug("LocLoc0:"+dict_param['transform'].DumpJsonToString())
        Logger().debug("LocLoc:"+loc.DumpJsonToString())
        Logger().debug(loc.Transformation().DumpJsonToString())
        dx = dict_param['l']
        dy = dict_param['h']
        dz = dict_param['w']

        api = BRepPrimAPI_MakeBox(dx, dy, dz)
        Logger().debug("run")
        api.Build()
        Logger().debug("run")
        if not api.IsDone():
            Logger().debug("MakeBox Failed.")
            Logger().debug(dict_param.__str__())
            Logger().debug(str(dx)+":"+str(dy)+":"+str(dz))
            return 1

        Logger().debug("run")
        shape = api.Shape()
        Logger().debug("run")
        trsf = loc.Transformation()
        Logger().debug("run")

        api = BRepBuilderAPI_Transform(shape, trsf)
        api.Build()
        if not api.IsDone():
            Logger().debug("Transform Failed")
            return 1

        shape = api.Shape()

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0



    @classproperty
    def ID(self):
        return  Sym_BoxDriver_GUID #


    @classproperty
    def Type(self):
        return "Box"
