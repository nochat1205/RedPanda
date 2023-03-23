from typing import Union
# standard
from OCC.Core.Standard import *

# TCol
from OCC.Core.TCollection import *


_std = ['RP_GUID']
_col = [
        'RP_AsciiStr',
        'RP_ExtendStr',
        'RP_Transient'
]

__all__ = [*_std, *_col, 'RP_TOLERANCE']

RP_TOLERANCE = 1e-6

RP_ExtendStr = TCollection_ExtendedString
RP_Transient = Standard_Transient

class RP_AsciiStr(TCollection_AsciiString):
    def __str__(self):
        return self.PrintToString()

    def __repr__(self) -> str:
        return self.__str__()

_GUIDHashUpper = 19260817

Standard_GUID.__hash__ = lambda x: x.Hash(_GUIDHashUpper)

Standard_GUID.__repr__ = Standard_GUID.__str__ = lambda x: x.ShallowDumpToString()
RP_GUID = Standard_GUID
