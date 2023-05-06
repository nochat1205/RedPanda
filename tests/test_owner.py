import os,sys
sys.path.append(os.getcwd())

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.AIS import AIS_Shape

from RedPanda.RPAF.RD_Label import Label
from RedPanda.RPAF.SelectOwner import SelectOwner

if __name__ == '__main__':
    box = BRepPrimAPI_MakeBox(10, 10, 10).Shape()
    ais = AIS_Shape(box)
    label = Label()

    # owner0 = ais.GetOwner()
    # book = dict()
    # book[owner0] = label
    # print(book[owner0])
    print(hash(box))
    print(hash(ais.Shape()))

    box = BRepPrimAPI_MakeBox(10, 20, 10).Shape()
    print(f'ais:{hash(ais)}')
    print(hash(box))

    ais.SetShape(box)

    print(hash(ais))

