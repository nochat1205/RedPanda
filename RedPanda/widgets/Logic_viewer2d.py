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

from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL
from PyQt5.QtCore import pyqtSlot
# QtCore, QtGui, QtWidgets, QtOpenGL = get_qt_modules()

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# log = logging.getLogger(__name__)

from OCC.Core.AIS import AIS_InteractiveContext, AIS_InteractiveObject
from OCC.Core.gp import gp_Pnt2d

from RedPanda.logger import Logger
from RedPanda.widgets.Ui_Viewer2d import Viewer2d

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

        self._trihedron = None
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
                [Xmin, Ymin, dx, dy] = self._drawbox
                self.SelectArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
                self._select_area = False
            else:
                # multiple select if shift is pressed
                if modifiers == QtCore.Qt.ShiftModifier:
                    self._display.ShiftSelect(pt.x(), pt.y())
                else:
                    # single select otherwise
                    self.Select(pt.x(), pt.y())

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

    def DisplayTrihedron(self, enable:bool=True):
        from OCC.Core.AIS import AIS_PlaneTrihedron
        from OCC.Core.Geom import Geom_Plane
        if enable:
            plane_ax3 = self._display.ViewPlane()
            pln = Geom_Plane(plane_ax3)
            ais_Trihedron = AIS_PlaneTrihedron(pln)
            aWindow = self.window()
            length = 10
            ais_Trihedron.SetLength(length)
            self._display.Context.Display(ais_Trihedron, False)
            self._display.DisplayMessage(gp_Pnt2d(0, length/2), f'(0, {length/2})')

            self._trihedron = ais_Trihedron
        else:
            if self._trihedron:
                self._display.Context.Erase(self._trihedron, False)
                self._trihedron = None

    def GridEnable(self, u1=0, u2=0, v1=100, v2=100):
        from OCC.Core.Quantity import Quantity_NOC_WHITE, Quantity_Color
        from OCC.Core.Aspect import (
            Aspect_GT_Rectangular, Aspect_GDM_Lines, Aspect_GDM_Points,
            Aspect_TOM_RING1,
        )
        from OCC.Core.Graphic3d import Graphic3d_AspectMarker3d
        self._display.Viewer.ActivateGrid(Aspect_GT_Rectangular, Aspect_GDM_Points)
        self._display.Viewer.SetGridEcho(True)
        aViewer = self._display.Viewer

        aGridAspect = Graphic3d_AspectMarker3d(Aspect_TOM_RING1, Quantity_Color(Quantity_NOC_WHITE), 2.0)
        aViewer.SetGridEcho(aGridAspect)
        aWindow = self.window()
        aWidth, aHeight = aWindow.width(), aWindow.height()
        aViewer.SetRectangularGridGraphicValues(u2-u1, v2-v1, 0.0)

        aViewer.SetRectangularGridValues (0, 0, (u2-u1)/10, (v2-v1)/10, 0)
        aViewer.ActivateGrid(Aspect_GT_Rectangular, Aspect_GDM_Lines)

    def Display_Plane(self, face):
        from OCC.Core.BRep import BRep_Tool_Surface
        from OCC.Core.Geom import Geom_Plane
    
        self.GridEnable()
        surface = BRep_Tool_Surface(face)
        plane:Geom_Plane = Geom_Plane.DownCast(surface)
        pln = plane.Pln()
        self._display.FocusOn(pln.Position())
        self.DisplayTrihedron()
        self._display.DisplayShape(face)

    def DisplaySurfaceFlay(self, surface):
        from OCC.Core.Geom import Geom_Surface
        from OCC.Core.gp import gp_Ax3
        surface:Geom_Surface
        u1, u2, v1, v2 = surface.Bounds()
        self.GridEnable(u1, u2, v1, v2)
        self.DisplayTrihedron()

    # selected object
    def GetSelectedObject(self):
        return self._display.Context.SelectedInteractive()

    def SelectArea(self, Xmin, Ymin, Xmax, Ymax)->list[AIS_InteractiveObject]:
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
        aContext.InitSelected()
        while aContext.MoreSelected():
            if aContext.HasSelectedShape():
                self.__selectedObject_li.append(aContext.SelectedInteractive())
            aContext.NextSelected()
        print(f'Arealen:{len(self.__selectedObject_li)}')

        from OCC.Core.StdSelect import StdSelect_BRepOwner
        from RedPanda.Core.topogy.types_lut import shape_lut
        for obj in self.__selectedObject_li:
            obj:AIS_InteractiveObject
            print('rin')
            brepOwer:StdSelect_BRepOwner = StdSelect_BRepOwner.DownCast(obj.GetOwner())
            print(shape_lut(brepOwer.Shape().ShapeType()))

        return self.__selectedObject_li

    def Select(self, X, Y):
        self.selected_shapes = []

        aContext = self._display.Context

        aContext.Select(True)
        aContext.InitSelected()
        from OCC.Core.AIS import AIS_KindOfInteractive_Shape,AIS_Shape
        from RedPanda.Core.topogy.types_lut import topo_lut
        from OCC.Core.StdSelect import StdSelect_BRepOwner
        if aContext.MoreSelected():
            if aContext.HasSelectedShape():
                owner = aContext.SelectedOwner()
                self.selected_shapes.append(StdSelect_BRepOwner.DownCast(owner))

        from OCC.Core.TopoDS import TopoDS_Shape
        for obj in self.selected_shapes:
            obj:StdSelect_BRepOwner
            shape:TopoDS_Shape = obj.Shape()
            interactive = AIS_Shape.DownCast(obj.Selectable())
            shapep = interactive.Shape()
            print('pa:', topo_lut[shapep.ShapeType()])
            print('me:', topo_lut[shape.ShapeType()])
