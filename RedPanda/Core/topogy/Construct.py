#!/usr/bin/env python

##Copyright 2011-2015 Jelle Feringa (jelleferinga@gmail.com)
##
##This file is part of pythonOCC.
##
##pythonOCC is free software: you can redistribute it and/or modify
##it under the terms of the GNU Lesser General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##pythonOCC is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU Lesser General Public License for more details.
##
##You should have received a copy of the GNU Lesser General Public License
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

"""
This modules makes the construction of geometry a little easier
"""

from functools import wraps
import warnings

from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.BRepOffset import BRepOffset_Skin
from OCC.Core.Geom import Geom_TrimmedCurve
from OCC.Core.GeomConvert import GeomConvert_ApproxCurve
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Transform,
    BRepBuilderAPI_Sewing,
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeSolid,
    BRepBuilderAPI_MakeShell,
    BRepBuilderAPI_MakeEdge2d,
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_FindPlane,
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeEvolved
from OCC.Core.GeomAbs import (
    GeomAbs_Arc,
    GeomAbs_C2,
    GeomAbs_C0,
    GeomAbs_Tangent,
    GeomAbs_Intersection,
    GeomAbs_G1,
    GeomAbs_G2,
    GeomAbs_C1,
)
from OCC.Core.TopAbs import TopAbs_REVERSED
from OCC.Core.TopoDS import (
    TopoDS_Wire,
    TopoDS_Solid,
    TopoDS_Vertex,
    TopoDS_Shape,
    TopoDS_Builder,
    TopoDS_Compound,
)
from OCC.Core.TColgp import TColgp_SequenceOfVec, TColgp_HArray1OfPnt
from OCC.Core.gp import (

    gp_Circ,
    gp_Pln,
)

from .Common import (
    TOLERANCE,
    assert_isdone,
    to_tcol_,
    to_adaptor_3d,
    vertex2pnt,
    smooth_pnts,
    points_to_bspline,
    project_point_on_curve,
)
from .types_lut import ShapeToTopology
from .Topology import Topo
from ..Euclid import (
    RP_Vec,
    RP_Pnt,
    RP_Dir,
    RP_Trsf,
    RP_Ax1,
    RP_Quaternion,
)

# ===========================================================================
# ---TOPOLOGY---
# ===========================================================================


@wraps(BRepBuilderAPI_MakeSolid)
def make_solid(*args):
    sld = BRepBuilderAPI_MakeSolid(*args)
    with assert_isdone(sld, "failed to produce solid"):
        result = sld.Solid()
        return result


@wraps(BRepBuilderAPI_MakeShell)
def make_shell(*args):
    shell = BRepBuilderAPI_MakeShell(*args)
    st = ShapeToTopology()
    with assert_isdone(shell, "failed to produce shell"):
        result = shell.Shell()
        return st(result)


@wraps(BRepBuilderAPI_MakeFace)
def make_face(*args):
    face = BRepBuilderAPI_MakeFace(*args)
    with assert_isdone(face, "failed to produce face"):
        result = face.Face()
        return result


@wraps(BRepBuilderAPI_MakeEdge2d)
def make_edge2d(*args):
    edge = BRepBuilderAPI_MakeEdge2d(*args)
    with assert_isdone(edge, "failed to produce edge"):
        result = edge.Edge()
    return result


@wraps(BRepBuilderAPI_MakeEdge)
def make_edge(*args):
    edge = BRepBuilderAPI_MakeEdge(*args)
    with assert_isdone(edge, "failed to produce edge"):
        result = edge.Edge()
        return result


@wraps(BRepBuilderAPI_MakeVertex)
def make_vertex(*args):
    vert = BRepBuilderAPI_MakeVertex(*args)
    with assert_isdone(vert, "failed to produce vertex"):
        result = vert.Vertex()
        return result


@wraps(BRepBuilderAPI_MakeWire)
def make_wire(*args):
    # if we get an iterable, than add all edges to wire builder
    if isinstance(args[0], list) or isinstance(args[0], tuple):
        wire = BRepBuilderAPI_MakeWire()
        for i in args[0]:
            wire.Add(i)
        wire.Build()
        return wire.Wire()

    wire = BRepBuilderAPI_MakeWire(*args)
    wire.Build()
    with assert_isdone(wire, "failed to produce wire"):
        result = wire.Wire()
        return result


@wraps(BRepBuilderAPI_MakePolygon)
def make_polygon(args, closed=False):
    poly = BRepBuilderAPI_MakePolygon()
    for pt in args:
        # support nested lists
        if isinstance(pt, list) or isinstance(pt, tuple):
            for i in pt:
                poly.Add(i)
        else:
            poly.Add(pt)
    if closed:
        poly.Close()
    poly.Build()

    with assert_isdone(poly, "failed to produce wire"):
        result = poly.Wire()
        return result


@wraps(BRepBuilderAPI_MakePolygon)
def make_closed_polygon(*args):
    poly = BRepBuilderAPI_MakePolygon()
    for pt in args:
        if isinstance(pt, list) or isinstance(pt, tuple):
            for i in pt:
                poly.Add(i)
        else:
            poly.Add(pt)
    poly.Build()
    poly.Close()
    with assert_isdone(poly, "failed to produce wire"):
        result = poly.Wire()
        return result

