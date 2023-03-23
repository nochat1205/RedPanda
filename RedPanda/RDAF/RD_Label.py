
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

def FindAttribute(self, GUID:RP_GUID, attribute):
    it_attr = TDF_AttributeIterator(self)
    while it_attr.More():
        # TODO: may be all object associated TopoDS should use ShallowCopy 
        if it_attr.Value().ID() == GUID:
            if GUID in _topAttr_id:
                aType = Lookup_Attr[GUID]
                _AttrShallowCopy(attribute, 
                                        aType.DownCast(it_attr.Value() ) )
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
        return DataDriverTable.Get().FindDriver(id, aDriver)
    return None

def GetEntry(theLabel:TDF_Label):
    anEntry = RP_AsciiStr()
    TDF_Tool.Entry(theLabel, anEntry)

    return anEntry

def GetFunctionID(theLabel:TDF_Label):
    function = TFunction_Function()
    if theLabel.FindAttribute(TFunction_Function.GetID(), function):
        return function.GetDriverGUID()
    return None

def GetAttrValue(theLabel:TDF_Label, guid:RP_GUID):
    container = Lookup_Attr[guid]()
    if theLabel.FindAttribute(guid, container):
        return container.Get()

    Logger().warn(f'Entry:{theLabel.GetEntry()} get attr {guid} error')        
    return None

Label = TDF_Label
Label.__hash__ = __hash__
Label.FindAttribute = FindAttribute
Label.GetEntry = GetEntry
Label.GetFunctionID = GetFunctionID
Label.GetDriver = GetDriver
Label.GetAttrValue = GetAttrValue
