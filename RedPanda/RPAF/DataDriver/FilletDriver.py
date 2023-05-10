from OCC.Core.TNaming import TNaming_Builder, TNaming_NamedShape
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.gp import gp_Ax1, gp_Trsf, gp_Ax2, gp_Ax3
from OCC.Core.AIS import AIS_ColoredShape, AIS_Shaded, AIS_Plane, AIS_TOPL_XYPlane
from OCC.Core.Geom import Geom_Axis2Placement

from RedPanda.RPAF.DisplayContext import DisplayCtx
from RedPanda.logger import Logger
from RedPanda.RPAF.RD_Label import Label
from RedPanda.decorator import classproperty

from .BaseDriver import (
    ShapeRefDriver,
    Argument,
    DataLabelState,
)
from .VarDriver import IntDriver, RealDriver

from .ShapeBaseDriver import (
    BareShapeDriver,
)
from .VertexDriver import PntDriver


class FilletAllDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Shape'] = Argument(self.tagResource, ShapeRefDriver.ID)
        self.Arguments['Radius'] = Argument(self.tagResource, RealDriver.ID)
    
    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
        from OCC.Core.TopExp import TopExp_Explorer
        from OCC.Core.TopAbs import TopAbs_EDGE
        from OCC.Core.TopoDS import topods
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        try:
            shape = dict_param['Shape']
            r = dict_param['Radius']
            builder = BRepFilletAPI_MakeFillet(shape)
            exploer = TopExp_Explorer(shape, TopAbs_EDGE)
            while exploer.More():
                builder.Add(r, topods.Edge(exploer.Current()))
                exploer.Next()
            shape = builder.Shape()
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1
        
        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0


    @classproperty
    def ID(self):
        from ..GUID import Sym_FilAllDriver_GUID
        return  Sym_FilAllDriver_GUID #

    @classproperty
    def Type(self):
        return "FilletAll"
