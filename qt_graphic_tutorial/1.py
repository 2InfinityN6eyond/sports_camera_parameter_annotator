from itertools import chain

from posixpath import supports_unicode_filenames
from random import paretovariate
from string import ascii_uppercase
import numpy as np

from PyQt5 import QtWidgets, QtGui, QtCore
from sklearn.metrics import jaccard_score


class GripItem(QtWidgets.QGraphicsPathItem):
    circle = QtGui.QPainterPath()
    circle.addEllipse(QtCore.QRectF(-10, -10, 20, 20))
    square = QtGui.QPainterPath()
    square.addRect(QtCore.QRectF(-15, -15, 30, 30))

    def __init__(self, annotation_item, index):
        super(GripItem, self).__init__()
        self.m_annotation_item = annotation_item
        self.m_index = index

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
        if change == QtWidgets.QGraphicsItem.ItemPositionChange and self.isEnabled():
            self.m_annotation_item.movePoint(self.m_index, value)
        return super(GripItem, self).itemChange(change, value)


class Dragger(QtWidgets.QGraphicsEllipseItem) :
    circle = QtGui.QPainterPath()
    circle.addEllipse(QtCore.QRectF(-10, -10, 20, 20))
    square = QtGui.QPainterPath()
    square.addRect(QtCore.QRectF(-15, -15, 30, 30))
    
    def __init__(self, x, y, w, h, parent, my_id) :
        self.my_parent = parent
        self.my_id = my_id

        super(Dragger, self).__init__(x, y, w, h)


        self.setBrush(QtGui.QColor("green"))
        self.setPen(QtGui.QPen(QtGui.QColor("green"), 2))
     

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(20)

    def hoverEnterEvent(self, event):
        self.setPath(GripItem.square)
        self.setBrush(QtGui.QColor("red"))
        super(GripItem, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPath(GripItem.circle)
        self.setBrush(QtGui.QColor("green"))
        super(GripItem, self).hoverLeaveEvent(event)


    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print("dragger clicked")
        return

        print(event.pos())
        print(event.scenePos())
        print(event.screenPos())

        scene_transform = self.sceneTransform()
        
        print(f"{scene_transform.m11()}, {scene_transform.m12()}, {scene_transform.m13()}")
        print(f"{scene_transform.m21()}, {scene_transform.m22()}, {scene_transform.m23()}")
        print(f"{scene_transform.m31()}, {scene_transform.m32()}, {scene_transform.m33()}")
        print()

        #return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        return
        print(event.pos())
        print(event.scenePos())
        print(event.screenPos())

        prev_mouse_pos = event.lastScenePos()
        curr_mouse_pos = event.scenePos()

        print(curr_mouse_pos.x() - prev_mouse_pos.x())

        m31 = curr_mouse_pos.x() - prev_mouse_pos.x()
        m32 = curr_mouse_pos.y() - prev_mouse_pos.y()
        m33 = 1

        self.translation_m[2, 0] += m31
        self.translation_m[2, 1] += m32

        self.warpItem()

        print()

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print(self.pos())
        print()
        #return super().mouseReleaseEvent(event)


   

class FootballFieldTemplate(QtWidgets.QGraphicsItemGroup) :

    "pitch line annotation follows that of Soccernet"

    def __init__(self, pitch_name = "standard") :

        super(FootballFieldTemplate, self).__init__()

        field_size = {
            "standard" : {
                "width"  : 105,
                "height" : 68
            },
            "etihad_stadium" : {
                "width"  : 106,
                "height" : 70
            },
            "old_trafford" : {
                "width"  : 106,
                "height" : 68
            },
            "anfield" : {
                "width"  : 101,
                "height" : 68
            }
        }

        w = field_size[pitch_name]["width"]
        h = field_size[pitch_name]["height"]
        r = 9.15

        self.big_rect        = QtWidgets.QGraphicsRectItem(0,   0,    w,   h)  # x, y, width, height, 
        self.center_line     = QtWidgets.QGraphicsLineItem(w/2, 0,    w/2, h)
        self.center_circle   = QtWidgets.QGraphicsEllipseItem(w/2-r, h/2-r,   r*2, r*2)
        self.left_penalty    = QtWidgets.QGraphicsRectItem(0,      h/2-20.15,   16.5, 40.3) 
        self.right_penalty   = QtWidgets.QGraphicsRectItem(w-16.5, h/2-20.15,   16.5, 40.3) 
        self.left_goal_area  = QtWidgets.QGraphicsRectItem(0,      h/2-9.16,    5.5,  18.32) 
        self.right_goal_area = QtWidgets.QGraphicsRectItem(w-5.5,  h/2-9.16,    5.5,  18.32)  
        self.left_arc        = QtWidgets.QGraphicsEllipseItem(11-r,   h/2-r,      r*2, r*2)
        self.right_arc       = QtWidgets.QGraphicsEllipseItem(w-11-r, h/2-r,      r*2, r*2)


        self.dragger_1 = Dragger(0, 0, 3, 3, self, 1)
        self.dragger_2 = Dragger(w/2, 0, 3, 3, self, 2)

        #self.addToGroup(self.dragger_1)
        #self.addToGroup(self.dragger_2)


        angle = np.arccos(5.5 / 9.15).item()
        angle = int(np.rad2deg(np.arccos(5.5 / 9.15)))

        #self.left_arc.setStartAngle(-angle)
        #self.left_arc.setSpanAngle(angle)

        #self.right_arc.setStartAngle(-angle)
        #self.right_arc.setSpanAngle(angle)

        self.addToGroup(self.big_rect)
        self.addToGroup(self.center_line)
        self.addToGroup(self.center_circle)
        self.addToGroup(self.left_arc)
        self.addToGroup(self.right_arc)
        self.addToGroup(self.left_penalty)
        self.addToGroup(self.right_penalty)
        self.addToGroup(self.left_goal_area)
        self.addToGroup(self.right_goal_area)


        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)


        self.setAcceptTouchEvents(True)
        #self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        #self.setFlag(QtWidgets.QGraphicsItem.)

        self.setZValue(10)

        self.homography = np.array([
            [1,   0.1, 0.001],
            [0.1, 1,   0],
            [0.2, 0,   1]
        ])

        self.translation_m = np.array([
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ])
        self.translation_m = np.eye(3)
        self.scale = 2
        self.rotation = 0 # radian

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print(event.pos())
        print(event.scenePos())
        print(event.screenPos())

        scene_transform = self.sceneTransform()
        
        print(f"{scene_transform.m11()}, {scene_transform.m12()}, {scene_transform.m13()}")
        print(f"{scene_transform.m21()}, {scene_transform.m22()}, {scene_transform.m23()}")
        print(f"{scene_transform.m31()}, {scene_transform.m32()}, {scene_transform.m33()}")
        print()

        #return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print(event.pos())
        print(event.scenePos())
        print(event.screenPos())

        prev_mouse_pos = event.lastScenePos()
        curr_mouse_pos = event.scenePos()

        print(curr_mouse_pos.x() - prev_mouse_pos.x())

        m31 = curr_mouse_pos.x() - prev_mouse_pos.x()
        m32 = curr_mouse_pos.y() - prev_mouse_pos.y()
        m33 = 1

        self.translation_m[2, 0] += m31
        self.translation_m[2, 1] += m32

        self.warpItem()

        print()

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print(self.pos())
        print()
        #return super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        print("mouse entered to annotation")
        return super().hoverEnterEvent(event)

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        return super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        print("mouse leaved from annotation")

    
    def dragEnterEvent(self, event: 'QGraphicsSceneDragDropEvent') -> None:
        print("drag entered")

    def dragMoveEvent(self, event: 'QGraphicsSceneDragDropEvent') -> None:
        print("dragging")

    def dragLeaveEvent(self, event: 'QGraphicsSceneDragDropEvent') -> None:
        print("drag stopped")


    def gethomography(self) :
        pass

    def warpItem(self) :
        homography = np.eye(3) * self.scale
        homography = np.matmul(homography, self.translation_m)
        homography = np.matmul(homography, self.homography)
        self.setTransform(QtGui.QTransform(
            homography[0, 0], homography[0, 1], homography[0, 2],
            homography[1, 0], homography[1, 1], homography[1, 2],
            homography[2, 0], homography[2, 1], homography[2, 2],
        ))

    def applyHomgraphyTransform(self) :
        self.setTransform(QtGui.QTransform(
            self.homography[0, 0], self.homography[0, 1], self.homography[0, 2],
            self.homography[1, 0], self.homography[1, 1], self.homography[1, 2],
            self.homography[2, 0], self.homography[2, 1], self.homography[2, 2],
        ))

    def applyTransform(self, m11=1, m12=0, m13=0, m21=0, m22=1, m23=0, m31=0, m32=0, m33=1) :

        print(f"{m11:4} {m12:4} {m13:4}")
        print(f"{m21:4} {m22:4} {m23:4}")
        print(f"{m31:4} {m32:4} {m33:4}")

        self.setTransform(QtGui.QTransform(
            m11, m12, m13,
            m21, m22, m23,
            m31, m32, m33
        ))

    def sampleTransform(self) :

        self.setTransformOriginPoint(0, 0)
        self.setTransform(QtGui.QTransform(
            1,   0,   0,
            0,   1,   1,
            0,   0,   1
        ))

