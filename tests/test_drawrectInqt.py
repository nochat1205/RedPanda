from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt
import sys

class MyWidget(QWidget):
    draw_box = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        painter.drawRect(10, 10, 100, 100)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.setGeometry(100, 100, 300, 300)
    widget.show()
    sys.exit(app.exec_())