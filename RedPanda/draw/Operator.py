import os,sys
sys.path.append(os.getcwd()) 

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen


from RedPanda.logger import Logger

from RedPanda.RPAF.DisplayContext import DisplayCtx
from RedPanda.Core.Euclid import RP_Pnt2d
from RedPanda.widgets.Ui_Viewer2d import Viewer2d


class PixelPoint(RP_Pnt2d):
    def X(self) -> float:
        return int(super().X())

    def Y(self) -> float:
        return int(super().Y())

class WheelOperator(object):
    def __init__(self, parent:QWidget, display) -> None:
        # static message
        self.name = 'Wheel'

        # 静态参数变量
        self.parent = parent
        self._display = display


    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            zoom_factor = 2.0
        else:
            zoom_factor = 0.5
        self._display.ZoomFactor(zoom_factor)

    def mousePressEvent(self, event:QMouseEvent, ctx:DisplayCtx):
        ev = event.pos()
        self.dragStartPosX = ev.x()
        self.dragStartPosY = ev.y()

    def mouseMoveEvent(self, evt:QMouseEvent, ctx):
        pt = evt.pos()
        dx = pt.x() - self.dragStartPosX
        dy = pt.y() - self.dragStartPosY
        self.dragStartPosX = pt.x()
        self.dragStartPosY = pt.y()
        self.cursor = "pan"
        self._display.Pan(dx, -dy)

    def mouseReleaseEvent(self, event:QMouseEvent, ctx:DisplayCtx):
        pass

class Operator(object):
    def __init__(self, widget, display:Viewer2d) -> None:
        from ..widgets.Logic_Viewer2d import qtViewer2d
        self.widget:qtViewer2d = widget
        self._display = display

        self.dragStartP = None
        self.dragEndP = None

    def update_dragLine(self, event):
        tolerance = 2
        pt = event.pos()
        pt = PixelPoint(pt.x(), pt.y())
        distp = pt-self.dragStartP
        if distp < tolerance:
            return 
        self.dragEndP = pt

    def mousePressEvent(self, event, ctx:DisplayCtx):
        ev = event.pos()
        self.dragStartP = PixelPoint(ev.x(), ev.y())
        self.dragEndP = None

    def mouseMoveEvent(self, evt:QMouseEvent, displayCtx:DisplayCtx):
        pass

    def mouseReleaseEvent(self, event, displayCtx:DisplayCtx):
        pass

    def quit(self):
        pass


class ViewerOperator(Operator):
    def __init__(self, widget: QWidget, display: Viewer2d) -> None:
        super().__init__(widget, display)
        
        self.name = 'viewer'

        self._zoom_area = False
        self._select_area = False

    def mouseMoveEvent(self, evt, displayCtx: DisplayCtx):
        mod = evt.modifiers()
        buttons = int(evt.buttons())
        pt = evt.pos()

        # 启动状态, 记录信息
        if buttons == Qt.RightButton and mod == Qt.ShiftModifier:
            self._zoom_area = True
            self.cursor = "zoom-area"
            self.drawbox(evt)
            # Operator.draw_rect_in_widget(self.widget, self._drawbox)

        elif buttons == Qt.LeftButton and mod == Qt.ShiftModifier:
            self._select_area = True
            self.drawbox(evt)
            # Operator.draw_rect_in_widget(self.widget, self._drawbox)

        elif buttons == Qt.RightButton:
            self.cursor = 'zoom'
            self._display.Repaint()
            self._display.DynamicZoom(
                abs(self.dragStartPosX),
                abs(self.dragStartPosY),
                abs(pt.x()),
                abs(pt.y()),
            )
        else:
            self._display.MoveTo(pt.x(), pt.y())
            self.widget.cursor = 'arrow'

    def mouseReleaseEvent(self, evt, displayCtx: DisplayCtx):
        pt = evt.pos()
        mod = evt.modifiers()
        if self._select_area and self._drawbox:
            [Xmin, Ymin, dx, dy] = self._drawbox
            self._display.SelectArea(Xmin, Ymin, Xmin+dx, Ymin+dy)
            self._select_area = False
        elif self._zoom_area and self._drawbox:
            [Xmin, Ymin, dx, dy] = self._drawbox
            self._display.ZoomArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
            self._zoom_area = False
        elif evt.button() == Qt.LeftButton and mod == Qt.ShiftModifier:
            self._display.ShiftSelect(pt.x(), pt.y())
        elif evt.button() == Qt.LeftButton:
            self._display.Select(pt.x(), pt.y())
            self.widget.HoverPoint(pt.x(), pt.y())
        # elif evt.button() == Qt.RightButton:
        #     self.widget.showContextMenu(pt)
        else:
            return 

