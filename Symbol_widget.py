
from tests.preview_widget import WidgetPreview



def Text_qt2d():
    # Application()
    from RedPanda.widgets.Logic_viewer2d import qtViewer2d
    from RedPanda.Core.Make import make_plane, make_box
    previewer = WidgetPreview(qtViewer2d)
    # previewer.widget.Run(Sym_NewBuilder(BoxDriver()))
    face = make_plane()
    box = make_box(1, 1, 1)
    widget:qtViewer2d = previewer.widget
    widget.Display_Plane(face)
    widget._display.DisplayShape(box)
    previewer.run()

def Text_LabelView():
    from RedPanda.widgets.Logic_LabelView import LabelView
    from RedPanda.Sym_ParamBuilder import Sym_NewBuilder
    from RedPanda.RPAF.DataDriver.Geom2dDriver import EllipseDriver
    from RedPanda.RPAF.Application import Application
    app = Application()
    previewer = WidgetPreview(LabelView)
    previewer.widget.Run(Sym_NewBuilder(EllipseDriver()))
    previewer.widget.Test()
    previewer.run()

if __name__ == '__main__':
    Text_LabelView()

