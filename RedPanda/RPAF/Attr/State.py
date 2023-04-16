from OCC.Core.TDataStd import TDataStd_Integer
from ..GUID import Attr_State_guid

class Attr_State(TDataStd_Integer):
    @staticmethod
    def GetID():
        return Attr_State_guid

