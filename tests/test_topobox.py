import os,sys                                     
sys.path.append(os.getcwd()) 


from OCC.Core.TDF import (
    TDF_Data,
    TDF_Label,
)

from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.TNaming import (
    TNaming_Builder, 
    TNaming_NamedShape, 
    TNaming_Selector,
)
from RedPanda.RPAF.RD_Label import Label

from OCC.Display.SimpleGui import init_display

def case3():
    data = TDF_Data()
    aLabel = data.Root()
    
    box = BRepPrimAPI_MakeBox(10, 20, 30)

    createIfNotExist = True
    myBoxLabel = aLabel.FindChild(1, createIfNotExist)
    topLabel = myBoxLabel.FindChild(1, createIfNotExist)
    botLabel = myBoxLabel.FindChild(2, createIfNotExist)
    rigLabel = myBoxLabel.FindChild(3, createIfNotExist)
    lefLabel = myBoxLabel.FindChild(4, createIfNotExist)
    froLabel = myBoxLabel.FindChild(5, createIfNotExist)
    bacLabel = myBoxLabel.FindChild(6, createIfNotExist)

    myBoxBuilder = TNaming_Builder(myBoxLabel)
    myBoxBuilder.Generated(box.Shape())

    builder = TNaming_Builder(topLabel)
    builder.Generated(box.TopFace())
    
    builder = TNaming_Builder(botLabel)
    builder.Generated(box.BottomFaceFace())
    
    builder = TNaming_Builder(rigLabel)
    builder.Generated(box.RightFace())

    builder = TNaming_Builder(lefLabel)
    builder.Generated(box.LeftFace())

    builder = TNaming_Builder(froLabel)
    builder.Generated(box.FrontFace())

    builder = TNaming_Builder(bacLabel)
    builder.Generated(box.BackFace())

    cut_loc = gp_Pnt(7, 5, 30)
    cut_dir = gp_Dir(0, 0, -1)
    cut_ax2 = gp_Ax2(cut_loc, cut_dir)
    box = BRepPrimAPI_MakeBox(cut_ax2, 5, 5, 5)

    cutBoxLabel = aLabel.FindChild(2, createIfNotExist)
    topLabel = cutBoxLabel.FindChild(1, createIfNotExist)
    botLabel = cutBoxLabel.FindChild(2, createIfNotExist)
    rigLabel = cutBoxLabel.FindChild(3, createIfNotExist)
    lefLabel = cutBoxLabel.FindChild(4, createIfNotExist)
    froLabel = cutBoxLabel.FindChild(5, createIfNotExist)
    bacLabel = cutBoxLabel.FindChild(6, createIfNotExist)

    myBoxBuilder = TNaming_Builder(cutBoxLabel)
    myBoxBuilder.Generated(box.Shape())

    builder = TNaming_Builder(topLabel)
    builder.Generated(box.TopFace())
    
    builder = TNaming_Builder(botLabel)
    builder.Generated(box.BottomFaceFace())
    
    builder = TNaming_Builder(rigLabel)
    builder.Generated(box.RightFace())

    builder = TNaming_Builder(lefLabel)
    builder.Generated(box.LeftFace())

    builder = TNaming_Builder(froLabel)
    builder.Generated(box.FrontFace())

    builder = TNaming_Builder(bacLabel)
    builder.Generated(box.BackFace())

    # box 3
    myBoxCutLabel:Label = aLabel.FindChild(3, createIfNotExist)
    boxRecovered = myBoxLabel.GetAttrValue(TNaming_NamedShape.GetID())
    resultCutLabel = myBoxCutLabel.FindChild(1, createIfNotExist)

    
    # 4
    modifiedFacesLabel      = myBoxCutLabel.FindChild(2, createIfNotExist)
    deletedFacesLabel       = myBoxCutLabel.FindChild(3, createIfNotExist)
    intersectingFacesLabel  = myBoxCutLabel.FindChild(4, createIfNotExist)
    newFacesLabel           = myBoxCutLabel.FindChild(5, createIfNotExist)

    cutBoxRecovered = cutBoxLabel.GetAttrValue(TNaming_NamedShape.GetID())
    myBoxCutSel = TNaming_Selector(resultCutLabel)
    myBoxCutSel.Select(cutBoxRecovered, cutBoxRecovered)

    

def case1_filletAndSelector():
    from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
    from OCC.Extend.TopologyUtils import TopologyExplorer
    from OCC.Core.TDF import TDF_TagSource, TDF_LabelMap
    from OCC.Core.TopTools import TopTools_ListIteratorOfListOfShape
    df = TDF_Data()
    root = df.Root()

    boxLabel = root.NewChild()
    box = BRepPrimAPI_MakeBox(10, 10, 15).Shape()
    builder = TNaming_Builder(boxLabel)
    builder.Generated(box)

    for face in TopologyExplorer(box).faces():
        aLabel = boxLabel.NewChild()
        builder = TNaming_Builder(aLabel)
        builder.Generated(face)

    
    selectLabel = root.NewChild()
    selector = TNaming_Selector(selectLabel)
    face = list(TopologyExplorer(box).faces())[0]
    selector.Select(list(TopologyExplorer(face).edges())[0], face)

    filletLabel = root.NewChild()
    fillet = BRepFilletAPI_MakeFillet(box)
    for edge in TopologyExplorer(box).edges():
        fillet.Add(1, edge)
    fillet.Build()
    filletBox = fillet.Shape()
    builder = TNaming_Builder(filletLabel)
    builder.Generated(filletBox)
    
    for face in TopologyExplorer(box).faces():
        face_li = fillet.Modified(face)
        it = TopTools_ListIteratorOfListOfShape(face_li)
        while it.More():
            aLabel = filletLabel.NewChild()
            builder = TNaming_Builder(aLabel)
            builder.Modify(face, it.Value())            

            it.Next()

    map = TDF_LabelMap()
    # selector.Solve(map)
    shape = selector.NamedShape().Get()

    display, start_display, *_ = init_display()
    display.DisplayShape(shape)
    display.DisplayShape(filletBox)
    start_display()

if __name__ == '__main__':
    case1_filletAndSelector()
