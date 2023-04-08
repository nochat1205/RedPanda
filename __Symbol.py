import typing
from PyQt5.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QSizePolicy, QApplication, QStyle, QTreeWidgetItem,
    QSplitter, QSplitterHandle, QPushButton, QStatusBar, QToolBar, QTreeWidget, QComboBox,
    QProgressBar, QAction, QFrame, QStyleOption, QHBoxLayout, QMenuBar, QMenu,
    QWIDGETSIZE_MAX
)
from PyQt5.QtCore import (
    Qt, QObject, QEvent, QRect, QMargins, QByteArray, QDataStream, QBuffer,
    QSettings, QUrl, QThread, QTimer, QSize, QPoint, QLine, 
    pyqtSignal as Signal
)
from PyQt5.QtGui import (
    QIcon, QKeySequence, QDesktopServices, QPainter, QColor, QPen, QKeyEvent,
    QActionEvent
)


from RedPanda.utils.widgetpreview import WidgetPreview
from RedPanda.widgets.gui import UiFactory

class Test(QDialog):
    buttons_area_orientation = Qt.Horizontal

    def __init__(self, parent: typing.Optional[QWidget]=None, *args, **kwargs) -> None:
        super().__init__(parent,  *args, **kwargs)
        self.resizing_enabled = True
        self.isShape = True
        self.want_control_area = True
        self.want_main_area = True
        
        self.setup_ui()

    def setup_ui(self):
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(2, 2, 2, 2)
        if not self.resizing_enabled:
            self.layout().setSizeConstraint(QVBoxLayout.SetFixedSize)

        self._create_default_buttons()
        self._insert_splitter()
        if self.want_control_area:
            self._insert_control_area()
        if self.want_main_area:
            self._insert_main_area()

    def _insert_control_area(self):
        self.left_side = UiFactory.vBox(self.__splitter, spacing=0)
        if self.want_main_area:
            self.left_side.setSizePolicy(
                QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

            scroll_area = UiFactory.VerticalScrollArea(self.left_side)
            scroll_area.setSizePolicy(QSizePolicy.MinimumExpanding,
                                      QSizePolicy.Preferred)
            self.controlArea = UiFactory.vBox(scroll_area, spacing=6,
                                        sizePolicy=(QSizePolicy.MinimumExpanding,
                                                    QSizePolicy.Preferred))
            scroll_area.setWidget(self.controlArea)

            self.left_side.layout().addWidget(scroll_area)

            m = 4, 4, 0, 4
        else:
            self.controlArea = UiFactory.vBox(self.left_side, spacing=6)

            m = 4, 4, 4, 4

        if self.buttons_area_orientation is not None:
            self._insert_buttons_area()
            self.buttonsArea.layout().setContentsMargins(
                m[0] + 8, m[1], m[2] + 8, m[3]
            )
            # margins are nice on macOS with this
            m = m[0], m[1], m[2], m[3] - 2

        self.controlArea.layout().setContentsMargins(*m)

    def _insert_buttons_area(self):
        if not self.want_main_area:
            UiFactory.separator(self.left_side)
        self.buttonsArea = UiFactory.widgetBox(
            self.left_side, spacing=6,
            orientation=self.buttons_area_orientation,
            sizePolicy=(QSizePolicy.MinimumExpanding,
                        QSizePolicy.Maximum)
        )

    def _insert_main_area(self):
        pass

    def _insert_splitter(self):
        self.__splitter = QSplitter(Qt.Horizontal, self)
        self.layout().addWidget(self.__splitter)

    def _create_default_buttons(self):
        # These buttons are inserted in buttons_area, if it exists
        # Otherwise it is up to the widget to add them to some layout
        if self.isShape:
            self.graphButton = QPushButton("&Save Shape", autoDefault=False)
            self.graphButton.clicked.connect(self.save_shape)

        # if hasattr(self, "send_report"):

    def save_shape(self):
        pass

import sys
class TreeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(['名称', '类型', '值'])

        item1 = QTreeWidgetItem(self.tree, ['Item 1', 'ComboBox', ''])
        combo_box = QComboBox(self.tree)
        combo_box.addItems(['Option 1', 'Option 2', 'Option 3'])
        self.tree.setItemWidget(item1, 2, combo_box)

        item2 = QTreeWidgetItem(self.tree, ['Item 2', 'Text', 'Text Value'])

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = TreeWidget()
    widget.show()
    sys.exit(app.exec_())
