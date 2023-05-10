#!/usr/bin/env python

##Copyright 2009-2019 Thomas Paviot (tpaviot@gmail.com)
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

import os
import sys

# from OCC.Display import OCCViewer
from OCC.Display.backend import get_qt_modules
from OCC.Core.AIS import AIS_KindOfInteractive_Shape,AIS_Shape, AIS_TextLabel
from RedPanda.Core.topogy.types_lut import topo_lut
from OCC.Core.StdSelect import StdSelect_BRepOwner

from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL
from PyQt5.QtCore import pyqtSlot


from OCC.Core.AIS import AIS_InteractiveContext, AIS_InteractiveObject
from OCC.Core.gp import gp_Pnt2d, gp_Ax3, gp_Pnt
from OCC.Core.Graphic3d import Graphic3d_Structure
from OCC.Core.TopoDS import TopoDS_Shape

from RedPanda.logger import Logger
from RedPanda.widgets.Ui_Viewer2d import Viewer2d
from RedPanda.RPAF.DataDriver import BareShapeDriver

class qtBaseViewer(QtWidgets.QWidget):
    """The base Qt Widget for an OCC viewer"""

    def __init__(self, parent=None):
        super(qtBaseViewer, self).__init__(parent)
        self._display = Viewer2d()
        self._inited = False

        # enable Mouse Tracking
        self.setMouseTracking(True)

        # Strong focus
        self.setFocusPolicy(QtCore.Qt.WheelFocus)

        self.setAttribute(QtCore.Qt.WA_NativeWindow)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)

        self.setAutoFillBackground(False)

    def resizeEvent(self, event):
        super(qtBaseViewer, self).resizeEvent(event)
        self._display.View.MustBeResized()

    def paintEngine(self):
        return None

