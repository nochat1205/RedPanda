from OCC.Core.TDataStd import TDataStd_Integer
from OCC.Core.TDF import TDF_Label
from ..GUID import Attr_State_guid, Attr_Exist_GUID

class Attr_State(TDataStd_Integer):
    @staticmethod
    def GetID():
        return Attr_State_guid
    @staticmethod
    def Set(theLabel:TDF_Label, value):
        TDataStd_Integer.Set(theLabel, Attr_State.GetID(), value)

class Attr_Exist(TDataStd_Integer):
    @staticmethod
    def GetID():
        return Attr_Exist_GUID
