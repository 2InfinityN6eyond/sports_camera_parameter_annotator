from itertools import chain

from posixpath import supports_unicode_filenames
from random import paretovariate
from string import ascii_uppercase
import numpy as np

from PyQt5 import QtWidgets, QtGui, QtCore
from sklearn.metrics import jaccard_score

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
        
        print("dragger movved")
        print(event.pos())
        print(event.scenePos())
        print(event.screenPos())

        prev_mouse_pos = event.lastScenePos()
        curr_mouse_pos = event.scenePos()

        print(curr_mouse_pos.x() - prev_mouse_pos.x())
        return 

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


   

class FootballFieldTemplate(QtWidgets.QGraphicsRectItem) :

    "pitch line annotation follows that of Soccernet"

    field_size = {
        "boundary" : {
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
        },
        "circle_radius"      : 9.15,
        "penalty_box_width"  : 16.5,
        "penalty_box_height" : 40.3,
        "goal_area_width"    : 5.5,
        "goal_area_height"   : 18.32
    }

    def __init__(self, parent = None, pitch_name = "standard") :

        super(FootballFieldTemplate, self).__init__()

        self.parent = parent
        w = FootballFieldTemplate.field_size["boundary"][pitch_name]["width"]
        h = FootballFieldTemplate.field_size["boundary"][pitch_name]["height"]
        r = 9.15

        self.setRect(0,   0,    w,   h)  # x, y, width, height, 

        self.center_line     = QtWidgets.QGraphicsLineItem(w/2, 0,    w/2, h, parent=self)
        self.center_circle   = QtWidgets.QGraphicsEllipseItem(w/2-r, h/2-r,   r*2, r*2, parent=self)
        self.left_penalty    = QtWidgets.QGraphicsRectItem(0,      h/2-20.15,   16.5, 40.3, parent=self)
        self.right_penalty   = QtWidgets.QGraphicsRectItem(w-16.5, h/2-20.15,   16.5, 40.3, parent=self) 
        self.left_goal_area  = QtWidgets.QGraphicsRectItem(0,      h/2-9.16,    5.5,  18.32, parent=self) 
        self.right_goal_area = QtWidgets.QGraphicsRectItem(w-5.5,  h/2-9.16,    5.5,  18.32, parent=self)  
        self.left_arc        = QtWidgets.QGraphicsEllipseItem(11-r,   h/2-r,      r*2, r*2, parent=self)
        self.right_arc       = QtWidgets.QGraphicsEllipseItem(w-11-r, h/2-r,      r*2, r*2, parent=self)

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
        return 
        print(event.pos())
        print(event.scenePos())
        print(event.screenPos())

        prev_mouse_pos = event.lastScenePos()
        curr_mouse_pos = event.scenePos()

        print(curr_mouse_pos.x() - prev_mouse_pos.x())

        self.parent.templateDragged(curr_mouse_pos - prev_mouse_pos)

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


class FootballFieldAnnotation(QtWidgets.QGraphicsItemGroup) :
    def __init__(self) :
        super(FootballFieldAnnotation, self).__init__()

        w = 105
        h = 68
        r = 9.15


        self.football_field_template = FootballFieldTemplate(self)

        self.dragger_1 = Dragger(0,   0,  2, 2, self, 0)
        self.dragger_2 = Dragger(105, 0,  2, 2, self, 1)
        self.dragger_3 = Dragger(0,   68, 2, 2, self, 2)
        self.dragger_4 = Dragger(105, 68, 2, 2, self, 3)
        #parent=self)self.dragger_1 = Dragger(, 0, 2, 2, self, 0)
        #parent=self)self.dragger_1 = Dragger(0, 0, 2, 2, self, 0)
        #parent=self)self.dragger_1 = Dragger(0, 0, 2, 2, self, 0)
        #parent=self)self.dragger_1 = Dragger(0, 0, 2, 2, self, 0)

        self.addToGroup(self.football_field_template)
        self.addToGroup(self.dragger_1)
        self.addToGroup(self.dragger_2)
        self.addToGroup(self.dragger_3)
        self.addToGroup(self.dragger_4)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)

        self.setHan
        

    def draggerDragged(self, idx, d_pos) :
        print("dragger dragged")
        print(idx, d_pos.x(), d_pos.y())    

    def templateDragged(self, d_pos) :
        print("template dragged")
        print(d_pos.x(), d_pos.y())



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

        self.graphics_scene.addItem(FootballFieldAnnotation())


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