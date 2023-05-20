
from OCC.Core.gp import gp_Pln
from OCC.Core.BRep import  BRep_Tool
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TNaming import TNaming_Builder
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.AIS import AIS_ColoredShape, AIS_InteractiveObject
from OCC.Core.gp import gp_Ax2d, gp_Dir2d, gp_Pnt2d

from RedPanda.logger import Logger
from RedPanda.decorator import classproperty
from RedPanda.Core.Euclid import RP_Ax3, RP_Pnt, RP_Trsf, RP_Ax1
from RedPanda.Core.topogy import VertexAnalyst
from ..DisplayContext import DisplayCtx

from RedPanda.RPAF.RD_Label import Label

from ..Attribute import XCAFDoc_Location, TNaming_NamedShape
from ..RD_Label import Label
from ..GUID import Sym_TransformDriver_GUID
from ..DriverTable import DataDriverTable
from ..DisplayContext import DisplayCtx

from .BaseDriver import (
    DataDriver,
    CompoundDriver,
    Param,
    Argument,
    DataEnum,
    DataLabelState
)
from .VarDriver import (
    RealDriver,
)

class BareShapeDriver(CompoundDriver):
    OutputType = DataEnum.Shape
    def __init__(self) -> None:
        super().__init__()
        self.Presentation = dict()

        self.Attributes['value'] = Param(TNaming_NamedShape.GetID())

    def myValue(self, theLabel: Label):
        return self.Attributes['value'].GetValue(theLabel)

    def Prs3d(self, theLabel)->DisplayCtx:
        ais_dict = DisplayCtx(theLabel)
        ais = AIS_ColoredShape(TopoDS_Shape())
        ais_dict[(theLabel, 'shape')] = ais

        self.UpdatePrs3d(theLabel, ais_dict)
        return ais_dict

    def UpdatePrs3d(self, theLabel, ais_dict:DisplayCtx):
        from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
        from OCC.Core.BRepLib import breplib_BuildCurve3d
        from OCC.Core.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface

        import math

        if not DataLabelState.IsOK(theLabel):
            return False

        shape:TopoDS_Shape = theLabel.GetAttrValue(TNaming_NamedShape.GetID())
        if shape.ShapeType() == TopAbs_EDGE:
            breplib_BuildCurve3d(shape)
            adap = BRepAdaptor_Curve(shape)
            if math.isnan(adap.FirstParameter()) or math.isnan(adap.LastParameter()):
                return False
        elif shape.ShapeType() == TopAbs_FACE:
            adap = BRepAdaptor_Surface(shape)
            if (
                math.isnan(adap.FirstUParameter())
            or  math.isnan(adap.FirstVParameter())
            or math.isnan(adap.LastUParameter())
            or math.isnan(adap.LastVParameter())
            ):
                return False

        self.myUpdatePrs3d(theLabel, ais_dict)
        return True

    def myUpdatePrs3d(self, theLabel, ais_dict:DisplayCtx):
        shape = self.Attributes['value'].GetValue(theLabel)
        if shape:
            ais_dict.SetShape((theLabel, 'shape'), shape)

        return True

    def Prs2d(self, theLabel:Label):
        ais_dict = DisplayCtx(theLabel)
        return ais_dict

    def UpdatePrs2d(self, theLabel:Label, ais_dict:DisplayCtx):
        from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
        from OCC.Core.BRepLib import breplib_BuildCurve3d
        from OCC.Core.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
        import math

        if not DataLabelState.IsOK(theLabel):
            return False

        shape:TopoDS_Shape = theLabel.GetAttrValue(TNaming_NamedShape.GetID())
        if shape.ShapeType() == TopAbs_EDGE:
            breplib_BuildCurve3d(shape)
            adap = BRepAdaptor_Curve(shape)
            if math.isnan(adap.FirstParameter()) or math.isnan(adap.LastParameter()):
                return False
        elif shape.ShapeType() == TopAbs_FACE:
            adap = BRepAdaptor_Surface(shape)
            if (
                math.isnan(adap.FirstUParameter())
            or  math.isnan(adap.FirstVParameter())
            or math.isnan(adap.LastUParameter())
            or math.isnan(adap.LastVParameter())
            ):
                return False


        self.myUpdatePrs2d(theLabel, ais_dict)
        return True

    def myUpdatePrs2d(self, theLabel:Label, ais_dict):
        return False


from .VertexDriver import (
    PntDriver
)

