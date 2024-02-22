from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_Transform
)
from OCC.Core.TopoDS import TopoDS_Shape

from OCC.Core.TDocStd import (
    TDocStd_Document,
    TDocStd_Application
)
from OCC.Core.TDF import (
    TDF_LabelSequence,
    TDF_Label,
    TDF_Tool
)

from OCC.Core.TopoDS import TopoDS_Solid
from OCC.Core.TColStd import (
    TColStd_ListOfInteger
)

from OCC.Core.TopLoc import TopLoc_Location

from OCC.Core.TCollection import (
    TCollection_ExtendedString as String
)

from OCC.Core.XCAFDoc import (
    XCAFDoc_DocumentTool
)

from OCC.Core.STEPCAFControl import STEPCAFControl_Reader


from OCC.Core.IFSelect import (
    IFSelect_RetDone,
)
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.XmlDrivers import (
    xmldrivers
)
from OCC.Core.TDF import TDF_Data

from RedPanda.logger import Logger

default_color_id = 125

import os

def TDocStd_Application_AddDocument(self:TDocStd_Application, doc):
    self.InitDocument(doc)
    super(TDocStd_Application, self).Open(doc)


TDocStd_Application.AddDocument = TDocStd_Application_AddDocument


def OpenFile(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError("{} not found.".format(filename))

    app = TDocStd_Application()
    # create an handle to a document
    xmldrivers.DefineFormat(app)

    doc = TDocStd_Document(String("XmlOcaf"))
    app.AddDocument(doc)
    
    
    step_reader = STEPCAFControl_Reader()
    step_reader.SetColorMode(True)
    step_reader.SetLayerMode(True)
    step_reader.SetNameMode(True)
    step_reader.SetMatMode(True)
    step_reader.SetGDTMode(True)
    status = step_reader.ReadFile(filename)
    if status == IFSelect_RetDone:
        step_reader.Transfer(doc)
        # app.SaveAs(doc, String("sample.xml"))
    else:
        raise Exception("readError")
    return doc

def read_step_file_with_names_colors(doc:TDocStd_Document):
    """ 
    """
    # dict of out shape
    dict_display_shape = dict()

    # Get shape
    shape_tool = XCAFDoc_DocumentTool.ShapeTool(doc.Main())
    color_tool = XCAFDoc_DocumentTool.ColorTool(doc.Main())
    l_layers = XCAFDoc_DocumentTool.LayerTool(doc.Main())
    l_materials = XCAFDoc_DocumentTool.MaterialTool(doc.Main())

    DumpToString = shape_tool.DumpToString()
    # num = 0

    stack_location = []

    def _get_sub_list_shape(label):
        name = label.GetLabelName()
        shapeSequence = TDF_LabelSequence()
        componentSequence = TDF_LabelSequence()

        shape_tool.GetSubShapes(label, shapeSequence)
        shape_tool.GetComponents(label, componentSequence)

        def _referenceLabel_read(shape_tool: XCAFDoc_DocumentTool.ShapeTool, label:TDF_Label):
            label_reference = TDF_Label()
            shape_tool.GetReferredShape(label, label_reference)
            location = shape_tool.GetLocation(label)

            stack_location.append(location)
            _get_sub_list_shape(label_reference)
            stack_location.pop()

        def _setColor(label, shape:TopoDS_Shape):
            color =  Quantity_Color( default_color_id) # 地址拷贝, quantity 不能等于quantity
            color_set = False

            if (color_tool.GetInstanceColor(shape, 0, color)
             or color_tool.GetInstanceColor(shape, 1, color)
             or color_tool.GetInstanceColor(shape, 2, color)):
                color_tool.SetInstanceColor(shape, 0, color)
                color_tool.SetInstanceColor(shape, 1, color)
                color_tool.SetInstanceColor(shape, 2, color)
                color_set = True

            if not color_set:
                if (
                    color_tool.GetColor(label, 0, color)
                    or color_tool.GetColor(label, 1, color)
                    or color_tool.GetColor(label, 2, color)
                ):
                    color_tool.SetInstanceColor(shape, 0, color)
                    color_tool.SetInstanceColor(shape, 1, color)
                    color_tool.SetInstanceColor(shape, 2, color)

            return color

        # 是否为装配关系
        if shape_tool.IsAssembly(label):
            for i in range(componentSequence.Length()):
                alabel = componentSequence.Value(i+1)
                if shape_tool.IsReference(alabel):
                    _referenceLabel_read(shape_tool, alabel)

        elif shape_tool.IsSimpleShape(label):
            location = TopLoc_Location()
            for loc in stack_location:
                location = location.Multiplied(loc)

            # color = _setColor(label, shape)

            # shape_disp = BRepBuilderAPI_Transform(shape, location.Transformation()).Shape()
            # tagList = TColStd_ListOfInteger()
            # TDF_Tool.TagList(label, tagList)
            # dict_display_shape[shape_disp] = {"color": color,
            #                                   "tagList": tagList}
            shapeSequence.Append(label)
            for i in range(shapeSequence.Length()):
                label = shapeSequence.Value(i+1)
                shape = shape_tool.GetShape(label)

                shape_disp = BRepBuilderAPI_Transform(shape, location.Transformation()).Shape()
                if shape_disp not in dict_display_shape:
                    tagList = TColStd_ListOfInteger()
                    TDF_Tool.TagList(label, tagList)
                    color = _setColor(label, shape)
                    otherShape = TopoDS_Shape()
                    # if  isinstance(shape, TopoDS_Solid): # 排除非solid
                    #     n = color.Name(color.Red(), color.Green(), color.Blue())
                    #     print('T   shape color Name & RGB: ', color, n, color.Red(), color.Green(), color.Blue())

                    dict_display_shape[shape_disp] = {"color": color,
                                                    "tagList": tagList}

    def _get_shapes():
        sequence_label = TDF_LabelSequence()
        # print("Number of shapes at root :", sequence_label.Length())
        shape_tool.GetFreeShapes(sequence_label)
        for i in range(sequence_label.Length()):
            root_item = sequence_label.Value(i+1)
            _get_sub_list_shape(root_item)

    _get_shapes()
    # print(len(dict_display_shape))
    # print("num:", num)
    return dict_display_shape

