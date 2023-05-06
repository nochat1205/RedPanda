from OCC.Core.TNaming import TNaming_Builder
from OCC.Core.TopoDS import TopoDS_Shape

from RedPanda.logger import Logger
from RedPanda.RPAF.RD_Label import Label
from RedPanda.decorator import classproperty


from .BaseDriver import (
    ShapeRefDriver,
    Argument,
    DataLabelState,
)
from .VarDriver import IntDriver

from .ShapeBaseDriver import (
    BareShapeDriver,
)


class RefSubDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Shape'] = Argument(self.tagResource, ShapeRefDriver.ID)
        self.Arguments['TopoType'] = Argument(self.tagResource, IntDriver.ID)
        self.Arguments['Index'] = Argument(self.tagResource, IntDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        from OCC.Core.TopAbs import TopAbs_COMPOUND, TopAbs_VERTEX
        from OCC.Core.TopExp import TopExp_Explorer

        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        if dict_param['TopoType'] < TopAbs_COMPOUND or  dict_param['TopoType'] > TopAbs_VERTEX:
            DataLabelState.SetError(theLabel, 'TopoEnum Error', True)
            return 1
 
        dict_param['Shape']:TopoDS_Shape
        if dict_param['TopoType'] < dict_param['Shape'].ShapeType():
            DataLabelState.SetError(theLabel, 'TopoEnum is must be sub of Shape')
            return 1

        sub = None
        try:
            explorer = TopExp_Explorer(dict_param['Shape'], self.Arguments['TopoType'])
            i = 0
            while explorer.More():
                i += 1
                if i == self.Arguments['Index']:
                    sub = explorer.Value()
                    break
                explorer.Next()
        except:
            DataLabelState.SetError(theLabel, 'Explorer Error', True)
            return 1

        if sub is None:
            DataLabelState.SetError(theLabel, 'Sub Error', True)
            return 1

        return 0

    @classproperty
    def ID(self):
        from ..GUID import Sym_RefSubDriver_GUID
        return  Sym_RefSubDriver_GUID #

    @classproperty
    def Type(self):
        return "RefSub"


# TNaming_Selector.Select will clear all Attribute, AtFirst

# class SelectorDriver(BareShapeDriver):
#     def __init__(self) -> None:
#         super().__init__()
#         self.Arguments['Shape'] = Argument(self.tagResource, ShapeRefDriver.ID)
#         self.Arguments['TopoType'] = Argument(self.tagResource, IntDriver.ID)
#         self.Arguments['Index'] = Argument(self.tagResource, IntDriver.ID)

#     def myExecute(self, theLabel: Label) -> int:
#         dict_param = dict()
#         for name, argu in self.Arguments.items():
#             argu:Argument
#             dict_param[name] = argu.Value(theLabel)
#         Logger().debug(f'Execute {self.Type}, argu:{dict_param}')
#         try:
#             pass
#         except:
#             pass

#         return 0



