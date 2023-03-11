from OCC.Core.Standard import *
from OCC.Core.TCollection import TCollection_ExtendedString
# geom struct
from OCC.Core.gp import *
from OCC.Core.Geom import *
from OCC.Core.Geom2d import *

# topods struct
from OCC.Core.TopAbs import *
from OCC.Core.TopoDS import *
from OCC.Core.TopLoc import *

# AIS
from OCC.Core.AIS import AIS_InteractiveContext

# topods build
from OCC.Core.BRepBuilderAPI import *
from OCC.Core.BRepPrimAPI import *
from OCC.Core.BRepOffsetAPI import *
from OCC.Core.BRepFilletAPI import *
from OCC.Core.BRepAlgoAPI import *
from OCC.Core.BRepFeat import *
from OCC.Core.BRepTools import *

# exception
from OCC.Core.IFSelect import *

# application framework
# LCAF
from OCC.Core.TDF import *
from OCC.Core.TDocStd import *
from OCC.Core.TNaming import *
from OCC.Core.TPrsStd import *
from OCC.Core.TDataStd import *
from OCC.Core.TFunction import *

#CAF
from OCC.Core.TDataXtd import TDataXtd_Point

#XCAF
from OCC.Core.XCAFDoc import XCAFDoc_Location

"""
NCollection_DataMap<TheKeyType, TheItemType, Hasher>
=> typedef NCollection_DataMap<Standard_GUID, Handle<TFunction_Driver>, Standard_GUID > 
           TFunction_DataMapOfGUIDDriver

different with:
NCollection_Map<TheKeyMap, Hasher>
=> typedef NCollection_Map< TDF_Label, TDF_LabelMapHasher > 	TDF_LabelMap
"""

# TOBJ
from OCC.Core.TObj import *

# my
from utils.Sym_Singleton import Singleton
from utils.Sym_Attribute import (
    FindAttribute,
    Assembly,
    ShapeRef,
    IDcolCurv,
    IDcolSurf,
    IDcol
)

# fix
TDF_Label.FindAttribute = FindAttribute

GUIDHashUpper = 19260817
Standard_GUID.__hash__ = lambda x: Standard_GUID.Hash(x, GUIDHashUpper)
Standard_GUID.__str__ = Standard_GUID.ShallowDumpToString

LabelHashUpper = 19260817        
TDF_Label.__hash__ = lambda self: TDF_LabelMapHasher.HashCode(self, LabelHashUpper)

def TDocStd_Application_AddDocument(self:TDocStd_Application, doc):
    self.InitDocument(doc)
    super(TDocStd_Application, self).Open(doc)
TDocStd_Application.AddDocument = TDocStd_Application_AddDocument


def ShallowCopy(dest, src):
    dest.__class__ = src.__class__ # 
    dest.__dict__ = src.__dict__ 
    # __annotations__
    # __doc__
    # __module__


# Driver Table
class myTFunction_DriverTable(Standard_Transient, Singleton):
    _myDrivers:dict = dict()
    # _myThreadDrivers = TFunction_HArray1OfDataMapOfGUIDDriver()
    def __init__(self, *args) -> None:
        return 
        # super().__init__(*args)

    def Get()->TFunction_DriverTable:
        if not hasattr(TFunction_DriverTable, '_instance'):
            TFunction_DriverTable()

        return TFunction_DriverTable._instance

    def AddDriver(self, guid:Standard_GUID, 
                  driver:TFunction_Driver)->bool:

        self._myDrivers[guid] = driver
        return self.HasDriver(guid)

    def HasDriver(self, guid:Standard_GUID)->bool:
        
        return guid in self._myDrivers.keys()

    def FindDriver(self, guid:Standard_GUID, 
                   driver:TFunction_Driver)->bool:

        if self.HasDriver(guid):
            ShallowCopy(driver, self._myDrivers.get(guid))
            return True
        print("not found, ", guid)
        return False

    def __str__(self):
        for guid, driver in self._myDrivers.items():
            print(guid.ShallowDumpToString(), end='\t')
            es = TCollection_ExtendedString()
            if tdf_ProgIDFromGUID(guid, es):
                print(es, end="")
            print()

    def RemoveDriver(self, guid:Standard_GUID):
        self._myDrivers.pop(guid)

    def Clear(self):
        self._myDrivers.clear()

TFunction_DriverTable = myTFunction_DriverTable


# TFunction_Logbook
def SetUnTouched(self:TFunction_Logbook, theLabel:TDF_Label):
    map_Lab:TDF_LabelMap = self.GetTouched()
    map_Lab.remove(theLabel)

def SetUnImpacted(self:TFunction_Logbook, theLabel:TDF_Label):
    map_Lab:TDF_LabelMap = self.GetImpacted()
    map_Lab.remove(theLabel)

def SetUnValid(self:TFunction_Logbook, theLabel:TDF_Label):
    map_Lab:TDF_LabelMap = self.GetValid()
    map_Lab.remove(theLabel)

TFunction_Logbook.SetUnValid = SetUnValid
TFunction_Logbook.SetUnTouched = SetUnTouched
TFunction_Logbook.SetUnImpacted = SetUnImpacted

# data translate
def FromText(theType:type, text:str):
    if theType == TDataStd_Real:
        return float(text)
    elif theType == TDataStd_Integer:
        return int(text)
    elif theType == TCollection_ExtendedString:
        return TCollection_ExtendedString(text)
    else:
        return text