from RedPanda.RPAF.GUID import RP_GUID
class qtViewer2d(qtBaseViewer):
    # emit signal when selection is changed
    # is a list of TopoDS_*
    sig_new_shape = QtCore.pyqtSignal(RP_GUID, dict)

    sig_topods_selected = QtCore.pyqtSignal(list)
    sig_point = QtCore.pyqtSignal((gp_Pnt, TopoDS_Shape, list))

    def __init__(self, *kargs):
        qtBaseViewer.__init__(self, *kargs)
        self.disp_ctx = None
        self.aLabel = None

        self.setObjectName("qt_viewer_3d")

        self.operatorManager = None
        self._drawbox = False
        self._zoom_area = False
        self._select_area = False
        self._inited = False
        self._leftisdown = False
        self._middleisdown = False
        self._rightisdown = False
        self._selection = None
        self._drawtext = True
        self._qApp = QtWidgets.QApplication.instance()
        self._key_map = {}
        self._current_cursor = "arrow"
        self._available_cursors = {}

        self._key_map = {
            ord("W"): self._display.SetModeWireFrame,
            ord("S"): self._display.SetModeShaded,
            ord("A"): self._display.EnableAntiAliasing,
            ord("B"): self._display.DisableAntiAliasing,
            ord("H"): self._display.SetModeHLR,
            ord("F"): self._display.FitAll,
            ord("G"): self._display.SetSelectionMode,
        }


        self.InitDriver()
        self.InitOperatorManager()

    @property
    def qApp(self):
        # reference to QApplication instance
        return self._qApp

    @qApp.setter
    def qApp(self, value):
        self._qApp = value

    def InitDriver(self):
        self._display.Create(window_handle=int(self.winId()), parent=self)
        # # background gradient
        # self._display.SetModeShaded()

        self._inited = True
        # dict mapping keys to functions
        self.createCursors()
        self._display.FocusOn(gp_Ax3())

        self.SetUVGrid(-10, 10, -10, 10)
        # me 
        # self._dict_Context = {"default": self._dict_Context}

    def createCursors(self):
        module_pth = os.path.abspath(os.path.dirname(__file__))
        icon_pth = os.path.join(module_pth, "icons")

        _CURSOR_PIX_ROT = QtGui.QPixmap(os.path.join(icon_pth, "cursor-rotate.png"))
        _CURSOR_PIX_PAN = QtGui.QPixmap(os.path.join(icon_pth, "cursor-pan.png"))
        _CURSOR_PIX_ZOOM = QtGui.QPixmap(os.path.join(icon_pth, "cursor-magnify.png"))
        _CURSOR_PIX_ZOOM_AREA = QtGui.QPixmap(
            os.path.join(icon_pth, "cursor-magnify-area.png")
        )

        self._available_cursors = {
            "arrow": QtGui.QCursor(QtCore.Qt.ArrowCursor),  # default
            "pan": QtGui.QCursor(_CURSOR_PIX_PAN),
            "rotate": QtGui.QCursor(_CURSOR_PIX_ROT),
            "zoom": QtGui.QCursor(_CURSOR_PIX_ZOOM),
            "zoom-area": QtGui.QCursor(_CURSOR_PIX_ZOOM_AREA),
        }

        self._current_cursor = "arrow"

    def keyPressEvent(self, event):
        super(qtViewer2d, self).keyPressEvent(event)
        code = event.key()
        if code in self._key_map:
            self._key_map[code]()
        elif code in range(256):
            Logger().info(
                'key: "%s"(code %i) not mapped to any function' % (chr(code), code)
            )
        else:
            Logger().info("key: code %i not mapped to any function" % code)

    @pyqtSlot()
    def Repaint(self):
        if self._inited:
            self._display.Repaint()

    def focusInEvent(self, event):
        self.Repaint()

    def focusOutEvent(self, event):
        self.Repaint()

    def paintEvent(self, event):

        self._display.Context.UpdateCurrentViewer()

        if self._drawbox:
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
            rect = QtCore.QRect(*self._drawbox)
            painter.drawRect(rect)


    # @property
    # def cursor(self):
    #     return self._current_cursor

    # @cursor.setter
    # def cursor(self, value):
    #     if not self._current_cursor == value:

    #         self._current_cursor = value
    #         cursor = self._available_cursors.get(value)

    #         if cursor:
    #             self.qApp.setOverrideCursor(cursor)
    #         else:
    #             self.qApp.restoreOverrideCursor()

    #  -- -- -- Prsentation -- -- --
    def clear(self):
        self._display.Context.RemoveAll(False)

    def ShowLabel(self, theLabel):
        if 'ctx' not in self.__dict__:
            self.ctx = None

        aDriver:BareShapeDriver = theLabel.GetDriver()
        if aDriver is None or not isinstance(aDriver, BareShapeDriver):
            return

        # TODO:
        self.clear()

        ctx = aDriver.Prs2d(theLabel)
        self.ctx = ctx

        for ais in ctx.values():
            self._display.Context.Display(ais, False)

        aDriver.UpdatePrs2d(theLabel, ctx)

        self._display.FitAll()
        self._display.Repaint()

    def UpdateLabel(self, theLabel):
        aDriver:BareShapeDriver = theLabel.GetDriver()
        if aDriver is None:
            return

        if not aDriver.UpdatePrs2d(theLabel, self.ctx):
            return

        # for ais in self.ctx.values():
        #     self._display.Context.Display(ais, False)

        self.SetUVGrid(*self.ctx.GetBound())
        self._display.Viewer.Update()
        self._display.Repaint()

    def TrihedronEnable(self, length):
        from OCC.Core.AIS import AIS_PlaneTrihedron
        from OCC.Core.Geom import Geom_Plane
        from OCC.Core.Quantity import Quantity_Color,Quantity_NOC_BLACK
        from OCC.Core.TCollection import TCollection_AsciiString

        if 'scale_structure_li' not in self.__dict__: # new scale
            self.scale_structure_li:list[Graphic3d_Structure] = list()

        if '_trihedron' not in self.__dict__: # new trihedron
            plane_ax3 = self._display.ViewPlane()
            pln = Geom_Plane(plane_ax3)
            
            ais_trihedron = AIS_PlaneTrihedron(pln)
            ais_trihedron.SetColor(Quantity_Color(Quantity_NOC_BLACK))

            self._trihedron:AIS_PlaneTrihedron = ais_trihedron

        # display scale
        for scale in self.scale_structure_li:
            scale:Graphic3d_Structure
            scale.Clear()
        self.scale_structure_li.clear()

        # aWindow = self.window()
        self._trihedron.SetLength(length)
        for num in range(1, 6): # (1, 5)
            pos = length * num / 6
            struct = self._display.DisplayMessage(gp_Pnt(0, pos, 0), f'{pos:.2f}')
            self.scale_structure_li.append(struct)

            struct = self._display.DisplayMessage(gp_Pnt(pos, 0, 0), f'{pos:.2f}')
            self.scale_structure_li.append(struct)

        self._display.Context.Display(self._trihedron, False)

    def GridEnable(self, u1=0, u2=0, v1=100, v2=100):
        from OCC.Core.Quantity import Quantity_NOC_WHITE, Quantity_Color
        from OCC.Core.Aspect import (
            Aspect_GT_Rectangular, Aspect_GDM_Lines, Aspect_GDM_Points,
            Aspect_TOM_RING1,
        )
        from OCC.Core.Graphic3d import Graphic3d_AspectMarker3d

        aViewer = self._display.Viewer

        aGridAspect = Graphic3d_AspectMarker3d(Aspect_TOM_RING1, Quantity_Color(Quantity_NOC_WHITE), 2.0)
        aViewer.SetGridEcho(aGridAspect)
        aWindow = self.window()
        # aWidth, aHeight = aWindow.width(), aWindow.height()
        aViewer.SetRectangularGridValues (-(u1+u2)/2, -(v1+v2)/2, 1, 1, 0)
        aViewer.SetRectangularGridGraphicValues((u2-u1)/2, (v2-v1)/2, 0.0)

        aViewer.ActivateGrid(Aspect_GT_Rectangular, Aspect_GDM_Lines)
        aViewer.SetGridEcho(True)


        if 'structure_li' not in self.__dict__: # new scale
            self.structure_li:list[Graphic3d_Structure] = list()

        for sturct in self.structure_li:
            sturct:Graphic3d_Structure
            sturct.Clear()
        self.structure_li.clear()

        for x, y in zip((u1, u2), (v1, v2)):
            struc = self._display.DisplayMessage(gp_Pnt(x, y, 0), f'({x}, {y})')
            self.structure_li.append(struc)

    def SetUVGrid(self, u1, u2, v1, v2):
        self.GridEnable(u1, u2, v1, v2)
        length = max((u2-u1), (v2-v1))
        self.TrihedronEnable(length)

    # selected object
    def GetSelectedObject(self):
        return self._display.Context.SelectedInteractive()

    def InitOperatorManager(self):
        from RedPanda.draw.Operator import MouseControl, ViewerOperator, WheelOperator, LineOperator

        self.operatorManager:MouseControl = MouseControl()
        self.operatorManager.RegisterWheelOperaor(WheelOperator(self, self._display))

        operator = ViewerOperator(self, self._display)
        self.operatorManager.Register(operator)
        self.operatorManager.Activate(operator.name)

        line = LineOperator(self, self._display)
        self.operatorManager.Register(line)

    def wheelEvent(self, event):
        self.operatorManager.wheelEvent(event, self.disp_ctx)

    def mousePressEvent(self, event):
        self.setFocus()
        self.operatorManager.mousePressEvent(event, self.disp_ctx)

    def mouseMoveEvent(self, evt):
        self.operatorManager.mouseMoveEvent(evt, self.disp_ctx)

    def mouseReleaseEvent(self, event):
        self.operatorManager.mouseReleaseEvent(event, self.disp_ctx)


    def ActiveOperator(self, name:str):
        self.operatorManager.Activate(name)

    def HoverPoint(self, x, y):
        from OCC.Core.BRep import BRep_Tool
        from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_WIRE, TopAbs_VERTEX
        from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnCurve

        from RedPanda.Core.topogy.edge import EdgeAnalyst

        projX, projy, projz, rayx, rayy, rayz = self._display.View.ProjReferenceAxe(x, y)   
        p = gp_Pnt(projX, projy, projz)
        shapes = self._display.selected_shapes[:]

        shape = TopoDS_Shape()
        param = [0.0 for _ in range(3)]
        if len(shapes) == 0:
            pass
        elif shapes[0].ShapeType() == TopAbs_VERTEX:
            p = BRep_Tool.Pnt(shapes[0])
            shape = shapes[0]
        elif shapes[0].ShapeType() == TopAbs_EDGE:
            shape = shapes[0]
            try:
                curve, u0, u1 = EdgeAnalyst(shapes[0]).curve
                builder = GeomAPI_ProjectPointOnCurve(p, curve)
                # print(u0, u1)
                # print(builder.LowerDistanceParameter(), builder.NearestPoint(), builder.LowerDistance())
                p = builder.NearestPoint()
                param[0] = builder.LowerDistanceParameter()
            except Exception as error:
                Logger().warning(f'hover point error:{error}')

        p2d = gp_Pnt(p.X(), p.Y(), 0)
        self.sig_point.emit(p2d, shape, param)

    def GetPoint(self, x, y):
        from OCC.Core.BRep import BRep_Tool
        from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_WIRE, TopAbs_VERTEX

        from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Lin
        from OCC.Core.BRep import BRep_Tool
        from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnCurve

        from RedPanda.Core.topogy.edge import EdgeAnalyst

        self._display.Select(x, y)
        shapes = self._display.selected_shapes[:]
        # self._display.Context.ClearSelected(True)
        # viewer
        # TODO: may be anything effection which isn't considering
        projX, projy, projz, rayx, rayy, rayz = self._display.View.ProjReferenceAxe(x, y)   
        p = gp_Pnt(projX, projy, projz)

        if len(shapes) == 0:
            pass
        elif shapes[0].ShapeType() == TopAbs_VERTEX:
            p = BRep_Tool.Pnt(shapes[0])
        elif shapes[0].ShapeType() == TopAbs_EDGE:
            try:
                curve, u0, u1 = EdgeAnalyst(shapes[0]).curve
                builder = GeomAPI_ProjectPointOnCurve(p, curve)
                # print(u0, u1)
                # print(builder.LowerDistanceParameter(), builder.NearestPoint(), builder.LowerDistance())
                p = builder.NearestPoint()
            except Exception as error:
                Logger().warning(f'get point :{error}')

        p2d = gp_Pnt2d(p.X(), p.Y())
        return p2d
