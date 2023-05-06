import os,sys
sys.path.append(os.getcwd()) 


'''
Prs3d_Presentation might be filled in by the following primitives:

Triangles
    - Graphic3d_ArrayOfTriangles
    - Graphic3d_ArrayOfTriangleFans
    - Graphic3d_ArrayOfTriangleStrips
Lines
    - Graphic3d_ArrayOfSegments
    - Graphic3d_ArrayOfPolylines
Points or Markers
    - Graphic3d_ArrayOfPoints

这三组基元是图形硬件能够渲染的,因此可以以顶点缓冲对象(VBO)的形式
直接传输到低级图形库。
每个基元数组包括一个顶点属性数组（位置、法线、纹理坐标、顶点颜色等）
和可选的索引数组。后者可以避免重复属性数组中连接元素（三角形、折线）之间共享的顶点。

'''

'''
Graphic3d_ArrayOfPrimitives and it's subclasses provide a convenient interface 
for filling in primitive arrays:
- Constructor takes a number of vertices, number of edges (indices) and 
a bitmask of optional vertex attributes.
- Graphic3d_ArrayOfPrimitives::AddVertex() appends a vertex with specified attributes 
to the end of the array (within the range specified at construction time).
- Graphic3d_ArrayOfPrimitives::AddEdges() appends indices, starting with 1. 
Each line segment is defined by two consequential edges, each triangle is defined 
by three consequential edges.

'''
from OCC.Core.gp import gp_Pnt, gp_Trsf, gp_Ax3, gp_DZ, gp_DX, gp_XOY
from OCC.Core.TCollection import TCollection_AsciiString


def test_primitive():
    from OCC.Core.StdPrs import StdPrs_ShadedShape, StdPrs_WFShape
    from OCC.Core.Prs3d import (
        Prs3d_Presentation, Prs3d_ToolQuadric,
        Prs3d_ToolCylinder
    )
    from OCC.Core.TopoDS import TopoDS_Shape
    from OCC.Display.SimpleGui import init_display
    from OCC.Core.Graphic3d import (
        Graphic3d_Structure,
        Graphic3d_ArrayOfSegments,
        Graphic3d_ArrayFlags_None,
        Graphic3d_Text,
        Graphic3d_Aspects,
        Graphic3d_TypeOfShadingModel_Unlit,
        Graphic3d_AspectText3d
    )
    from OCC.Core.Quantity import (
        Quantity_Color,
        Quantity_NOC_ORANGE,
    )
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder

    anAspects = Graphic3d_Aspects()
    anAspects.SetShadingModel(Graphic3d_TypeOfShadingModel_Unlit)
    anAspects.SetColor(Quantity_Color(Quantity_NOC_ORANGE))

    display, start_display, *_ = init_display()
    thePrs = Graphic3d_Structure(display._struc_mgr)

    aRadius = 100
    aHeight = 100
    aShape:TopoDS_Shape  = BRepPrimAPI_MakeCylinder (aRadius, aHeight).Shape()
    myDrawer = display.default_drawer

    StdPrs_ShadedShape.Add (thePrs, aShape, myDrawer)
    StdPrs_WFShape.Add (thePrs, aShape, myDrawer) # add wireframe
    # aTris = Prs3d_ToolCylinder.Create(aRadius, aRadius, aHeight, 10, 10, gp_Trsf())

    aSegs = Graphic3d_ArrayOfSegments(4, 4*2,
                                        Graphic3d_ArrayFlags_None)
    aSegs.AddVertex(gp_Pnt(0, -aRadius, 0))
    aSegs.AddVertex(gp_Pnt(0, -aRadius, aHeight))
    aSegs.AddVertex(gp_Pnt(0,  aRadius, aHeight))
    aSegs.AddVertex(gp_Pnt(0,  aRadius, 0))
    aSegs.AddEdges(1, 2)
    aSegs.AddEdges(2, 3)
    aSegs.AddEdges(3, 4)
    aSegs.AddEdges(4, 1)

    text = Graphic3d_Text(14)
    text.SetText('Hello word.')

    # Create a new Graphic3d_Group using Prs3d_Presentation::NewGroup();
    aGroupSegs = thePrs.NewGroup()
    # Specify presentation aspects using Graphic3d_Group::SetGroupPrimitivesAspect()
    aGroupSegs.SetPrimitivesAspect(anAspects)
    # Create and add an array of primitives using Graphic3d_Group::AddPrimitiveArray().
    aGroupSegs.AddPrimitiveArray(aSegs)
    
    aGroupSegs.AddText(text)
    thePrs.Display()
    # thePrs.Clear()
    start_display()

'''
Graphic3d_Aspects is a class defining display properties of a primitive array 
(Graphic3d_Group::SetGroupPrimitivesAspect())
- material, shading model, color, texture maps, blending mode, line width and others.

'''

