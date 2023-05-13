
from OCC.Core.TPrsStd import (
    TPrsStd_Driver, TPrsStd_AISPresentation,
    TPrsStd_NamedShapeDriver   
)
from OCC.Core.TDF import TDF_Data
from OCC.Core.TNaming import TNaming_Builder

from RedPanda.RPAF.DataDriver import BoxDriver
from RedPanda.RPAF.DriverTable import TPrsStd_DriverTable

if __name__ == '__main__':
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
    table = TPrsStd_DriverTable.Get()
    table.AddDriver(BoxDriver.ID, TPrsStd_NamedShapeDriver())

    df = TDF_Data()
    aLabel = df.Root()

    box = BRepPrimAPI_MakeBox(1, 2, 1).Shape()
    builder = TNaming_Builder(aLabel)
    builder.Generated(box)

    prs = TPrsStd_AISPresentation.Set(aLabel, BoxDriver.ID)
    prs.Update()
    ais = prs.GetAIS()
    print(ais)

    from OCC.Display.SimpleGui import init_display
    display, start_display, *_ = init_display()
    display.Context.Display(ais, True)
    display.FitAll()
    start_display()
