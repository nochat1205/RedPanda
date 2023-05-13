from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display
from OCC.Extend.ShapeFactory import points_to_bspline

def decorator_run(fun):
    def decorated_fun(*args, **kwargs):
        print(f'Before {fun.__name__}')
        shape = fun(*args, **kwargs)
        print(f'end {fun.__name__}')
        return shape 
    return decorated_fun

@decorator_run
def test_bezier0():
    p = gp_Pnt()
    try:
        line = points_to_bspline([p, p, p])
    except Exception as eror:
        print(eror)
    return line

if __name__ == '__main__':
    display, start, *_ = init_display()
    line = test_bezier0()
    display.DisplayShape(line)
    start()