from OCC.Core.AIS import AIS_ColoredShape
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_ORANGE
from OCC.Core.GCE2d import GCE2d_MakeSegment
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge2d, BRepBuilderAPI_MakeEdge
from OCC.Core.BRepLib import breplib_BuildCurve3d
from OCC.Core.gp import gp_Pln
from OCC.Core.Geom import Geom_Plane
from RedPanda.RPAF.DataDriver.Geom2dDriver import Segment2dDriver
class LineOperator(Operator):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.name = 'line'
        self.line_li = list()
        self.ais = None

    def mousePressEvent(self, event, ctx: DisplayCtx):
        super().mousePressEvent(event, ctx)
        x0, y0 = self.dragStartP.X(), self.dragStartP.Y()
        self.sp = self.widget.GetPoint(x0, y0)

    def mouseMoveEvent(self, evt: QMouseEvent, displayCtx: DisplayCtx):
        buttons = int(evt.buttons())
        mod = evt.modifiers()
        if buttons == Qt.LeftButton:
            self.update_dragLine(evt)
            if self.dragEndP is None:
                return

            x0, y0 = self.dragStartP.X(), self.dragStartP.Y()
            x1, y1 = self.dragEndP.X(), self.dragEndP.Y()
            dx, dy = x1 - x0, y1-y0
            if mod == Qt.ShiftModifier:
                if abs(dx) > abs(dy):
                    y1 = y0
                elif abs(dx) < abs(dy):
                    x1 = x0
            try:
                sp = self.sp
                ep = self.widget.GetPoint(x1, y1)
                seg = GCE2d_MakeSegment(sp, ep).Value()
                # edge = BRepBuilderAPI_MakeEdge2d(seg).Edge()
                pln_ax3 = self._display.ViewPlane()
                pln = Geom_Plane(pln_ax3)
                edge = BRepBuilderAPI_MakeEdge(seg, pln).Shape()
                # breplib_BuildCurve3d(edge) # 问题出在这.
                # print(f"({x0}, {y0}) -> ({x1}, {y1})")

                if self.ais:
                    self._display.Context.Erase(self.ais, False)
                    # self.ais.ErasePresentations(True)
    
                self.ais = AIS_ColoredShape(edge)
                self._display.Context.Display(self.ais, True)
            except Exception as err:
                print(err)

    def mouseReleaseEvent(self, event:QMouseEvent, displayCtx: DisplayCtx):
        mod = event.modifiers()
        
        self.update_dragLine(event)

        if event.button() == Qt.LeftButton and self.dragEndP:
            x0, y0 = self.dragStartP.X(), self.dragStartP.Y()
            x1, y1 = self.dragEndP.X(), self.dragEndP.Y()
            dx, dy = x1 - x0, y1-y0
            if mod == Qt.ShiftModifier:
                if abs(dx) > abs(dy):
                    y1 = y0
                elif abs(dx) < abs(dy):
                    x1 = x0
    
            p2d1 = self.widget.GetPoint(x0, y0)
            p2d2 = self.widget.GetPoint(x1, y1)

            # print(x, y, dx, dy)
            # print(p2d1.X(), p2d1.Y(), p2d2.X(), p2d2.Y())

            param = {'p1': {'x':str(p2d1.X()), 
                            'y':str(p2d1.Y())}, 
                     'p2':{'x':p2d2.X().__str__(), 
                           'y':p2d2.Y().__str__()}}
            self.widget.sig_new_shape.emit(Segment2dDriver.ID, param)

        self.line_li.append(self.ais)
        self.ais = None

    def quit(self):
        for ais in self.line_li:
            self._display.Context.Remove(ais, False)
        self._display.View.SetImmediateUpdate(True)
        self.line_li.clear()


