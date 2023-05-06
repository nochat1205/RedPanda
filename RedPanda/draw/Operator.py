from RedPanda.Core.Euclid import RP_Pnt

class Operator(object):
    def __init__(self) -> None:
        self.p0 = RP_Pnt()
        self.p1 = RP_Pnt()

    def onMousePressEvent(self, point):
        self.p0 = point

    def onMouseReleaseEvent(self, point):
        self.p1 = point

class DrawLine(Operator):
    def onMousePressEvent(self, point):
        super().onMouseReleaseEvent()
        
        
        return 