import os,sys
sys.path.append(os.getcwd()) 

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen


from RedPanda.logger import Logger

from RedPanda.RPAF.DisplayContext import DisplayCtx
from RedPanda.widgets.Ui_Viewer2d import Viewer2d

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
    def __init__(self, widget:QWidget, display:Viewer2d) -> None:
        self.widget = widget
        self._display = display

    @staticmethod
    def draw_rect_in_widget(widget:QWidget, rect):
        if rect is None or widget is None:
            return 
        # Create a QPainter object to draw on the widget
        painter = QPainter(widget)

        # Set the pen and brush to use for drawing
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        brush = QBrush(Qt.red, Qt.SolidPattern)
        painter.setPen(pen)
        painter.setBrush(brush)
        
        # Draw the rectangle
        painter.drawRect(QRect(*rect))

        # Clean up the painter object
        painter.end()
        widget.update()

    @staticmethod
    def draw_line_in_widget(widget:QWidget, rect):
        # Create a QPainter object to draw on the widget
        painter = QPainter(widget)
        
        # Set the pen to use for drawing
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)
        
        # Draw the line
        painter.drawLine(rect[0], rect[1], rect[0]+rect[2], rect[1]+rect[3])

        # Clean up the painter object
        painter.end()

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


    def drawbox(self, event):
        tolerance = 2
        pt = event.pos()
        dx = pt.x() - self.dragStartPosX
        dy = pt.y() - self.dragStartPosY
        if abs(dx) <= tolerance and abs(dy) <= tolerance:
            return

        self._drawbox = [self.dragStartPosX, self.dragStartPosY, dx, dy]

    def mousePressEvent(self, event, ctx:DisplayCtx):
        self.widget.setFocus()
        ev = event.pos()
        self.dragStartPosX = ev.x()
        self.dragStartPosY = ev.y()

    def mouseMoveEvent(self, evt:QMouseEvent, displayCtx:DisplayCtx):
        pass

    def mouseReleaseEvent(self, event, displayCtx:DisplayCtx):
        pass

class ViewerOperator(Operator):
    def __init__(self, widget: QWidget, display: Viewer2d) -> None:
        super().__init__(widget, display)
        
        self.name = 'Viewer'

        self._zoom_area = False
        self._select_area = False
        self._drawbox = None

    def mouseMoveEvent(self, evt, displayCtx: DisplayCtx):
        mod = evt.modifiers()
        buttons = int(evt.buttons())
        pt = evt.pos()
        # 启动状态, 记录信息
        if buttons == Qt.RightButton and mod == Qt.ShiftModifier:
            self._zoom_area = True
            self.cursor = "zoom-area"
            self.drawbox(evt)
            Operator.draw_rect_in_widget(self.widget, self._drawbox)

        elif buttons == Qt.LeftButton and mod == Qt.ShiftModifier:
            self._select_area = True
            self.drawbox(evt)
            Operator.draw_rect_in_widget(self.widget, self._drawbox)

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
            self.cursor = 'arrow'

    def mouseReleaseEvent(self, evt, displayCtx: DisplayCtx):
        pt = evt.pos()
        mod = evt.modifiers()
        if self._select_area:
            [Xmin, Ymin, dx, dy] = self._drawbox
            self._display.SelectArea(Xmin, Ymin, Xmin+dx, Ymin+dy)
            self._select_area = False
        elif self._zoom_area:
            [Xmin, Ymin, dx, dy] = self._drawbox
            self._display.ZoomArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
            self._zoom_area = False
        elif evt.button() == Qt.LeftButton and mod == Qt.ShiftModifier:
            self._display.ShiftSelect(pt.x(), pt.y())
        elif evt.button() == Qt.LeftButton:
            self._display.Select(pt.x(), pt.y())
        # elif evt.button() == Qt.RightButton:
        #     self.widget.showContextMenu(pt)
        else:
            return 

class LineOperator(Operator):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.name = 'line'

    def mouseMoveEvent(self, evt: QMouseEvent, display: Viewer2d, displayCtx: DisplayCtx):
        pt = evt.pos()
        buttons = int(evt.buttons())
        modifiers = evt.modifiers()

        if buttons == Qt.LeftButton:
            self.drawBox(evt)

    def mouseReleaseEvent(self, event:QMouseEvent, displayCtx: DisplayCtx):
        mod = event.modifiers()
        if self._select_area:
            [Xmin, Ymin, dx, dy] = self._drawbox
            self._display.SelectArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
        elif mod == Qt.ShiftModifier:
            pass


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
