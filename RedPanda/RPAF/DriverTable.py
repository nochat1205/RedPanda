
from OCC.Core.TDF import (
    tdf_ProgIDFromGUID,
    TDF_LabelMap
)
from OCC.Core.TFunction import TFunction_Logbook

from RedPanda.Core.data import (
    RP_GUID,
    RP_Transient,
    RP_ExtendStr
)
from RedPanda.logger import Logger
from RedPanda.RD_Singleton import Singleton

from .DataDriver.BaseDriver import DataDriver
from .RD_Label import Label

def _ShallowCopy(dest, src):
    dest.__class__ = src.__class__ # 
    dest.__dict__ = src.__dict__

    # __annotations__
    # __doc__
    # __module__

# Driver Table
class DataDriverTable(RP_Transient, Singleton):
    _myDrivers:dict = dict()
    # _myThreadDrivers = TFunction_HArray1OfDataMapOfGUIDDriver()
    def __init__(self, *args) -> None:
        return 
        # super().__init__(*args)

    def Get():
        if not hasattr(DataDriverTable, '_instance'):
            DataDriverTable()

        return DataDriverTable._instance

    def AddDriver(self, guid:RP_GUID, 
                  driver:DataDriver)->bool:

        self._myDrivers[guid] = driver
        return self.HasDriver(guid)

    def HasDriver(self, guid:RP_GUID)->bool:
        
        return guid in self._myDrivers.keys()

    def GetDriver(self, guid:RP_GUID)->bool:
        aDriver = DataDriver()
        if self.HasDriver(guid):
            _ShallowCopy(aDriver, self._myDrivers.get(guid))
            return aDriver

        Logger().warn(f'Driver:{guid} not found')

        return None

    def __str__(self):
        str_data = str()
        for guid, driver in self._myDrivers.items():
            str_data += guid.ShallowDumpToString() + '\t'
            es = RP_ExtendStr()
            if tdf_ProgIDFromGUID(guid, es):
                str_data += es
            str_data += '\n'
        return str_data

    def RemoveDriver(self, guid:RP_GUID):
        self._myDrivers.pop(guid)

    def Clear(self):
        self._myDrivers.clear()

