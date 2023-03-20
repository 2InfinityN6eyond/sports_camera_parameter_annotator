import copy

#import cv2
import json

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


    def undo(self) :
        if len(self.transform_history) > 1 :
            self.transform_history.pop()
            self.homography_m = self.transform_history[-1]["homography"]
            self.drawFootBallField()


    def memoryCurrState(self, tx, ty, tz, rx, ry, rz, f, cx, cy) :
        self.transform_history.append({
            "tx" : tx,
            "ty" : ty,
            "tz" : tz,
            "rx" : rx,
            "ry" : ry,
            "rz" : rz,
            "f"  : f,
            "cx" : cx,
            "cy" : cy,
            "homography" : self.homography_m.copy()
        })

    def homographyByParameters(self, tx=0, ty=0, tz=0, rx=0, ry=0, rz=0, f=0, cx=0, cy=0) :
        intrinsic = np.array([
            [f, 0, cx],
            [0, f, cy],
            [0, 0, 1]
        ])

        rotation_m = self.rotationMatrix(rx, ry, rz)
        translation_m = np.array([[tx], [ty], [tz]])

        #print(intrinsic)
        #print(np.hstack((rotation_m, translation_m)))

        extrinsic = np.hstack((rotation_m, translation_m))
        homography = np.matmul(intrinsic, extrinsic)
        self.homography_m = homography

        self.intrinsic_m = intrinsic
        self.extrinsic_m = extrinsic

        self.memoryCurrState(tx, ty, tz, rx, ry, rz, f, cx, cy)
        self.drawFootBallField()


    def drawFootBallField(self) :
        template_transformed = np.matmul(self.homography_m, self.template_origin)
        template_transformed = self.setHomogeniouseCoordScale(template_transformed)

        print(template_transformed)
        print(self.homography_m)

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

        self.parent.updateIndicator()


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
                    #[[-w1], [-h1], [1]],
                    #[[ w1], [-h1], [1]],
                    #[[ w1], [ h1], [1]],
                    #[[-w1], [ h1], [1]],
                    #[[-w1], [-h1], [1]]
                    [[-w1], [-h1], [0], [1]],
                    [[ w1], [-h1], [0], [1]],
                    [[ w1], [ h1], [0], [1]],
                    [[-w1], [ h1], [0], [1]],
                    [[-w1], [-h1], [0], [1]]
                ]
            ),
            "penalty_area_left" : np.array(
                [
                    #[[-w1 +  0], [-h2], [1]],
                    #[[-w1 + w2], [-h2], [1]],
                    #[[-w1 + w2], [ h2], [1]],
                    #[[-w1 +  0], [ h2], [1]],
                    #[[-w1 +  0], [-h2], [1]]
                    [[-w1 +  0], [-h2], [0], [1]],
                    [[-w1 + w2], [-h2], [0], [1]],
                    [[-w1 + w2], [ h2], [0], [1]],
                    [[-w1 +  0], [ h2], [0], [1]],
                    [[-w1 +  0], [-h2], [0], [1]]
                ]
            ),
            "penalty_area_right" : np.array(
                [
                    [[w1 -  0], [-h2], [0], [1]],
                    [[w1 - w2], [-h2], [0], [1]],
                    [[w1 - w2], [ h2], [0], [1]],
                    [[w1 -  0], [ h2], [0], [1]],
                    [[w1 -  0], [-h2], [0], [1]]
                ]
            ),
            "goal_area_left" : np.array(
                [
                    [[-w1 +  0], [-h3], [0], [1]],
                    [[-w1 + w3], [-h3], [0], [1]],
                    [[-w1 + w3], [ h3], [0], [1]],
                    [[-w1 +  0], [ h3], [0], [1]],
                    [[-w1 +  0], [-h3], [0], [1]]
                ]
            ),
            "goal_area_right" : np.array(
                [
                    [[w1 -  0], [-h3], [0], [1]],
                    [[w1 - w3], [-h3], [0], [1]],
                    [[w1 - w3], [ h3], [0], [1]],
                    [[w1 -  0], [ h3], [0], [1]],
                    [[w1 -  0], [-h3], [0], [1]]
                ]
            ),
            "center_line" : np.array(
                [
                    [[0], [-h1], [0], [1]],
                    [[0], [ h1], [0], [1]]
                ]
            ),
            "center_circle" : np.array(
                [
                    [[np.cos(theta)], [np.sin(theta)], [0], [1]]
                    for theta in np.linspace(np.pi * 0.5 ,np.pi * 2.5, angular_resolution_of_circle)
                ]
            ) * np.array([[[r], [r], [0], [1]]])
        }

        self.template_origin = np.vstack((
            self.template_components["boundary"],
            self.template_components["penalty_area_left"],
            self.template_components["goal_area_left"],

            np.array([[[-w1], [-h1], [0], [1]]]),

            self.template_components["center_line"],
            self.template_components["center_circle"],

            np.array([[[0], [-h1],  [0], [1]]]),
            np.array([[[w1], [-h1], [0], [1]]]),

            self.template_components["penalty_area_right"],
            self.template_components["goal_area_right"],
            
            np.array([[[w1], [-h1], [0], [1]]]),
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

        self.homography_m = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 1]
        ])

        #self.translation_m = np.array([[0], [0], [0]])

        #self.rotation_x_m = np.eye(3)
        #self.rotation_y_m = np.eye(3)
        #self.rotation_z_m = np.eye(3)
        #self.focal_length = 200
        #self.cx = 1000
        #self.cy = 800

        self.intrinsic_m = np.eye(3)
        self.extrinsic_m = np.hstack((np.eye(3), np.array([[0], [0], [0]])))

        #self.homography_history = [self.homography_m]
        self.transform_history = []



        self.translation_m = np.eye(3)

        self.last_4_edited_points_idx = [0, 1, 2, 3]
        self.point_r = 4

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
        
        #self.drawFootBallField()


    def rotationMatrix(self, theta1, theta2, theta3):
        c1 = np.cos(theta1 * np.pi / 180)
        s1 = np.sin(theta1 * np.pi / 180)
        c2 = np.cos(theta2 * np.pi / 180)
        s2 = np.sin(theta2 * np.pi / 180)
        c3 = np.cos(theta3 * np.pi / 180)
        s3 = np.sin(theta3 * np.pi / 180)
        return np.array([
            [c2*c3, -c2*s3, s2],
            [c1*s3+c3*s1*s2, c1*c3-s1*s2*s3, -c2*s1],
            [s1*s3-c1*c3*s2, c3*s1+c1*s2*s3, c1*c2]
        ])   



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
            ) < 30 :

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



        converted = np.matmul(self.homography_m, self.template_origin)
        converted = self.setHomogeniouseCoordScale(converted)


        random_4_idxs = np.random.randint(0, len(self.template_origin) - 1, 4)


        print("orig : ")
        print(self.template_origin[random_4_idxs])
        print("transfromed :")
        print(converted[random_4_idxs])

        print("homography:")
        print(self.homography_m)
        print("recalculated : ")


          

        print(self.resolveHomography(self.template_origin[random_4_idxs], converted[random_4_idxs]))


        Q, R = np.linalg.qr(self.homography_m)
        Q *= -1
        R *= -1

        Q, R = np.linalg.qr(np.linalg.inv(self.homography_m[:, :3]))
        Q = np.linalg.inv(Q)
        R = np.linalg.inv(R)

        self.intrinsic_m = R
        self.extrinsic_m = Q

        self.drawFootBallField()

        self.transform_history.append({
            "homography" : self.homography_m.copy()
        })


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
     def resolveHomography(self, pts_src, pts_dst) : 
        """
        resolve projection matrix from point [x, y, z, 1] -> [u, v, 1]
        """

        pts_src = list(map(
            lambda x : np.squeeze(x),
            np.split(pts_src, 4)
        ))
        pts_dst = list(map(
            lambda x : np.squeeze(x),
            np.split(pts_dst, 4)
        ))
        
        zeros = np.zeros(4)

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
        homography = Vt[-1].reshape(3, 4)
        return homography / homography[2][3]



    def __resolveHomography(self, pts_src, pts_dst) :
        
        """
        deprecated.
        
        """

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
        image = QtGui.QPixmap(image_path)
        self.image_item.setPixmap(image)
        self.setSceneRect(self.image_item.boundingRect())

        return (image.width(), image.height())