from OCC.Core.GCE2d import GCE2d_MakeCircle
class CircleOperator(Operator):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.name = 'circle'
        self.line_li = list()
        self.ais = None

    def mousePressEvent(self, event, ctx: DisplayCtx):
        super().mousePressEvent(event, ctx)
        x0, y0 = self.dragStartP.X(), self.dragStartP.Y()
        self.sp = self.widget.GetPoint(x0, y0)

    def mouseMoveEvent(self, evt: QMouseEvent, displayCtx: DisplayCtx):
        buttons = int(evt.buttons())
        mod = evt.modifiers()
        if buttons == Qt.LeftButton:
            self.update_dragLine(evt)
            if self.dragEndP is None:
                return

            x0, y0 = self.dragStartP.X(), self.dragStartP.Y()
            x1, y1 = self.dragEndP.X(), self.dragEndP.Y()
            dx, dy = x1-x0, y1-y0

            try:
                sp = self.sp
                ep = self.widget.GetPoint(x1, y1)
                
                seg = GCE2d_MakeSegment(sp, ep).Value()
                # edge = BRepBuilderAPI_MakeEdge2d(seg).Edge()
                pln_ax3 = self._display.ViewPlane()
                pln = Geom_Plane(pln_ax3)
                edge = BRepBuilderAPI_MakeEdge(seg, pln).Shape()
                # breplib_BuildCurve3d(edge) # 问题出在这. 这行函数会多余的影响
                # print(f"({x0}, {y0}) -> ({x1}, {y1})")

                if self.ais:
                    self._display.Context.Erase(self.ais, False)
                    # self.ais.ErasePresentations(True)
    
                self.ais = AIS_ColoredShape(edge)
                self._display.Context.Display(self.ais, True)
            except Exception as err:
                print(err)

    def mouseReleaseEvent(self, event:QMouseEvent, displayCtx: DisplayCtx):
        mod = event.modifiers()
        
        self.update_dragLine(event)

        if event.button() == Qt.LeftButton and self.dragEndP:
            x0, y0 = self.dragStartP.X(), self.dragStartP.Y()
            x1, y1 = self.dragEndP.X(), self.dragEndP.Y()
            dx, dy = x1 - x0, y1-y0
            if mod == Qt.ShiftModifier:
                if abs(dx) > abs(dy):
                    y1 = y0
                elif abs(dx) < abs(dy):
                    x1 = x0
    
            p2d1 = self.widget.GetPoint(x0, y0)
            p2d2 = self.widget.GetPoint(x1, y1)

            # print(x, y, dx, dy)
            # print(p2d1.X(), p2d1.Y(), p2d2.X(), p2d2.Y())

            param = {'p1': {'x':str(p2d1.X()), 
                            'y':str(p2d1.Y())}, 
                     'p2':{'x':p2d2.X().__str__(), 
                           'y':p2d2.Y().__str__()}}
            self.widget.sig_new_shape.emit(Segment2dDriver.ID, param)

        self.line_li.append(self.ais)
        self.ais = None

    def quit(self):
        for ais in self.line_li:
            self._display.Context.Remove(ais, False)
        self._display.View.SetImmediateUpdate(True)
        self.line_li.clear()

class MouseControl(object):
    def __init__(self) -> None:
        self.operator_d = dict()
        self.wheel_operator:WheelOperator = None
        self.runing_operator:Operator = None

    def RegisterWheelOperaor(self, operator):
        self.wheel_operator:WheelOperator = operator

    def Register(self, operator):
        if operator.name in self.operator_d:
            Logger().warning(f'operator with name:{operator.name} had existed ')
            return False
        self.operator_d[operator.name] = operator
        return True

    def Activate(self, name):
        if name in self.operator_d:
            if self.runing_operator != self.operator_d[name]:
                if self.runing_operator:
                    self.runing_operator.quit()
                self.runing_operator = self.operator_d[name]
                Logger().info(f'change to opertor to {name}')

    def wheelEvent(self, event, ctx):
        self.wheel_operator.wheelEvent(event)

    def mousePressEvent(self, event, ctx):
        if event.button() == Qt.MidButton:
            self.wheel_operator.mousePressEvent(event, ctx)

        else:
            self.runing_operator.mousePressEvent(event, ctx)

    def mouseMoveEvent(self, event, ctx):
        buttons = int(event.buttons())

        if buttons == Qt.MidButton:
            self.wheel_operator.mouseMoveEvent(event, ctx)

        elif buttons == Qt.LeftButton or buttons == Qt.RightButton:
            self.runing_operator.mouseMoveEvent(event, ctx)

    def mouseReleaseEvent(self, event, ctx):
        if event.button() == Qt.MidButton:
            self.wheel_operator.mouseReleaseEvent(event, ctx)

        else:
            self.runing_operator.mouseReleaseEvent(event, ctx)
