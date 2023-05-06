from uuid import uuid5, NAMESPACE_DNS
from RedPanda.Core.data import RP_GUID

AssemblyGUID  = RP_GUID ("5b896b00-3adf-11d4-b9b7-0060b0ee281b")
IDcolGUID     = RP_GUID ("efd212e4-6dfd-11d4-b9c8-0060b0ee281b")
IDcolSurfGUID = RP_GUID ("efd212e5-6dfd-11d4-b9c8-0060b0ee281b")
IDcolCurvGUID = RP_GUID ("efd212e6-6dfd-11d4-b9c8-0060b0ee281b")


Sym_IdAttr_GUID = RP_GUID ("22D22E59-ABCA-11d4-8F1A-0060B0EE18E8")
ShapeRefGUID  = RP_GUID ("5b896afe-3adf-11d4-b9b7-0060b0ee281b")
Attr_State_guid = RP_GUID ("5b896aff-3adf-11d4-b9b7-0060b0ee281b")
Attr_Exist_GUID = RP_GUID ("12052000-3adf-11d4-b9b7-0060b0ee281b")

Attr_Entry_GUID = RP_GUID ("22D22E64-ABCA-11d4-8F1A-0060B0EE18E8")
Attr_StateMes_GUID = RP_GUID ("22D22E65-ABCA-11d4-8F1A-0060B0EE18E8")


Sym_RealDriver_GUID = RP_GUID ("22D22E51-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_IntDriver_GUID = RP_GUID ("22D22E57-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_IdDriver_GUID = RP_GUID ("22D22E60-ABCA-11d4-8F1A-0060B0EE18E8")

Sym_BoxDriver_GUID = RP_GUID ("22D22E50-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_PntDriver_GUID = RP_GUID ("22D22E52-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_TransformDriver_GUID = RP_GUID ("22D22E53-ABCA-11d4-8F1A-0060B0EE18E8")


Sym_ShapeRefDriver_GUID = RP_GUID ("22D22E54-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_CutDriver_GUID = RP_GUID ("22D22E55-ABCA-11d4-8F1A-0060B0EE18E8")

Sym_ArrayDriver_GUID = RP_GUID ("22D22E56-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_BezierDriver_GUID = RP_GUID ("22D22E61-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_TransShapeDriver_GUID = RP_GUID ("22D22E62-ABCA-11d4-8F1A-0060B0EE18E8")

Sym_Pnt2dDriver_GUID = RP_GUID("22D22E70-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_Ax2dDriver_GUID = RP_GUID("22D22E71-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_Ax3dDriver_GUID = RP_GUID("22D22E72-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_EllipseDriver_GUID = RP_GUID("22D22E73-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_CurSrvDriver_GUID = RP_GUID("22D22E74-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_Ax3Driver_GUID = RP_GUID("22D22E75-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_RefSubDriver_GUID = RP_GUID("22D22E76-ABCA-11d4-8F1A-0060B0EE18E8")

Sym_Build3dEdgeDriver_GUID = RP_GUID("22D22E77-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_Elps2dDriver_GUID = RP_GUID("22D22E78-ABCA-11d4-8F1A-0060B0EE18E8")
Sym_TrimmedCurve2d_GUID = RP_GUID(str(uuid5(NAMESPACE_DNS, 'TrimmedCurve')))



class GuidLookup(object):
    def __init__(self, key_in, key_value) -> None:
        self.dict = {}
        for key, value in zip(key_in, key_value):
            self.dict[key] = value

    def __getitem__(self, item) -> type:
        return self.dict[item]

    def Add(self, key, value)->None:
        self.dict[key] = value