class TransformDriver(CompoundDriver):
    OutputType = DataEnum.Shape

    def __init__(self) -> None:
        super().__init__()
        # self.myAttr = Param(XCAFDoc_Location.GetID()) # 存储形式
        # self.Attributes['value'] = self.myAttr

        self.Arguments['angle'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['rotateAxis'] = Argument(self.tagResource, PntDriver.ID)
        self.Arguments['position'] = Argument(self.tagResource, PntDriver.ID)

    def myExecute(self, theLabel:Label)->int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        try:
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

        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        return 0

    def myValue(self, theLabel:Label)->RP_Trsf: # TODO: 用location 存在问题, 无法正确传出
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

        return TRSF

    def myChange(self, theLabel: Label, theData):
        if not isinstance(theData, dict):
            return False
        for name, subData in theData.items():
            argu:Argument = self.Arguments[name]
            aLabel = theLabel.FindChild(argu.Tag)
            aDriver:DataDriver = aLabel.GetDriver()
            if not aDriver.Change(aLabel, subData):
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

class Ax3Driver(CompoundDriver):
    def __init__(self) -> None:
        super().__init__()
        
        self.Attributes['value'] = Param(TNaming_NamedShape.GetID())

        self.Arguments['P'] = Argument(self.tagResource, PntDriver.ID)
        self.Arguments['Direction'] = Argument(self.tagResource, PntDriver.ID)
        self.Arguments['XDirection'] = Argument(self.tagResource, PntDriver.ID)

    def myExecute(self, theLabel: Label) -> int:

        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        pos = dict_param['P']
        pos = BRep_Tool.Pnt(pos)

        dir:VertexAnalyst = VertexAnalyst(dict_param['Direction'])
        if dir.as_pnt == RP_Pnt():
            dir.z = 1.0
        dir = dir.as_dir

        x_dir = VertexAnalyst(dict_param['XDirection'])
        if x_dir.as_pnt == RP_Pnt():
            x_dir.x = 1.0
        x_dir = x_dir.as_dir

        try:
            ax = RP_Ax3(pos, dir, x_dir)

        except:
            DataLabelState.SetError(theLabel, f'Argu:{pos}, {dir}, {x_dir} is not accept')
            return 1

        gp_pln = gp_Pln(ax)
        plane = BRepBuilderAPI_MakeFace(gp_pln).Face()

        builder = TNaming_Builder(theLabel)
        builder.Generated(plane)

        return 0

    def myValue(self, theLabel: Label):
        from RedPanda.Core.topogy import FaceAnalyst

        shape:TopoDS_Shape = self.Attributes['value'].GetValue(theLabel)
        pln = FaceAnalyst(shape).as_pln()

        if pln:
            return pln.Position()
        else:
            return None

    @classproperty
    def Type(self):
        return 'Ax3'

    @classproperty
    def ID(self):
        from ..GUID import Sym_Ax3Driver_GUID
        return Sym_Ax3Driver_GUID

from .VertexDriver import Pnt2dDriver
class Ax2dDriver(CompoundDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['P'] = Argument(self.tagResource, Pnt2dDriver.ID)
        self.Arguments['XDirection'] = Argument(self.tagResource, Pnt2dDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        try:
            self.myValue(theLabel)
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1

        return 0

    def myValue(self, theLabel: Label):
        param_dict = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            param_dict[name] = argu.Value(theLabel)

        pnt = param_dict['P']
        pnt_d:gp_Pnt2d = param_dict['XDirection']
        dir = gp_Dir2d(*pnt_d.Coord())
        return gp_Ax2d(pnt, dir)

    @classproperty
    def Type(self):
        return 'Ax2d'

    @classproperty
    def ID(self):
        from ..GUID import Sym_Ax2dDriver_GUID
        return Sym_Ax2dDriver_GUID



class ConstShapeDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Attributes['value'] = Param(TNaming_NamedShape.GetID())

    def myInit(self, theLabel, theData:TopoDS_Shape):
        builder = TNaming_Builder(theLabel)
        builder.Generated(theData)
        return True

    def myChange(self, theLabel: Label, theData: tuple):
        return True

    def  myValue(self, theLabel: Label):
        return self.Attributes['value'].GetValue(theLabel)

    @classproperty
    def ID(self):
        from ..GUID import Sym_ConstShapebDriver_GUID
        return Sym_ConstShapebDriver_GUID

    @classproperty
    def Type(self):
        """ 函数名
        """
        return 'ConstShape'