def test_toolCylinder():
    from OCC.Core.StdPrs import StdPrs_ShadedShape, StdPrs_WFShape
    from OCC.Core.Prs3d import (
        Prs3d_Presentation, Prs3d_ToolQuadric,
        Prs3d_ToolCylinder
    )
    from OCC.Core.TopoDS import TopoDS_Shape
    from OCC.Display.SimpleGui import init_display
    from OCC.Core.Graphic3d import (
        Graphic3d_Structure,
        Graphic3d_Group,
        Graphic3d_ArrayOfSegments,
        Graphic3d_ArrayFlags_None,
        Graphic3d_Text,
        Graphic3d_Aspects,
        Graphic3d_TypeOfShadingModel_Unlit,
        Graphic3d_AspectText3d
    )
    from OCC.Core.Quantity import (
        Quantity_Color,
        Quantity_NOC_ORANGE,
    )
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder

    anAspects = Graphic3d_Aspects()
    anAspects.SetShadingModel(Graphic3d_TypeOfShadingModel_Unlit)
    anAspects.SetColor(Quantity_Color(Quantity_NOC_ORANGE))

    display, start_display, *_ = init_display()
    thePrs = Graphic3d_Structure(display._struc_mgr)

    aRadius = 100
    aHeight = 100

    aTris = Prs3d_ToolCylinder.Create(aRadius, aRadius, aHeight, 10, 10, gp_Trsf())

    aSegs = Graphic3d_ArrayOfSegments(4, 4*2,
                                        Graphic3d_ArrayFlags_None)
    aSegs.AddVertex(gp_Pnt(0, -aRadius, 0))
    aSegs.AddVertex(gp_Pnt(0, -aRadius, aHeight))
    aSegs.AddVertex(gp_Pnt(0,  aRadius, aHeight))
    aSegs.AddVertex(gp_Pnt(0,  aRadius, 0))
    aSegs.AddEdges(1, 2)
    aSegs.AddEdges(2, 3)
    aSegs.AddEdges(3, 4)
    aSegs.AddEdges(4, 1)

    aGroupTris:Graphic3d_Group = thePrs.NewGroup()
    aGroupTris.SetPrimitivesAspect(anAspects)
    aGroupTris.AddPrimitiveArray(aTris)
    aGroupTris.AddPrimitiveArray(aSegs)

    text = Graphic3d_Text(14)
    text.SetText('Hello word.')
    
    aGroupTris.AddText(text)
    thePrs.Display()
    # thePrs.Clear()
    start_display()

def test_tooldisk():
    from OCC.Core.StdPrs import StdPrs_ShadedShape, StdPrs_WFShape
    from OCC.Core.Prs3d import (
        Prs3d_Presentation, Prs3d_ToolQuadric,
        Prs3d_ToolCylinder, Prs3d_ToolDisk
    )
    from OCC.Core.TopoDS import TopoDS_Shape
    from OCC.Display.SimpleGui import init_display
    from OCC.Core.Graphic3d import (
        Graphic3d_Structure,
        Graphic3d_Group,
        Graphic3d_ArrayOfSegments,
        Graphic3d_ArrayFlags_None,
        Graphic3d_Text,
        Graphic3d_Aspects,
        Graphic3d_TypeOfShadingModel_Unlit,
        Graphic3d_AspectText3d,
        Graphic3d_ArrayOfTriangles,
        Graphic3d_ArrayFlags_VertexNormal
    )
    from OCC.Core.Quantity import (
        Quantity_Color,
        Quantity_NOC_ORANGE,
    )
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder

    display, start_display, *_ = init_display()

    anAspects = Graphic3d_Aspects()
    anAspects.SetShadingModel(Graphic3d_TypeOfShadingModel_Unlit)
    anAspects.SetColor(Quantity_Color(Quantity_NOC_ORANGE))

    thePrs = Graphic3d_Structure(display._struc_mgr)

    aRadius = 100
    aHeight = 100

    aCyl = Prs3d_ToolCylinder(aRadius, aRadius, aHeight, 25, 1)
    aDisk = Prs3d_ToolDisk(0.0, aRadius, 25, 1)
    aTris = Graphic3d_ArrayOfTriangles(aCyl.VerticesNb()+2*aDisk.VerticesNb(),
                                       3*(aCyl.TrianglesNb()+2*aDisk.TrianglesNb()),
                                       Graphic3d_ArrayFlags_VertexNormal)
    aCyl .FillArray(aTris, gp_Trsf())
    aDisk.FillArray(aTris, gp_Trsf())

    aDisk2Trsf = gp_Trsf()
    aDisk2Trsf.SetTransformation(
                gp_Ax3(gp_Pnt(0, 0, aHeight), -gp_DZ(), gp_DX()), 
                            gp_Ax3()
                        )
    aDisk.FillArray(aTris, aDisk2Trsf)

    aSegs = Graphic3d_ArrayOfSegments(4, 4*2,
                                        Graphic3d_ArrayFlags_None)
    aSegs.AddVertex(gp_Pnt(0, -aRadius, 0))
    aSegs.AddVertex(gp_Pnt(0, -aRadius, aHeight))
    aSegs.AddVertex(gp_Pnt(0,  aRadius, aHeight))
    aSegs.AddVertex(gp_Pnt(0,  aRadius, 0))
    aSegs.AddEdges(1, 2)
    aSegs.AddEdges(2, 3)
    aSegs.AddEdges(3, 4)
    aSegs.AddEdges(4, 1)

    text = Graphic3d_Text(14)
    text.SetText('Hello word.')

    aGroupTris:Graphic3d_Group = thePrs.NewGroup()
    aGroupTris.SetPrimitivesAspect(anAspects)
    aGroupTris.AddPrimitiveArray(aTris)

    an2Aspects = Graphic3d_Aspects()
    an2Aspects.SetColor(Quantity_Color(1))
    # textAspects = Graphic3d_AspectText3d()
    # textAspects.SetColor(Quantity_Color(0))

    aGroupText = thePrs.NewGroup()
    aGroupText.SetPrimitivesAspect(an2Aspects)
    aGroupText.AddPrimitiveArray(aSegs)
    aGroupText.AddText(text)
    

    thePrs.Display()
    # thePrs.Clear()
    start_display()



if __name__ == '__main__':
    test_tooldisk()
    
