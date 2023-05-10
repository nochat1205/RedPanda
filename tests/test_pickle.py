import os,sys
sys.path.append(os.getcwd())
import pickle

from OCC.Display.SimpleGui import init_display
from RedPanda.Core.Make import make_box
def test_topo():
    display, start, *_ = init_display()
    box = make_box(10, 10, 10)
    with open('a.rpbin', 'wb+') as f:
        pickle.dump(box, f)
    
    with open('a.rpbin', 'rb') as f:
        b2 = pickle.load(f)
    display.DisplayShape(b2)
    start()

if __name__ == '__main__':
    test_topo()
