from RedPanda.Core.data import RP_GUID

ShapeRefGUID  = RP_GUID ("5b896afe-3adf-11d4-b9b7-0060b0ee281b")
Sym_IdAttr_GUID = RP_GUID ("22D22E59-ABCA-11d4-8F1A-0060B0EE18E8")


AssemblyGUID  = RP_GUID ("5b896b00-3adf-11d4-b9b7-0060b0ee281b")
IDcolGUID     = RP_GUID ("efd212e4-6dfd-11d4-b9c8-0060b0ee281b")
IDcolSurfGUID = RP_GUID ("efd212e5-6dfd-11d4-b9c8-0060b0ee281b")
IDcolCurvGUID = RP_GUID ("efd212e6-6dfd-11d4-b9c8-0060b0ee281b")

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

class GuidLookup(object):
    
    def __init__(self, key_in, key_value) -> None:
        self.dict = {}
        for key, value in zip(key_in, key_value):
            self.dict[key] = value

    def __getitem__(self, item) -> type:
        return self.dict[item]

