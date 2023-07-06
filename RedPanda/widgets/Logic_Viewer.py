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
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QMouseEvent
# QtCore, QtGui, QtWidgets, QtOpenGL = get_qt_modules()

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# log = logging.getLogger(__name__)

from OCC.Core.AIS import AIS_InteractiveContext

from RedPanda.logger import Logger
from RedPanda.widgets.Ui_Viewer import Viewer3d
from RedPanda.RPAF.DataDriver import BareShapeDriver
from RedPanda.RPAF.GUID import RP_GUID

class qtBaseViewer(QtWidgets.QWidget):
    """The base Qt Widget for an OCC viewer"""

    def __init__(self, parent=None):
        super(qtBaseViewer, self).__init__(parent)
        self._display = Viewer3d()
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


class qtViewer3d(qtBaseViewer):
    # emit signal when selection is changed
    # is a list of TopoDS_*
    HAVE_PYQT_SIGNAL = True
    sig_topods_selected = QtCore.pyqtSignal(list)

    sig_new_shape = pyqtSignal(RP_GUID, dict)

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
        self._ais_objects = set()

        self._key_map = {
            ord("W"): self._display.SetModeWireFrame,
            ord("S"): self._display.SetModeShaded,
            ord("A"): self._display.EnableAntiAliasing,
            ord("B"): self._display.DisableAntiAliasing,
            ord("H"): self._display.SetModeHLR,
            ord("F"): self._display.FitAll,
            ord("G"): self._display.SetSelectionMode,
            ord('X'): self._display.View_Left,
            ord('Y'): self._display.View_Top,
            ord('Z'): self._display.View_Front
            
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
        self._display.SetModeShaded()

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
        super(qtViewer3d, self).keyPressEvent(event)
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

    def mousePressEvent(self, event:QMouseEvent):
        self.setFocus()
        ev = event.pos()
        self.dragStartPosX = ev.x()
        self.dragStartPosY = ev.y()
        self._display.StartRotation(self.dragStartPosX, self.dragStartPosY)
        self._display.View.StartZoomAtPoint(self.dragStartPosX, self.dragStartPosY)
    def mouseReleaseEvent(self, event:QMouseEvent):
        pt = event.pos()
        modifiers = event.modifiers()

        if event.button() == QtCore.Qt.LeftButton:
            if self._select_area:
                [Xmin, Ymin, dx, dy] = self._drawbox
                self._display.SelectArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
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
            else:
                self.showContextMenu(pt)

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
            self._display.Rotation(pt.x(), pt.y())
            self._drawbox = False
        # DYNAMIC ZOOM
        elif (
            buttons == QtCore.Qt.RightButton
            and not modifiers == QtCore.Qt.ShiftModifier
        ):
            self.cursor = "zoom"
            self._display.Repaint()

            # pan
            dx = pt.x() - self.dragStartPosX
            dy = pt.y() - self.dragStartPosY

            self._display.View.ZoomAtPoint(
                abs(self.dragStartPosX),
                abs(self.dragStartPosY),
                abs(pt.x()),
                abs(pt.y()),
            )
            # self.dragStartPosX = pt.x()
            # self.dragStartPosY = pt.y()
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

    # --- --- presentation --- ---
    def clear(self):
        self._display.Context.RemoveAll(False)

    def ShowLabel(self, theLabel):
        from RedPanda.RPAF.DisplayContext import DisplayCtx
        aDriver:BareShapeDriver = theLabel.GetDriver()
        if aDriver is None or not isinstance(aDriver, BareShapeDriver):
            return
        
        # TODO:
        self.clear()

        ctx:DisplayCtx = aDriver.Prs3d(theLabel)
        self.ctx = ctx

        for ais in ctx.values():
            self._display.Context.Display(ais, False)

        self._display.FitAll()
        self._display.Repaint()

    def UpdateLabel(self, theLabel):
        from OCC.Core.AIS import AIS_ColoredShape
        aDriver:BareShapeDriver = theLabel.GetDriver()

        if aDriver is None:
            return

        self._display.Context.RemoveAll(False) #TODO:
        if not aDriver.UpdatePrs3d(theLabel, self.ctx):
            return

        for ais in self.ctx.values():
            ais:AIS_ColoredShape
            if ais is None:
                continue
            self._display.Context.Display(ais, False)

        self._display.Viewer.Update()
        self._display.Repaint()

    # menu
    def showContextMenu(self, position):
        from PyQt5.QtWidgets import QMenu, QAction

        # create a context menu
        menu = QMenu(self)

        # Create copy and paste actions for the menu
        refAction = QAction("Ref Shape", self)
        refAction.triggered.connect(self.GetRefSub)
        
        # Add the actions to the menu
        menu.addAction(refAction)
        
        # Show the menu at the position of the mouse click
        menu.exec_(self.mapToGlobal(position))

    #  menu function
    def GetRefSub(self):
        from OCC.Core.AIS import AIS_Shape, AIS_ColoredShape
        from OCC.Core.StdSelect import StdSelect_BRepOwner
        from OCC.Core.TopExp import TopExp_Explorer
        from OCC.Core.TopoDS import TopoDS_Shape
        # need selected_ais_li
        if len(self._display.selected_ais_li) > 0:
            owner:StdSelect_BRepOwner = StdSelect_BRepOwner.DownCast(self._display.selected_ais_li[0])
            if owner is None:
                print('owner is None')
                return

            subshape:TopoDS_Shape = owner.Shape()

            parentAis = AIS_ColoredShape.DownCast(owner.Selectable())
            if parentAis is None:
                return 

            shape = parentAis.Shape()
            explorer = TopExp_Explorer(shape, subshape.ShapeType())
            i = 0
            while explorer.More():
                i += 1
                if explorer.Value() == subshape:
                    break
                explorer.Next()

            label = self.ctx.GetLabel(parentAis)
            if label:
                from RedPanda.RPAF.DataDriver.ShapeDriver import RefSubDriver
                data = {'Shape': label.GetEntry(), 'TopoType':subshape.ShapeType(), 'Index':i}
                self.sig_new_shape.emit(RefSubDriver.ID, data)
