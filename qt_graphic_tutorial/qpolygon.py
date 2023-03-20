from itertools import chain
import copy

import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore


class FootballFieldTemplate(QtWidgets.QGraphicsPolygonItem) :

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


    def drawFootBallField(self) :

        template_transformed = np.matmul(self.homography_m, self.template_origin)
        template_transformed = self.setHomogeniouseCoordScale(template_transformed)

        list(map(
            lambda icon, point : icon.setRect(
                point[0] - self.point_r,
                point[1] - self.point_r,
                self.point_r * 2,
                self.point_r * 2,
            ),
            self.last_4_edited_icons,
            template_transformed[self.last_4_edited_points_idx]
        ))

        self.setPolygon(
            QtGui.QPolygonF(
                list(map(
                    lambda p : QtCore.QPointF(p[0], p[1]),
                    template_transformed
                ))
            )
        )

        #self.setPolygon( self.polygonFromHomogeniousCoords(self.template_origin, self.homography_m))


    def drawLast4EditedIcons() :
        pass    


    def setHomogeniouseCoordScale(self, coords) :
        return coords[:, :] / coords[:, [2, 2, 2]]

    def polygonFromHomogeniousCoords(self, coords, homography) :

        transformed_coords = np.matmul(homography, coords)

        transformed_coords = self.setHomogeniouseCoordScale(transformed_coords)

        return QtGui.QPolygonF(
            list(map(
                lambda x : QtCore.QPointF(x[0], x[1]),
                transformed_coords
            ))
        )

    def constructTemplate(self, pitch_name="standard", angular_resolution_of_circle=600) :
        field_size = FootballFieldTemplate.field_size
        
        w1 = field_size["boundary"][pitch_name]["width"] / 2
        h1 = field_size["boundary"][pitch_name]["height"] / 2 
        w2 = field_size["penalty_box_width"]
        h2 = field_size["penalty_box_height"] / 2
        w3 = field_size["goal_area_width"]
        h3 = field_size["goal_area_height"] / 2
        r  = field_size["circle_radius"]

        # elemonts of points that will construct polygon of football pitck
        self.template_components = {
            "boundary" : np.array(
                [
                    [[-w1], [-h1], [1]],
                    [[ w1], [-h1], [1]],
                    [[ w1], [ h1], [1]],
                    [[-w1], [ h1], [1]],
                    [[-w1], [-h1], [1]]
                ]
            ),
            "penalty_area_left" : np.array(
                [
                    [[-w1 +  0], [-h2], [1]],
                    [[-w1 + w2], [-h2], [1]],
                    [[-w1 + w2], [ h2], [1]],
                    [[-w1 +  0], [ h2], [1]],
                    [[-w1 +  0], [-h2], [1]]
                ]
            ),
            "penalty_area_right" : np.array(
                [
                    [[w1 -  0], [-h2], [1]],
                    [[w1 - w2], [-h2], [1]],
                    [[w1 - w2], [ h2], [1]],
                    [[w1 -  0], [ h2], [1]],
                    [[w1 -  0], [-h2], [1]]
                ]
            ),
            "goal_area_left" : np.array(
                [
                    [[-w1 +  0], [-h3], [1]],
                    [[-w1 + w3], [-h3], [1]],
                    [[-w1 + w3], [ h3], [1]],
                    [[-w1 +  0], [ h3], [1]],
                    [[-w1 +  0], [-h3], [1]]
                ]
            ),
            "goal_area_right" : np.array(
                [
                    [[w1 -  0], [-h3], [1]],
                    [[w1 - w3], [-h3], [1]],
                    [[w1 - w3], [ h3], [1]],
                    [[w1 -  0], [ h3], [1]],
                    [[w1 -  0], [-h3], [1]]
                ]
            ),
            "center_line" : np.array(
                [
                    [[0], [-h1], [1]],
                    [[0], [ h1], [1]]
                ]
            ),
            "center_circle" : np.array(
                [
                    [[np.cos(theta)], [np.sin(theta)], [1]]
                    for theta in np.linspace(np.pi * 0.5 ,np.pi * 2.5, angular_resolution_of_circle)
                ]
            ) * np.array([[[r], [r], [1]]])
        }

        self.template_origin = np.vstack((
            self.template_components["boundary"],
            self.template_components["penalty_area_left"],
            self.template_components["goal_area_left"],

            np.array([[[-w1], [-h1], [1]]]),

            self.template_components["center_line"],
            self.template_components["center_circle"],

            np.array([[[0], [-h1], [1]]]),
            np.array([[[w1], [-h1], [1]]]),

            self.template_components["penalty_area_right"],
            self.template_components["goal_area_right"],
            

            np.array([[[w1], [-h1], [1]]]),
        ))
        

    def __init__(self, parent = None, pitch_name = "standard") :
        super(FootballFieldTemplate, self).__init__()
        self.parent = parent

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptTouchEvents(True)
        self.setAcceptHoverEvents(True)
        self.setZValue(10)

        self.homography_m = np.eye(3)
        self.translation_m = np.eye(3)

        self.last_4_edited_points_idx = [0, 1, 2, 3]
        self.point_r = 40

        # scale coeffiecient from meter to pixel.
        self.meter_to_pix_coef = 500

        # basic points that 
        self.constructTemplate()

        self.last_4_edited_icons = list(map(
            lambda point : QtWidgets.QGraphicsEllipseItem(
                point[0] - self.point_r,
                point[1] - self.point_r,
                self.point_r * 2,
                self.point_r * 2,
                parent = self       
            ),
            self.template_origin[self.last_4_edited_points_idx]
        ))
        
        self.drawFootBallField()
        

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        return 

    def getDistance(self, p1:np.ndarray, p2:np.ndarray) :
        return np.sqrt(np.sum(np.square(p1 - p2)))


    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.start_pos = event.scenePos()
        self.intersection_clicked = False

        mouse_pose = np.array([
            [event.scenePos().x()],
            [event.scenePos().y()],
            [1]
        ])


        template_traansformed = self.setHomogeniouseCoordScale(np.matmul(self.homography_m, self.template_origin))
        

        for i in range(len(template_traansformed)) :

            if self.getDistance(
                mouse_pose,
                template_traansformed[i]
            ) < self.point_r :

                print("intersection clicked")

                if i not in self.last_4_edited_points_idx :
                    self.last_4_edited_points_idx.pop()
                    self.last_4_edited_points_idx.insert(0, i)
                else :
                    self.last_4_edited_points_idx.remove(i)
                    self.last_4_edited_points_idx.insert(0, i)

                self.intersection_clicked = True

                break

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

        prev_mouse_pos = event.lastScenePos()
        curr_mouse_pos = event.scenePos()


        mouse_pose = np.array([
            [event.scenePos().x()],
            [event.scenePos().y()],
            [1]
        ])
        
        last_4_points_local  = self.template_origin[self.last_4_edited_points_idx]
        last_4_points_global = self.setHomogeniouseCoordScale(np.matmul(
            self.homography_m,
            self.template_origin[self.last_4_edited_points_idx]
        ))

        if self.intersection_clicked :
            #print(self.last_4_edited_points_idx)
            #self.printHomogeniousCoordFriendly(self.template_origin[self.last_4_edited_points_idx])
            last_4_points_global[0] = mouse_pose
       
        else :
            last_4_points_global[:,0,:] += curr_mouse_pos.x() - prev_mouse_pos.x()
            last_4_points_global[:,1,:] += curr_mouse_pos.y() - prev_mouse_pos.y()

            
        self.homography_m = self.resolveHomography(last_4_points_local, last_4_points_global)



        self.drawFootBallField()



    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        return 

        if self.intersection_clicked :        
            pass
            """
            mouse_pose = np.array([
                [event.scenePos().x()],
                [event.scenePos().y()],
                [1]
            ])
            last_4_points_local = self.intersection_points[self.last_4_edited_points_idx]
            last_4_points_global = np.matmul(
                self.getTransformArray(),
                self.intersection_points[self.last_4_edited_points_idx]
            )
            last_4_points_global[0] = mouse_pose

            self.homography_m = self.resolveHomography(last_4_points_local, last_4_points_global)
            self.warpItem()
            """
        self.intersection_clicked = False



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


    def printHomogeniousCoordFriendly(self, coords) :
        print(coords.squeeze().transpose())
        print()



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
        self.setSceneRect(self.image_item.boundingRect())



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

        indicator_layout = QtWidgets.QVBoxLayout()



        self.text_edit = QtWidgets.QTextEdit()
        self.exec_button = QtWidgets.QPushButton("exec")
        self.exec_button.clicked.connect(self.execButtonCliked)

        indicator_layout.addWidget(QtWidgets.QLabel("mouse_pose"))
        self.mouse_pos_label = QtWidgets.QLabel()
        indicator_layout.addWidget(self.mouse_pos_label)


        self.graphics_view = AnnotatorGraphicsView()
        self.graphics_scene = AnnotatorGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)




        self.football_field_template = FootballFieldTemplate()
        self.graphics_scene.addItem(self.football_field_template)

        exec_layout.addWidget(self.text_edit)
        exec_layout.addWidget(self.exec_button)

        main_layout.addLayout(indicator_layout)
        main_layout.addLayout(exec_layout)
        main_layout.addWidget(self.graphics_view)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.createMenus()

    def createMenus(self):
        menu_file = self.menuBar().addMenu("File")
        load_image_action = menu_file.addAction("&Load Image")
        load_image_action.triggered.connect(self.loadImage)

    @QtCore.pyqtSlot()
    def loadImage(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Open Image",
            QtCore.QStandardPaths.writableLocation(
                QtCore.QStandardPaths.PicturesLocation
            ), #QtCore.QDir.currentPath(), 
            "Image Files (*.png *.jpg *.bmp)"
        )
        if filename:
            self.graphics_scene.loadImage(filename)
            self.graphics_view.fitInView(self.graphics_scene.image_item, QtCore.Qt.KeepAspectRatio)
            self.graphics_view.centerOn(self.graphics_scene.image_item)



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



