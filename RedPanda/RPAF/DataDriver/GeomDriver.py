from OCC.Core.Geom import Geom_CylindricalSurface, Geom_RectangularTrimmedSurface
from OCC.Core.TNaming import TNaming_Builder
from math import pi

from RedPanda.decorator import classproperty

from RedPanda.Core.topogy import make_face
from RedPanda.Core.data import RP_TOLERANCE

from .BaseDriver import Argument, DataLabelState
from .ShapeBaseDriver import BareShapeDriver, Ax2dDriver, Ax3Driver
from .VarDriver import RealDriver
from ..RD_Label import Label

class CylSurDriver(BareShapeDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Arguments['Ax'] = Argument(self.tagResource, Ax3Driver.ID)
        self.Arguments['radius'] = Argument(self.tagResource, RealDriver.ID)
        self.Arguments['height'] = Argument(self.tagResource, RealDriver.ID)

    def myExecute(self, theLabel: Label) -> int:
        dict_param = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            dict_param[name] = argu.Value(theLabel)

        try:
            cy = Geom_CylindricalSurface(dict_param['Ax'], dict_param['radius'])

            surface = Geom_RectangularTrimmedSurface(cy, 0, 2*pi,
                                                        0, dict_param['height'])

            face = make_face(surface, RP_TOLERANCE)
        except Exception as error:
            DataLabelState.SetError(theLabel, f'{error}', True)
            return 1
                        
        builder = TNaming_Builder(theLabel)
        builder.Generated(face)

        return 0

    @classproperty
    def ID(self):
        from ..GUID import Sym_CurSrvDriver_GUID
        return  Sym_CurSrvDriver_GUID

    @classproperty
    def Type(self):
        return "CylFace"