class AnnotatorGraphicsScene(QtWidgets.QGraphicsScene) :
    def __init__(self, parent = None) :
        super(AnnotatorGraphicsScene, self).__init__(parent)

        self.image_item = QtWidgets.QGraphicsPixmapItem()
        self.image_item.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

        self.addItem(self.image_item)

        self.plotAxis()
        
    def plotAxis(self) :
        x_axis = QtWidgets.QGraphicsLineItem(-1000, 0,       1000, 0)
        y_axis = QtWidgets.QGraphicsLineItem(0,     -1000,   0,    1000)
        self.addItem(x_axis)
        self.addItem(y_axis)

    def loadImage(self, image_path) :
        self.image_item.setPixmap(QtGui.QPixmap(image_path))
        self.setSceneRect()



class AnnotatorGraphicsView(QtWidgets.QGraphicsView) :

    def __init__(self, parent = None) :
        super(AnnotatorGraphicsView, self).__init__(parent)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setMouseTracking(True)

        self.shortcut_zoom_factor = 2.0

        QtWidgets.QShortcut(QtGui.QKeySequence.ZoomIn,  self, activated = self.zoomIn)
        QtWidgets.QShortcut(QtGui.QKeySequence.ZoomOut, self, activated = self.zoomOut)

        #self.setSceneRect(0, 0, 2000, 2000)


        #self.dragMoveEvent()
        #self.mo

        self.startPos = None

    @QtCore.pyqtSlot()
    def zoomIn(self):
        self.setZoomLevel(self.shortcut_zoom_factor)

    @QtCore.pyqtSlot()
    def zoomOut(self):
        self.setZoomLevel(1 / self.shortcut_zoom_factor)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        if event.angleDelta().y() > 0 :
            self.setZoomLevel(1.2)
        elif event.angleDelta().y() < 0 :
            self.setZoomLevel(0.8)

    def setZoomLevel(self, f):
        self.scale(f, f)
        #if self.scene() is not None:
        #    self.centerOn(self.scene().image_item)

    """
    # vvvvv   for dragging qgraphicsscene   vvvvv
    def mousePressEvent(self, event):
        
        #if event.modifiers() & QtCore.Qt.ControlModifier and event.button() == QtCore.Qt.LeftButton:
        if event.button() == QtCore.Qt.LeftButton:

            # store the origin point
            self.startPos = event.pos()

    def mouseMoveEvent(self, event):
        if self.startPos is not None:
            # compute the difference between the current cursor position and the
            # previous saved origin point
            delta = self.startPos - event.pos()
            # get the current transformation (which is a matrix that includes the
            # scaling ratios
            transform = self.transform()
            # m11 refers to the horizontal scale, m22 to the vertical scale;
            # divide the delta by their corresponding ratio
            deltaX = delta.x() / transform.m11()
            deltaY = delta.y() / transform.m22()
            # translate the current sceneRect by the delta
            self.setSceneRect(self.sceneRect().translated(deltaX, deltaY))
            # update the new origin point to the current position
            self.startPos = event.pos()

    def mouseReleaseEvent(self, event):
        self.startPos = None
    """

class MainWindow(QtWidgets.QMainWindow) :
    def __init__(self) :
        super(MainWindow, self).__init__()


        main_layout = QtWidgets.QHBoxLayout()

        exec_layout = QtWidgets.QVBoxLayout()

        self.text_edit = QtWidgets.QTextEdit()
        self.exec_button = QtWidgets.QPushButton("exec")
        self.exec_button.clicked.connect(self.execButtonCliked)


        self.graphics_view = AnnotatorGraphicsView()
        self.graphics_scene = AnnotatorGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)

        self.graphics_scene.addItem(FootballFieldTemplate())

        #self.football_field_template = FootballFieldTemplate()
        #self.football_field_template.sampleTransform()

        #self.graphics_scene.addItem(self.football_field_template)

        #self.setCentralWidget(self.graphics_view)
 
        exec_layout.addWidget(self.text_edit)
        exec_layout.addWidget(self.exec_button)

        main_layout.addLayout(exec_layout)
        main_layout.addWidget(self.graphics_view)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def execButtonCliked(self) :
        try :
            text = self.text_edit.toPlainText()
            exec(text)
        except :
            print("ERROR..")

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resize(640, 480)
    w.show()
    sys.exit(app.exec_())

