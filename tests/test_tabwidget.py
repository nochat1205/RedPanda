from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Display.OCCViewer import rgb_color
from OCC.Display import OCCViewer

from OCC.Display.backend import load_backend,get_loaded_backend
load_backend("qt-pyqt5")
import OCC.Display.qtDisplay as qtDisplay
from OCC.Display.SimpleGui import init_display
import sys,os
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Display.OCCViewer import rgb_color

class MainWindow(QMainWindow):
    BORDER_WIDTH = 5
    def __init__(self):
        super().__init__()

        self.main_widget = QTabWidget()
        self.setCentralWidget(self.main_widget)

        box = BRepPrimAPI_MakeBox(10, 10, 10).Shape()
        self.canvas = qtDisplay.qtViewer3d(self)
        print(f'inited:{self.canvas._inited}')
        # self.canvas.InitDriver()
        # self.canvas._display.DisplayShape(box)
        print(f'inited:{self.canvas._inited}')

        self.main_widget.addTab(self.canvas, 'test1')


        self.canvas2 = qtDisplay.qtViewer3d(self)
        self.canvas2._display.DisplayShape(box)
        self.canvas2.InitDriver()
        # my_box = BRepPrimAPI_MakeBox (10,10,10).Shape()
        # self.display.DisplayShape(my_box,update=True,color=rgb_color(0,1,0))
        self.main_widget.addTab(self.canvas2, 'test2')


app = QApplication(sys.argv)
win = MainWindow()
win.show()
win.raise_() 
app.exec_()