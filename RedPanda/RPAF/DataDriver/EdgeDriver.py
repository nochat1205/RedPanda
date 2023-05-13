
__all__ = ['BezierDriver']

from RedPanda.logger import Logger
from RedPanda.decorator import classproperty
from RedPanda.RPAF.GUID import *

from RedPanda.Core.Make import (
    make_box,
    make_edge,
    make_transform,
    boolean_cut,
)

from ..Attribute import (
    XCAFDoc_Location,
    TNaming_NamedShape,
    TNaming_Builder,
)
from ..RD_Label import Label
from .BaseDriver import (
    Argument,
    Param,
    DataEnum,
    DataLabelState
)
from .ShapeBaseDriver import BareShapeDriver
from .Geom2dDriver import BareShape2dDriver
from .VertexDriver import (
    PntArrayDriver,
)

class BezierDriver(BareShapeDriver):
    OutputType = DataEnum.Edge
    ViewType = '2D'
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['pnts'] = Argument(self.tagResource, PntArrayDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
        from OCC.Extend.ShapeFactory import point_list_to_TColgp_Array1OfPnt
        from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
        from RedPanda.Core.Euclid import RP_Pnt
        
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        pnts:list[RP_Pnt] = dict_param['pnts']
        
        if all(map(lambda x:x==RP_Pnt(0, 0, 0), pnts) ):
            DataLabelState.SetError(theLabel, 'zero line', True)
            return 1 
        try:
            array = point_list_to_TColgp_Array1OfPnt(pnts)
            curve = GeomAPI_PointsToBSpline(array)
            if not curve.IsDone():
                raise Exception('not done')
            shape = BRepBuilderAPI_MakeEdge(curve.Curve()).Edge()
        except Exception as error:
            DataLabelState.SetError(theLabel, str(error), True)
            return 1 

        builder = TNaming_Builder(theLabel)
        builder.Generated(shape)

        return 0

    @classproperty
    def Type(self):
        return 'bspline'

    @classproperty
    def ID(self):
        return Sym_BezierDriver_GUID
