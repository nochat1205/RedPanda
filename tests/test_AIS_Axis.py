import os,sys                                     
sys.path.append(os.getcwd()) 
import pytest

from OCC.Display.SimpleGui import init_display
from OCC.Core.V3d import V3d_View
from OCC.Core.AIS import (
    AIS_Axis
    
)
from OCC.Core.GC import GC_MakeLine
from RedPanda.Core.Make import make_box, make_line
from RedPanda.Core.Euclid import RP_Pnt, RP_Dir, RP_Vec



display, start, *_ = init_display()
def test_Axis():
    # line = make_line(RP_Pnt(0, 0, 0), RP_Pnt(0, 2, 0))
    line = GC_MakeLine(RP_Pnt(0, 0, 0), RP_Pnt(0, 1, 1)).Value()
    display.Context.Display (AIS_Axis(line), True)
    start()

if __name__ == '__main__':

    display, start, *_ = init_display()
    test_Axis()
    
    
