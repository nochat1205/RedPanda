from RedPanda.RDAF.RD_Label import Label
from OCC.Core.TDF import TDF_Data
if __name__ == '__main__':
    df = TDF_Data()
    root = df.Root()
    aLabel = type(Label)(root)
    print(type(aLabel))
    print(type(root))
