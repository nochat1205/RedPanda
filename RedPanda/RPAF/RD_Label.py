from __future__ import annotations
__all__ = ['Label']


from typing import Union

from OCC.Core.TDF import (
    TDF_Label,
    TDF_AttributeIterator,
    TDF_Tool,
    TDF_LabelMapHasher,
)

from RedPanda.Core.data import (
    RP_GUID,
    RP_AsciiStr
)
from .Attribute import (
    TNaming_NamedShape,
    XCAFDoc_Location,
    TFunction_Function,
    Lookup_Attr,
)
from RedPanda.logger import Logger
from RedPanda.RPAF.Document import Document

_topAttr_id = (
    TNaming_NamedShape.GetID(),
    XCAFDoc_Location.GetID()
)
_LabelHashUpper = 19260817

def __hash__(self) -> int:
    return TDF_LabelMapHasher.HashCode(self, _LabelHashUpper)

def _AttrShallowCopy(dest, src):
    dest.__class__ = src.__class__ # 
    dest.__dict__ = src.__dict__

from OCC.Core.TDataStd import TDataStd_Comment, TDataStd_Name

_inheritObject_id = (
    TDataStd_Comment.GetID(),
)

def FindAttribute(self, GUID:RP_GUID, attribute):
    it_attr = TDF_AttributeIterator(self)
    while it_attr.More():
        # TODO: may be all object associated TopoDS should use ShallowCopy 
        if it_attr.Value().ID() == GUID:
            if GUID in _topAttr_id or GUID in _inheritObject_id:
                aType = Lookup_Attr[GUID]
                _AttrShallowCopy(attribute, aType.DownCast(it_attr.Value() ) )
            else:
                attribute.Restore(it_attr.Value())
            return True 
        it_attr.Next()

    attribute = None
    return False

def GetDriver(self):

    from .DataDriver.BaseDriver import DataDriver
    from .DriverTable import DataDriverTable

    aDriver = DataDriver()
    id = self.GetFunctionID()
    if id:
        return DataDriverTable.Get().GetDriver(id)
    return None

def GetEntry(theLabel:TDF_Label):
    anEntry = RP_AsciiStr()
    TDF_Tool.Entry(theLabel, anEntry)

    return anEntry

def GetFunctionID(theLabel:TDF_Label):
    function = TFunction_Function()
    if theLabel.FindAttribute(TFunction_Function.GetID(), function):
        return function.GetDriverGUID()
    Logger().info(f'{theLabel.GetEntry()} not have function id')
    return None

from .Attribute import TDF_Attribute
def GetAttribute(theLabel:TDF_Label, guid:RP_GUID)->TDF_Attribute:
    container = Lookup_Attr[guid]()
    if container is None:
        Logger().warn(f"Lookup attr don't find {guid} ")        
        return None

    if theLabel.FindAttribute(guid, container):
        return container

    Logger().warning(f"{theLabel.GetEntry()} don't find  Attr {guid} ")        
    return None

def GetAttrValue(theLabel:TDF_Label, guid:RP_GUID):
    container = GetAttribute(theLabel, guid)
    if container:
        return container.Get()

    return None

def label_str(theLabel:TDF_Label):
    return theLabel.GetEntry()

def label_GetDataLabel(self:TDF_Label):
    while self.GetLabelName() == '':
        self = self.Father()
    return self

def label_argument(theLabel:TDF_Label, key:str):
    from .DataDriver.BaseDriver import DataDriver
    aDriver:DataDriver = theLabel.GetDriver()
    aLabel = aDriver.Arguments[key].Label(theLabel)
    return aLabel

def label_changeValue(theLabel:TDF_Label, value):
    from .DataDriver.BaseDriver import DataDriver
    aDriver:DataDriver = theLabel.GetDriver()
    aDriver.Change(theLabel, value)

Label = TDF_Label
Label.__hash__ = __hash__
Label.FindAttribute = FindAttribute
Label.GetEntry = GetEntry
Label.GetFunctionID = GetFunctionID
Label.GetDriver = GetDriver
Label.GetAttribute = GetAttribute
Label.GetAttrValue = GetAttrValue
Label.GetDataLabel = label_GetDataLabel
Label.Argument = label_argument
Label.ChangeValue = label_changeValue

Label.__str__ = label_str
Label.__repr__ = label_str
