import sys

from PyQt5.QtWidgets import QAction, QStyle, QApplication

from orangecanvas.gui.toolgrid import ToolGrid


def main(argv=[]):
    app = QApplication(argv)

    toolbox = ToolGrid(columns=3)
    icon = app.style().standardIcon(QStyle.SP_FileIcon)
    actions = [
        QAction("A", None, icon=icon),
        QAction("B", None, icon=icon),
        QAction("This one is longer.", icon=icon),
        QAction("Not done yet!", icon=icon),
        QAction("The quick brown fox ... does something I guess", icon=icon),
    ]

    toolbox.addActions(actions)
    toolbox.show()
    return app.exec()

from orangecanvas.gui.tooltree import ToolTree
def main1(argv=[]):
    app = QApplication(argv)

    toolbox = ToolTree()
    icon = app.style().standardIcon(QStyle.SP_FileIcon)
    actions = [
        QAction("A", None, icon=icon),
        QAction("B", None, icon=icon),
        QAction("This one is longer.", icon=icon),
        QAction("Not done yet!", icon=icon),
        QAction("The quick brown fox ... does something I guess", icon=icon),
    ]

    toolbox.addActions(actions)
    toolbox.show()
    return app.exec()

if __name__ == "__main__":
    main1(sys.argv)
