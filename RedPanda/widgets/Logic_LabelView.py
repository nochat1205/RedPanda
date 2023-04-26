import typing
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QListView,
    QScrollArea, QSizePolicy, QDialog
)
from RedPanda.RD_Singleton import Singleton
from RedPanda.RPAF.DataDriver import (
    BaseDriver,
    Argument
)

from RedPanda.RPAF.DriverTable import DataDriverTable
from RedPanda.RPAF.RD_Label import Label

from .Ui_LabelView import Ui_Dialog
from .Logic_Construct import Logic_Construct
from .Logic_Viewer import qtViewer3d
from .Logic_viewer2d import qtViewer2d

class LabelView(QDialog):
    sig_change = pyqtSignal(Label, str)
    def __init__(self, parent: typing.Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        
        right_layout = QVBoxLayout()
        self.v3d = qtViewer3d(self.ui.RightArea)
        self.v2d = qtViewer2d(self.ui.RightArea)
        
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.v3d.setSizePolicy(size_policy)
        self.v2d.setSizePolicy(size_policy)
    
        self.v2d.setHidden(False)

        right_layout.addWidget(self.v3d)
        right_layout.addWidget(self.v2d)
        self.ui.RightArea.setLayout(right_layout)

        # self.commit_bt = self.ui.commit_bt

        dataArea = self.ui.DataArea
        notDataArea = self.ui.NotDataArea

        self._content:Logic_Construct = Logic_Construct()
        dataArea.setWidget(self._content)
        
        # signal and slot
        self._content.sig_change.connect(self.onChange)

    def ShowLabel(self, theLabel:Label):
        self._content.ShowLabel(theLabel)

    def UpdataLabel(self, theLabel):
        self._content.Update(theLabel)
        aDriver = theLabel.GetDriver()
        for ais in aDriver.Presentaion3d().values():
            self.v3d._display.DisplayShape(ais)
        for ais in aDriver.Presentaion2d().values():
            self.v2d._display.DisplayShape(ais)

    def onChange(self, label, str):
         self.sig_change.emit(label, str)

    def Test(self):
        from OCC.Core.Geom import Geom_CylindricalSurface, Geom_RectangularTrimmedSurface
        from OCC.Core.Geom2d import Geom2d_Ellipse, Geom2d_TrimmedCurve
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
        from RedPanda.Core.topogy import FaceAnalyst
        from RedPanda.Core.topogy import make_face
        from RedPanda.Core.Euclid import RP_Ax3
        from OCC.Core.gp import gp_Pnt2d, gp_Dir2d, gp_Ax2d
        from math import pi
        height = 20
        cy = Geom_CylindricalSurface(RP_Ax3(), 3)
        surface = Geom_RectangularTrimmedSurface(cy, 0, 2*pi, 0, height)

        aPnt = gp_Pnt2d(2*pi, height/2)
        aDir = gp_Dir2d(2*pi, height/4)
        anAx2d = gp_Ax2d(aPnt, aDir)
        aMajor = 2 * pi
        aMinor = height / 10
        anEllipse1 = Geom2d_Ellipse(anAx2d, aMajor, aMinor)
        anArc1 = Geom2d_TrimmedCurve(anEllipse1, 0, pi)
        anEdge10Surf1 = BRepBuilderAPI_MakeEdge(anArc1, cy).Edge()

        from OCC.Core.gp import gp_Ax3, gp_Pnt, gp_Dir
        ax = gp_Ax3(gp_Pnt(aPnt.X(), aPnt.Y(), 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
        self.v2d._display.FocusOn(ax)
        self.v3d._display.DisplayShape(surface)
        self.v2d.DisplaySurfaceFlay(surface)


        self.v3d._display.DisplayShape(anEdge10Surf1)
        self.v2d._display.DisplayShape(anArc1)
