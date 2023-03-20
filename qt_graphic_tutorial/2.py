import numpy as np

from PyQt5 import QtWidgets, QtGui, QtCore
from sklearn.metrics import jaccard_score


class GripItem(QtWidgets.QGraphicsPathItem):
    circle = QtGui.QPainterPath()
    circle.addEllipse(QtCore.QRectF(-10, -10, 20, 20))
    square = QtGui.QPainterPath()
    square.addRect(QtCore.QRectF(-15, -15, 30, 30))

    def __init__(self):
        super(GripItem, self).__init__()

        self.setPath(GripItem.circle)
        self.setBrush(QtGui.QColor("green"))
        self.setPen(QtGui.QPen(QtGui.QColor("green"), 2))
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(11)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def hoverEnterEvent(self, event):
        self.setPath(GripItem.square)
        self.setBrush(QtGui.QColor("red"))
        super(GripItem, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPath(GripItem.circle)
        self.setBrush(QtGui.QColor("green"))
        super(GripItem, self).hoverLeaveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setSelected(False)
        super(GripItem, self).mouseReleaseEvent(event)

    def itemChange(self, change, value):
        pass

class MainWindow(QtWidgets.QMainWindow) :
    def __init__(self) :

        super(MainWindow, self).__init__()
        
        self.graphics_view = QtWidgets.QGraphicsView()
        self.graphics_scene = QtWidgets.QGraphicsScene()

        self.item1 = GripItem()

        self.graphics_scene.addItem(self.item1)
        self.plotAxis()

        self.graphics_view.setScene(self.graphics_scene)

        self.setCentralWidget(self.graphics_view)
        

        
    def plotAxis(self) :
        x_axis = QtWidgets.QGraphicsLineItem(-1000, 0,       1000, 0)
        y_axis = QtWidgets.QGraphicsLineItem(0,     -1000,   0,    1000)
        self.graphics_scene.addItem(x_axis)
        self.graphics_scene.addItem(y_axis)

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resize(640, 480)
    w.show()
    sys.exit(app.exec_())