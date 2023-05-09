from PyQt5.QtWidgets import QTableWidget, QPlainTextEdit, QApplication,QTableWidgetItem



app = QApplication([])

widget = QTableWidget()
widget.setColumnCount(2)
widget.setRowCount(2)

str='\r\na\r\n'

widget.setCellWidget(1, 1, QPlainTextEdit(str))

widget.show()
app.exec()