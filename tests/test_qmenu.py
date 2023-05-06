import os,sys
sys.path.append(os.getcwd()) 


from PyQt5.QtWidgets import QMenu, QAction, QApplication
from PyQt5.QtCore import Qt

from RedPanda.widgets.Logic_Viewer import qtViewer3d

# Define a slot function to handle the context menu request
def showContextMenu(point):
    # Create a context menu
    menu = QMenu(viewer)

    # Create an action for the menu
    action = QAction("Example Action", viewer)
    menu.addAction(action)

    # Show the menu at the requested position
    menu.exec_(viewer.mapToGlobal(point))



# Start the Qt event loop
app = QApplication([])

# Create a qtViewer3d widget
viewer:qtViewer3d = qtViewer3d()
viewer.show()
app.exec_()