class AnnotatorGraphicsView(QtWidgets.QGraphicsView) :

    def __init__(self, parent = None) :
        super(AnnotatorGraphicsView, self).__init__(parent)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setMouseTracking(True)

        self.shortcut_zoom_factor = 2.0

        QtWidgets.QShortcut(QtGui.QKeySequence.ZoomIn,  self, activated = self.zoomIn)
        QtWidgets.QShortcut(QtGui.QKeySequence.ZoomOut, self, activated = self.zoomOut)

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


        
        self.football_field_template = FootballFieldTemplate(self)
        self.annotator_scene = AnnotatorGraphicsScene()
        self.annotator_view = AnnotatorGraphicsView()

        self.annotator_scene.addItem(self.football_field_template)
        self.annotator_view.setScene(self.annotator_scene)





        indicator_control_layout = QtWidgets.QVBoxLayout()

        self.undo_button = QtWidgets.QPushButton("undo", clicked=self.undoButtonClicked)
        self.save_button = QtWidgets.QPushButton("save", clicked=self.saveButtonClicked)

#        self.undo_button.clicked.connect(self.undoButtonClicked)
#        self.save_button.clicked.connect(self.saveButtonClicked)

        self.mouse_pos_label = QtWidgets.QLabel()

        indicator_control_layout.addWidget(QtWidgets.QLabel("mouse_pose"))
        indicator_control_layout.addWidget(self.mouse_pos_label)

        indicator_control_layout.addWidget(self.undo_button)
        indicator_control_layout.addWidget(self.save_button)
        indicator_control_layout.addWidget(self.mouse_pos_label)


        rotation_slider_layout = QtWidgets.QHBoxLayout()


        self.slider_memory = {
            "tx" : 0,
            "ty" : 0,
            "tz" : 50,
            "rx" : 0,
            "ry" : 0,
            "rz" : 0,
            "f"  : 1000,
            "cx" : 800,
            "cy" : 500
        }


        self.homography_label = QtWidgets.QLabel(str(self.football_field_template.homography_m))
        indicator_control_layout.addWidget(QtWidgets.QLabel("homogrpahy matrix : "))
        indicator_control_layout.addWidget(self.homography_label)

        self.intrinsic_label  = QtWidgets.QLabel(str(self.football_field_template.intrinsic_m))
        indicator_control_layout.addWidget(QtWidgets.QLabel("intrinsic matrix : "))
        indicator_control_layout.addWidget(self.intrinsic_label)

        self.extrinsic_label = QtWidgets.QLabel(str(self.football_field_template.extrinsic_m))
        indicator_control_layout.addWidget(QtWidgets.QLabel("extrinsic matrix"))
        indicator_control_layout.addWidget(self.extrinsic_label)



        self.camera_parameter_indicator = QtWidgets.QLabel(
            f"f:{1000:5d}|tx:{0:5.0f}|ty:{0:5.0f}|tz:{0:5.0f}|rx:{0:5.0f}|ry:{0:5.0f}|rz:{0:5.0f}"
            
            #f"  f  | tx  | ty  | tz  | rx  | ry  | rz  \n" + 
            #f"{1000:5d}|{0:5d}|{0:5d}|{100:5d}|{0:5d}|{0:5d}|{0:5d}"
        )

        self.f_slider  = QtWidgets.QSlider(valueChanged = lambda x : self.sliderChanged(x, "f"))
        self.cx_slider = QtWidgets.QSlider(valueChanged = lambda x : self.sliderChanged(x, "cx"))
        self.cy_slider = QtWidgets.QSlider(valueChanged = lambda x : self.sliderChanged(x, "cy"))
        self.tx_slider = QtWidgets.QSlider(valueChanged = lambda x : self.sliderChanged(x, "tx"))
        self.ty_slider = QtWidgets.QSlider(valueChanged = lambda x : self.sliderChanged(x, "ty"))
        self.tz_slider = QtWidgets.QSlider(valueChanged = lambda x : self.sliderChanged(x, "tz"))
        self.rx_slider = QtWidgets.QSlider(valueChanged = lambda x : self.sliderChanged(x, "rx"))
        self.ry_slider = QtWidgets.QSlider(valueChanged = lambda x : self.sliderChanged(x, "ry"))
        self.rz_slider = QtWidgets.QSlider(valueChanged = lambda x : self.sliderChanged(x, "rz"))
        
        self.f_slider.setRange(100, 8000)
        self.f_slider.setSingleStep(0.1)
        self.f_slider.setValue(1000)
        
        self.cx_slider.setRange(1, 2000)
        self.cy_slider.setRange(1, 2000)

        self.cx_slider.setSingleStep(0.1)
        self.cy_slider.setSingleStep(0.1)

        self.tx_slider.setRange(-3000, 3000)
        self.ty_slider.setRange(-3000, 3000)
        self.tz_slider.setRange(10, 3000)

        self.tx_slider.setSingleStep(0.1)
        self.ty_slider.setSingleStep(0.1)
        self.tz_slider.setSingleStep(0.1)

        self.rx_slider.setRange(-100, 100)
        self.ry_slider.setRange(-100, 100)
        self.rz_slider.setRange(-100, 100)

        self.rx_slider.setSingleStep(0.1)
        self.ry_slider.setSingleStep(0.1)
        self.rz_slider.setSingleStep(0.1)

        rotation_slider_layout.addWidget(self.f_slider)
        #rotation_slider_layout.addWidget(self.cx_slider)
        #rotation_slider_layout.addWidget(self.cy_slider)
        rotation_slider_layout.addWidget(self.tx_slider)
        rotation_slider_layout.addWidget(self.ty_slider)
        rotation_slider_layout.addWidget(self.tz_slider)
        rotation_slider_layout.addWidget(self.rx_slider)
        rotation_slider_layout.addWidget(self.ry_slider)
        rotation_slider_layout.addWidget(self.rz_slider)

        indicator_control_layout.addLayout(rotation_slider_layout)

        indicator_control_layout.addWidget(self.camera_parameter_indicator)


        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(indicator_control_layout)
        main_layout.addWidget(self.annotator_view)

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
            self.file_name = filename
            image_shape = self.annotator_scene.loadImage(filename)
            self.annotator_view.fitInView(self.annotator_scene.image_item, QtCore.Qt.KeepAspectRatio)
            self.annotator_view.centerOn(self.annotator_scene.image_item)
            print(image_shape)
            self.cx_slider.setValue(int(image_shape[0] / 2))
            self.cy_slider.setValue(int(image_shape[1] / 2))

    def saveButtonClicked(self) :
        print("saveing output")
            
        homography = self.football_field_template.homography_m
        template_origin = copy.deepcopy(self.football_field_template.template_components)
        template_transformed = {}
        
        for k, v in template_origin.items() :
            template_transformed[k] = np.matmul(homography, v).tolist()
            template_origin[k] = v.tolist()
        
        
        with open(self.file_name.split(".")[0] + ".json", "w") as fp :
            json.dump(
                {
                    "image_file_name" : self.file_name,
                    "homography" : homography.tolist(),
                    "template_origin" : template_origin,
                    "template_transformed" : template_transformed
                },
                fp,
                indent=4
            )

    def undoButtonClicked(self) :
        self.football_field_template.undo()

    def sliderChanged(self, value, slider_name) :
        self.slider_memory[slider_name] = value
        self.football_field_template.homographyByParameters(**self.slider_memory)
        self.plotSliderValues(**self.slider_memory)
        self.updateIndicator()
        

    def updateIndicator(self) :
        self.homography_label.setText(str(self.football_field_template.homography_m))
        self.intrinsic_label.setText(str(self.football_field_template.intrinsic_m))
        self.extrinsic_label.setText(str(self.football_field_template.extrinsic_m))


    def plotSliderValues(self, f, cx, cy, tx, ty, tz, rx, ry, rz) :
        self.camera_parameter_indicator.setText(
            #"{}|{}|{}|{}|{}|{}|{}" + 
            #"  f  | tx  | ty  | tz  | rx  | ry  | rz  \n" + 
            #f"{f:5d}|{tx:5d}|{ty:5d}|{tz:5d}|{rx:5d}|{ry:5d}|{rz:5d}"
            
            f"f:{f:5d}|tx:{tx:5.0f}|ty:{ty:5.0f}|tz:{tz:5.0f}|rx:{rx:5.0f}|ry:{ry:5.0f}|rz:{rz:5.0f}"
        )

        
if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resize(1800, 1000)
    w.show()
    sys.exit(app.exec_())