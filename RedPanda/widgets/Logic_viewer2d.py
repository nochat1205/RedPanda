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

class qtViewer2d(qtBaseViewer):
    # emit signal when selection is changed
    # is a list of TopoDS_*
    HAVE_PYQT_SIGNAL = False
    if hasattr(QtCore, "pyqtSignal"):  # PyQt
        sig_topods_selected = QtCore.pyqtSignal(list)
        HAVE_PYQT_SIGNAL = True
    elif hasattr(QtCore, "Signal"):  # PySide2
        sig_topods_selected = QtCore.Signal(list)
        HAVE_PYQT_SIGNAL = True

    def __init__(self, *kargs):
        qtBaseViewer.__init__(self, *kargs)
        self.ais_dict = None
        self.aLabel = None

        self.setObjectName("qt_viewer_3d")

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
            return 
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
            rect = QtCore.QRect(*self._drawbox)
            painter.drawRect(rect)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            zoom_factor = 2.0
        else:
            zoom_factor = 0.5
        self._display.ZoomFactor(zoom_factor)

    @property
    def cursor(self):
        return self._current_cursor

    @cursor.setter
    def cursor(self, value):
        if not self._current_cursor == value:

            self._current_cursor = value
            cursor = self._available_cursors.get(value)

            if cursor:
                self.qApp.setOverrideCursor(cursor)
            else:
                self.qApp.restoreOverrideCursor()

    def mousePressEvent(self, event):
        self.setFocus()
        ev = event.pos()
        self.dragStartPosX = ev.x()
        self.dragStartPosY = ev.y()
        # self._display.StartRotation(self.dragStartPosX, self.dragStartPosY)

    def mouseReleaseEvent(self, event):
        pt = event.pos()
        modifiers = event.modifiers()

        if event.button() == QtCore.Qt.LeftButton:
            if self._select_area:
                from OCC.Extend.ShapeFactory import make_edge
                [Xmin, Ymin, dx, dy] = self._drawbox
                self._display.SelectArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
                # p0 = self.GetPoint(Xmin, Ymin)
                # p1 = self.GetPoint(Xmin+dx, Ymin+dy)
                # self._display.DisplayShape(make_edge(p0, p1), update=True)

                self._select_area = False
            else:
                # multiple select if shift is pressed
                if modifiers == QtCore.Qt.ShiftModifier:
                    self._display.ShiftSelect(pt.x(), pt.y())
                else:
                    # single select otherwise
                    self._display.Select(pt.x(), pt.y())

                    if (self._display.selected_shapes is not None) and self.HAVE_PYQT_SIGNAL:

                        self.sig_topods_selected.emit(self._display.selected_shapes)

        elif event.button() == QtCore.Qt.RightButton:
            if self._zoom_area:
                [Xmin, Ymin, dx, dy] = self._drawbox
                self._display.ZoomArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
                self._zoom_area = False

        self.cursor = "arrow"

    def DrawBox(self, event):
        tolerance = 2
        pt = event.pos()
        dx = pt.x() - self.dragStartPosX
        dy = pt.y() - self.dragStartPosY
        if abs(dx) <= tolerance and abs(dy) <= tolerance:
            return
        self._drawbox = [self.dragStartPosX, self.dragStartPosY, dx, dy]

    def mouseMoveEvent(self, evt):
        pt = evt.pos()
        buttons = int(evt.buttons())
        modifiers = evt.modifiers()
        # ROTATE
        if buttons == QtCore.Qt.LeftButton and not modifiers == QtCore.Qt.ShiftModifier:
            self.cursor = "rotate"
            # self._display.Rotation(pt.x(), pt.y())
            self._drawbox = False
        # DYNAMIC ZOOM
        elif (
            buttons == QtCore.Qt.RightButton
            and not modifiers == QtCore.Qt.ShiftModifier
        ):
            self.cursor = "zoom"
            self._display.Repaint()
            self._display.DynamicZoom(
                abs(self.dragStartPosX),
                abs(self.dragStartPosY),
                abs(pt.x()),
                abs(pt.y()),
            )
            self.dragStartPosX = pt.x()
            self.dragStartPosY = pt.y()
            self._drawbox = False
        # PAN
        elif buttons == QtCore.Qt.MidButton:
            dx = pt.x() - self.dragStartPosX
            dy = pt.y() - self.dragStartPosY
            self.dragStartPosX = pt.x()
            self.dragStartPosY = pt.y()
            self.cursor = "pan"
            self._display.Pan(dx, -dy)
            self._drawbox = False
        # DRAW BOX
        # ZOOM WINDOW
        elif buttons == QtCore.Qt.RightButton and modifiers == QtCore.Qt.ShiftModifier:
            self._zoom_area = True
            self.cursor = "zoom-area"
            self.DrawBox(evt)
            self.update()
        # SELECT AREA
        elif buttons == QtCore.Qt.LeftButton and modifiers == QtCore.Qt.ShiftModifier:
            self._select_area = True
            self.DrawBox(evt)
            self.update()
        else:
            self._drawbox = False
            self._display.MoveTo(pt.x(), pt.y())
            self.cursor = "arrow"


    # desprete
    def SelectArea(self, Xmin, Ymin, Xmax, Ymax)->list[AIS_InteractiveObject]:
        return 
        from OCC.Core.StdSelect import StdSelect_BRepOwner
        from RedPanda.Core.topogy.types_lut import shape_lut

        """ get interative object in the area
        Args:
            Xmin (int): 
            Ymin (int): _description_
            Xmax (int): _description_
            Ymax (int): _description_

        Returns:
            list[AIS_InteractiveObject]: ineractive object in the area
        """

        self.__selectedObject_li = list()
        aContext = self._display.Context
        aContext.Select(Xmin, Ymin, Xmax, Ymax, self.View, True)

        aContext.InitSelected()
        while aContext.MoreSelected():
            if aContext.HasSelectedShape():
                self.__selectedObject_li.append(aContext.SelectedInteractive())
            aContext.NextSelected()
        print(f'Arealen:{len(self.__selectedObject_li)}')

        for obj in self.__selectedObject_li:
            obj:AIS_InteractiveObject
            brepOwer:StdSelect_BRepOwner = StdSelect_BRepOwner.DownCast(obj.GetOwner())

        return self.__selectedObject_li

    def Select(self, X, Y):
        '''
        despre
        '''
        return 
        from OCC.Core.TopoDS import TopoDS_Shape

        self.selected_shapes = []

        aContext = self._display.Context

        aContext.Select(True)
        aContext.InitSelected()
        if aContext.MoreSelected():
            if aContext.HasSelectedShape():
                owner = aContext.SelectedOwner()
                self.selected_shapes.append(StdSelect_BRepOwner.DownCast(owner))

        # for obj in self.selected_shapes:
        #     obj:StdSelect_BRepOwner
        #     shape:TopoDS_Shape = obj.Shape()
        #     interactive = AIS_Shape.DownCast(obj.Selectable())
        #     shapeparent = interactive.Shape()

    # Prsentation
    def clear(self):
        self._display.Context.RemoveAll(False)
        self.ais_dict = None
        self.aLabel = None

    def ShowLabel(self, theLabel):

        self.clear()
        aDriver:BareShapeDriver = theLabel.GetDriver()
        if aDriver is None:
            return

        self.aLabel = theLabel
        ctx = aDriver.Prs2d(theLabel)
        self.ais_dict = ctx
        aDriver.UpdatePrs2d(theLabel, ctx)
        for ais in ctx.values():
            self._display.Context.Display(ais, False)

        self._display.FitAll()
        self._display.Repaint()

    def UpdateLabel(self):
        aDriver:BareShapeDriver = self.aLabel.GetDriver()
        if aDriver is None:
            return

        if not aDriver.UpdatePrs2d(self.aLabel, self.ais_dict):
            return 

        for ais in self.ais_dict.values():
            self._display.Context.Display(ais, False)

        self.SetUVGrid(*self.ais_dict.GetBound())

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
        length = max((u2-u1)/2, (v2-v1)/2)
        self.TrihedronEnable(length)

    # selected object
    def GetSelectedObject(self):
        return self._display.Context.SelectedInteractive()

    def GetPoint(self, x, y):
        from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Lin
        from OCC.Core.Geom import Geom_Line
        from OCC.Core.TopoDS import TopoDS_Shape
        from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_WIRE, TopAbs_VERTEX
        from OCC.Core.BRep import BRep_Tool
        from OCC.Core.BRepLib import breplib_BuildCurve3d
        from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
        from OCC.Extend.ShapeFactory import make_edge, make_wire
        from RedPanda.Core.Make import project_point_on_curve

        # self._display.Context.ClearSelected(True)
        shapes:list[TopoDS_Shape] = self._display.Select(x, y)

        projX, projy, projz, rayx, rayy, rayz = self._display.View.ProjReferenceAxe(x, y)
        p = gp_Pnt(projX, projy, projz)
        if len(shapes) == 0:
            return p

        if shapes[0].ShapeType() == TopAbs_VERTEX:
            p = BRep_Tool.Pnt(shapes[0])
            # self._display.DisplayMessage(p, f'Coord:{p.Coord()}')
        elif shapes[0].ShapeType() == TopAbs_EDGE:
            try:
                # 1
                dir = gp_Dir(rayx, rayy, rayz)
                line = gp_Lin(p, dir)
                edge = make_edge(line)
                wire = make_wire(shapes[0])
                extrema = BRepExtrema_DistShapeShape(wire, edge)
                p = extrema.PointOnShape1(1)

                # 2
                # from RedPanda.Core.topogy.edge import EdgeAnalyst
                # analyst = EdgeAnalyst(shapes[0])
                # print(analyst.parameter_to_point(0).Coord())
                # param, pnt = project_point_on_curve(analyst, p)
            except Exception as error:
                Logger().warning(f'error:{error}')

        return p
