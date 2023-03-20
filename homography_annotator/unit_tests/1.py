import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

class MainWindow(QtWidgets.QMainWindow) :
    def __init__(self, parent = None) :
        super(MainWindow, self).__init__()'
        


if __name__ == "__main__" :
    app = QtWidgets.QApplication(sys.argv)
    
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())