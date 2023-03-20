from itertools import chain
import copy

import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore


class FootballFieldTemplate(QtWidgets.QGraphicsItemGroup) :

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
        self.big_rect        = QtWidgets.QGraphicsRectItem(   0,      0,          w,    h,     parent=self)
        self.center_line     = QtWidgets.QGraphicsLineItem(   w/2,    0,          w/2,  h,     parent=self)
        self.center_circle   = QtWidgets.QGraphicsEllipseItem(w/2-r,  h/2-r,      r*2,  r*2,   parent=self)
        self.left_penalty    = QtWidgets.QGraphicsRectItem(   0,      h/2-20.15,  16.5, 40.3,  parent=self)
        self.right_penalty   = QtWidgets.QGraphicsRectItem(   w-16.5, h/2-20.15,  16.5, 40.3,  parent=self) 
        self.left_goal_area  = QtWidgets.QGraphicsRectItem(   0,      h/2-9.16,   5.5,  18.32, parent=self) 
        self.right_goal_area = QtWidgets.QGraphicsRectItem(   w-5.5,  h/2-9.16,   5.5,  18.32, parent=self)  
        self.left_arc        = QtWidgets.QGraphicsEllipseItem(11-r,   h/2-r,      r*2,  r*2,   parent=self)
        self.right_arc       = QtWidgets.QGraphicsEllipseItem(w-11-r, h/2-r,      r*2,  r*2,   parent=self)

        self.addToGroup(self.big_rect)
        self.addToGroup(self.center_line)
        self.addToGroup(self.center_circle)
        self.addToGroup(self.left_arc)
        self.addToGroup(self.right_arc)
        self.addToGroup(self.left_penalty)
        self.addToGroup(self.right_penalty)
        self.addToGroup(self.left_goal_area)
        self.addToGroup(self.right_goal_area)

        self.intersection_points = [
            [0,  0],
            [0 + w,  0],
            [0,  0 + h],
            [0 + w,  0 + h],

            [w/2,  0],
            [w/2 + w/2,  0],
            [w/2,  0 + h],
            [w/2 + w/2,  0 + h],

            [w/2-r,  h/2-r],
            [w/2-r + r*2,  h/2-r],
            [w/2-r,  h/2-r + r*2],
            [w/2-r + r*2,  h/2-r + r*2],

            [0,  h/2-20.15],
            [0 + 16.5,  h/2-20.15],
            [0,  h/2-20.15 + 40.3],
            [0 + 16.5,  h/2-20.15 + 40.3],

            [w-16.5,  h/2-20.15],
            [w-16.5 + 16.5,  h/2-20.15],
            [w-16.5,  h/2-20.15 + 40.3],
            [w-16.5 + 16.5,  h/2-20.15 + 40.3],

            [0,  h/2-9.16],
            [0 + 5.5,  h/2-9.16],
            [0,  h/2-9.16 + 18.32],
            [0 + 5.5,  h/2-9.16 + 18.32],

            [w-5.5,  h/2-9.16],
            [w-5.5 + 5.5,  h/2-9.16],
            [w-5.5,  h/2-9.16 + 18.32],
            [w-5.5 + 5.5,  h/2-9.16 + 18.32],

            [w/2, h/2-r ],
            [w/2, h/2+r],
            [16.5, h/2-7.312489316231512],
            [16.5, h/2+7.312489316231512],
            [w-16.5, h/2-7.312489316231512],
            [w-16.5, h/2+7.312489316231512]
        ]

        self.intersection_points = np.array(list(map(
            lambda x : np.array(x + [1]).reshape(-1, 1),
            self.intersection_points
        )))
        self.intersection_point_icons = [
            QtWidgets.QGraphicsEllipseItem(
                point[0] - 1,
                point[1] - 1,
                2,
                2
            ) for point in self.intersection_points
        ]
        list(map(self.addToGroup, self.intersection_point_icons))
        self.last_4_edited_points = [0, 1, 2, 3]
        self.intersection_point_r = 1

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptTouchEvents(True)
        self.setAcceptHoverEvents(True)
        self.setZValue(10)

        self.homography_m = np.eye(3)
        self.translation_m = np.eye(3)
        self.scale = 1
        self.rotation = 0 # radian

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        print(event.pos(), event.scenePos())

    def getDistance(self, p1:np.ndarray, p2:np.ndarray) :
        return np.sqrt(np.sum(np.square(p1 - p2)))

    def printTransform(self) :
        scene_transform = self.sceneTransform()
        print(f"{scene_transform.m11()}, {scene_transform.m12()}, {scene_transform.m13()}")
        print(f"{scene_transform.m21()}, {scene_transform.m22()}, {scene_transform.m23()}")
        print(f"{scene_transform.m31()}, {scene_transform.m32()}, {scene_transform.m33()}")
        print()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.start_pos = event.scenePos()
        self.intersection_clicked = False


        mouse_pose = np.array([
            [event.scenePos().x()],
            [event.scenePos().y()],
            [1]
        ])

        homography = self.getTransformArray()
        intersection_transformed = np.matmul(homography, self.intersection_points)

        for i in range(len(intersection_transformed)) :

            if self.getDistance(
                mouse_pose,
                intersection_transformed[i]
            ) < self.intersection_point_r :
                if i not in self.last_4_edited_points :
                    self.last_4_edited_points.pop()
                    self.last_4_edited_points.insert(0, i)
                print("intersection point clicked")
                print(self.last_4_edited_points)

                self.intersection_clicked = True

                self.initial_last_4_points_poses = np.matmul(
                    self.getTransformArray(),
                    self.intersection_points[self.last_4_edited_points]
                )

                break

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

        prev_mouse_pos = event.lastScenePos()
        curr_mouse_pos = event.scenePos()

        homography = self.getTransformArray()
        mouse_pose = np.array([
            [event.scenePos().x()],
            [event.scenePos().y()],
            [1]
        ])
        
        last_4_points_local  = self.intersection_points[self.last_4_edited_points]
        last_4_points_global = np.matmul(
            homography,
            self.intersection_points[self.last_4_edited_points]
        )

        #print(last_4_points_local[:,  :-1].squeeze().transpose())
        print(last_4_points_global[:, :-1].squeeze().transpose())

        
        if self.intersection_clicked :
            print("intersection editing") 
            #last_4_points_global = self.initial_last_4_points_poses

            last_4_points_global[0] = mouse_pose
        else :
            print("translating")
            last_4_points_global[:,0,:] += curr_mouse_pos.x() - prev_mouse_pos.x()
            last_4_points_global[:,1,:] += curr_mouse_pos.y() - prev_mouse_pos.y()

            
        print(last_4_points_global[:, :-1].squeeze().transpose())
        print()
        print((last_4_points_global - np.matmul(self.getTransformArray(), last_4_points_local))[:, :-1].squeeze().transpose())

   
        self.homography_m = self.resolveHomography(last_4_points_local, last_4_points_global).transpose()
        self.warpItem()

        print()


    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.intersection_clicked :        
            pass
            """
            mouse_pose = np.array([
                [event.scenePos().x()],
                [event.scenePos().y()],
                [1]
            ])
            last_4_points_local = self.intersection_points[self.last_4_edited_points]
            last_4_points_global = np.matmul(
                self.getTransformArray(),
                self.intersection_points[self.last_4_edited_points]
            )
            last_4_points_global[0] = mouse_pose

            self.homography_m = self.resolveHomography(last_4_points_local, last_4_points_global)
            self.warpItem()
            """
        self.intersection_clicked = False



    def warpItem(self) :
        homography_m = self.homography_m.transpose()
        self.setTransform(QtGui.QTransform(
            homography_m[0, 0], homography_m[0, 1], homography_m[0, 2],
            homography_m[1, 0], homography_m[1, 1], homography_m[1, 2],
            homography_m[2, 0], homography_m[2, 1], homography_m[2, 2],
        ))

    def applyHomgraphyTransform(self) :
        self.setTransform(QtGui.QTransform(
            self.homography_m[0, 0], self.homography_m[0, 1], self.homography_m[0, 2],
            self.homography_m[1, 0], self.homography_m[1, 1], self.homography_m[1, 2],
            self.homography_m[2, 0], self.homography_m[2, 1], self.homography_m[2, 2],
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

    def getTransformArray(self) :
        scene_transform = self.transform()
        return np.array([
            [scene_transform.m11(), scene_transform.m21(), scene_transform.m31()],
            [scene_transform.m12(), scene_transform.m22(), scene_transform.m32()],
            [scene_transform.m13(), scene_transform.m23(), scene_transform.m33()]
        ])

    def resolveHomography(self, pts_src, pts_dst) :
        
        pts_src = list(map(
            lambda x : np.squeeze(x),
            np.split(pts_src, 4)
        ))
        pts_dst = list(map(
            lambda x : np.squeeze(x),
            np.split(pts_dst, 4)
        ))
        zeros = np.zeros(3)

        P = np.vstack(list(map(
            lambda p_src, p_dst : np.stack(
                (
                    np.concatenate((p_src*-1, zeros, p_src*p_dst[0])),
                    np.concatenate((zeros, p_src*-1, p_src*p_dst[1]))
                )
            ),
            pts_src, pts_dst
        )))

        [U, S, Vt] = np.linalg.svd(P)
        homography = Vt[-1].reshape(3, 3)
        return homography / homography[2][2]






    def __resolveHomography(self, pts_src:np.ndarray, pts_dst:np.ndarray) :
        
        A = []
        b = []
        for i in range(4):
            s_x, s_y = pts_src[i][0][0], pts_src[i][1][0] #source[i]
            d_x, d_y = pts_dst[i][0][0], pts_dst[i][1][0] #destination[i]
            A.append([s_x, s_y, 1, 0, 0, 0, (-d_x)*(s_x), (-d_x)*(s_y)])
            A.append([0, 0, 0, s_x, s_y, 1, (-d_y)*(s_x), (-d_y)*(s_y)])
            b += [d_x, d_y]
        A = np.array(A)
        h = np.linalg.lstsq(A, b)[0]
        h = np.concatenate((h, [1]), axis=-1)
        return np.reshape(h, (3, 3)).transpose()

    def j_resolveHomography(self, src, dst) :

        print("src:")
        print(src, "\n")
        print("dst:")
        print(dst, "\n")


        x_1 = [src[0][0][0], dst[0][0][0]]
        y_1 = [src[0][1][0], dst[0][1][0]]
        x_2 = [src[1][0][0], dst[1][0][0]]
        y_2 = [src[1][1][0], dst[1][1][0]]
        x_3 = [src[2][0][0], dst[2][0][0]]
        y_3 = [src[2][1][0], dst[2][1][0]]
        x_4 = [src[3][0][0], dst[3][0][0]]
        y_4 = [src[3][1][0], dst[3][1][0]]

        print(x_1)
        print(y_1)
        print(x_2)
        print(y_2)
        print(x_3)
        print(y_3)
        print(x_4)
        print(y_4)
        

        P = np.array([
            [-x_1[0], -y_1[0], -1, 0, 0, 0, x_1[0]*x_1[1], y_1[0]*x_1[1], x_1[1]],
            [0, 0, 0, -x_1[0], -y_1[0], -1, x_1[0]*y_1[1], y_1[0]*y_1[1], y_1[1]],
            [-x_2[0], -y_2[0], -1, 0, 0, 0, x_2[0]*x_2[1], y_2[0]*x_2[1], x_2[1]],
            [0, 0, 0, -x_2[0], -y_2[0], -1, x_2[0]*y_2[1], y_2[0]*y_2[1], y_2[1]],
            [-x_3[0], -y_3[0], -1, 0, 0, 0, x_3[0]*x_3[1], y_3[0]*x_3[1], x_3[1]],
            [0, 0, 0, -x_3[0], -y_3[0], -1, x_3[0]*y_3[1], y_3[0]*y_3[1], y_3[1]],
            [-x_4[0], -y_4[0], -1, 0, 0, 0, x_4[0]*x_4[1], y_4[0]*x_4[1], x_4[1]],
            [0, 0, 0, -x_4[0], -y_4[0], -1, x_4[0]*y_4[1], y_4[0]*y_4[1], y_4[1]],
            ])

        [U, S, Vt] = np.linalg.svd(P)
        homography = Vt[-1].reshape(3, 3)
        return homography
        transformedPoint = homography @ np.array([1679,  128, 1]).transpose()
        print(transformedPoint/transformedPoint[-1]) # will be ~[4, 7, 1]



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
        factor = 1
        if event.angleDelta().y() > 0 :
            factor = 1.2
            self.setZoomLevel(1.2)
        elif event.angleDelta().y() < 0 :
            factor = 0.8
            self.setZoomLevel(0.8)
        

        return 

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

        self.graphics_scene.addItem(FootballFieldTemplate())

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



