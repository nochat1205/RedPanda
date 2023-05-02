import os,sys
sys.path.append(os.getcwd())

from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.TopAbs import TopAbs_FACE

if __name__ == '__main__':
    box = BRepPrimAPI_MakeBox(1, 1, 1).Solid()

    builder  = BRepAlgoAPI_Cut(box, box)
    cut = builder.Shape()
    for face in TopologyExplorer(cut).faces():
        print(cut)
