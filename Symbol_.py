from utils.OCCUtils import (
    TDF_Data,
    TDF_Label,
    gp_Trsf,
    TopLoc_Location,
    gp_Pnt,
    TDataStd_Name,
    TCollection_ExtendedString,
    TDataStd_TreeNode,
    TDF_Reference,
    Sym_ShapeRef,
    TDF_Tool,
    TCollection_AsciiString,
)

from OCC.Core.TDataStd import (
    TDataStd_Integer
)
from utils.Driver.Sym_ShapeDriver import (
    Sym_BoxDriver
)
from utils.Sym_ParamBuilder import (
    Sym_NewBuilder
)
from utils.Sym_Application import Sym_Application
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Extend.ShapeFactory import make_vertex
from utils.OCCUtils import (
    TDocStd_Document,
    TColgp_Array1OfPnt
)
from OCC.Core.XmlDrivers import xmldrivers_DefineFormat
def Trsf()->    TopLoc_Location:
    tr = gp_Trsf()
    tr.SetTranslation(gp_Pnt(1, 0, 0), gp_Pnt(0, 0, 1))
    loc = TopLoc_Location(tr)
    print(loc.DumpJsonToString())
    return loc

app = Sym_Application()
xmldrivers_DefineFormat(app)
doc = TDocStd_Document(TCollection_ExtendedString('XmlOcaf'))
app.AddDocument(doc)
df = doc.Main()

root = df.Root()
TDataStd_Name.Set(root, TCollection_ExtendedString("Root"))
node1 = root.FindChild(1)
TDataStd_Name.Set(node1, TCollection_ExtendedString("Node1"))
node2 = root.FindChild(2)
TDataStd_Name.Set(node2, TCollection_ExtendedString("Node2"))
Sym_ShapeRef.Set(node1, node2)

node3 = root.FindChild(3)
TDataStd_Name.Set(node3, TCollection_ExtendedString("Node3"))
Sym_ShapeRef.Set(node2, node1)
Sym_ShapeRef.Set(node3, node1)

def GetChilde():
    value = Sym_ShapeRef()
    if node2.FindAttribute(Sym_ShapeRef.GetID(), value):
        label = value.Get()
        print("get", label.GetLabelName())

    a = Sym_ShapeRef.Set(node1)
    for i in a:
        print("Get@:", i.GetLabelName())


def Entry():
    str = TCollection_AsciiString()
    TDF_Tool.Entry(node2, str)

    print(str.PrintToString())
    label = TDF_Label()
    TDF_Tool.Label(node2.Data(), str, label, False)
    print(label.GetLabelName())

def GetPoint():
    from OCC.Core.TNaming import (
        TNaming_Builder,
        TNaming_NamedShape
    )
    pnt = gp_Pnt(0, 0, 1)
    shape = make_vertex(pnt)
    
    builder = TNaming_Builder(root.FindChild(1))
    builder.Generated(shape)


def GetPoint2():
    from OCC.Core.TNaming import (
        TNaming_Builder,
        TNaming_NamedShape
    )
    pnt = gp_Pnt(0, 0, 2)
    shape = make_vertex(pnt)
    
    builder = TNaming_Builder(root.FindChild(1))
    builder.Generated(shape)

def GetShape():
    from utils.OCCUtils import TNaming_NamedShape
    a = TNaming_NamedShape
    NS = a()
    if not root.FindChild(1).FindAttribute(NS.GetID(), NS):
        print("not found")
        return 1

    value = NS.Get()
    if value is None:
        print("NS is NOne")
        return 1
    print(type(value))
    return value

def Param():
    from utils.Driver.Sym_DataDriver import Sym_ArrayDriver
    # param = Sym_NewBuilder(Sym_BoxDriver())
    param = Sym_NewBuilder(Sym_ArrayDriver())

if __name__ == "__main__":
    Param()
