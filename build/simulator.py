import sys

from numpy import array, dot, cross
from numpy.linalg import norm
from math import atan2, pi, cos, sin
import transformations as tf
from PyQt4 import QtCore, QtGui, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *

gl_identity = [[1, 0, 0, 0],
               [0, 1, 0, 0],
               [0, 0, 1, 0],
               [0, 0, 0, 1]]

class SimWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent, cam_config):
        super().__init__()
        self.parent = parent
        self.cam_config = cam_config
        self.camera = Camera(cam_config)
        self.object = None
        self.colour = QtGui.QColor.fromCmykF(0, 0, 0, 0.0)
        self.graphics_parts = []
        self.arm_vectors = None
        self.last_mouse_pos = None

    def initializeGL(self):
        self.qglClearColor(self.colour.dark())
        glShadeModel(GL_FLAT)
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_CULL_FACE)
        glLightfv(GL_LIGHT0, GL_POSITION, (0, 1000, 400, 1.0))
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        for graphics_part in self.graphics_parts:
            glLoadIdentity()
            gluLookAt(*self.camera.get_cam())
            graphics_part.draw()

    def resizeGL(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glViewport(0, 0, width, height)
        glLoadIdentity()
        gluPerspective(self.cam_config["fov"],
                       width / float(height),
                       self.cam_config["near_limit"],
                       self.cam_config["far_limit"])

    def update_display(self):
        arm_vectors = self.parent.arm.member_points
        for graphics_part in self.graphics_parts:
            matrix = arm_vectors.get(graphics_part.name)
            if matrix is None:
                continue
            graphics_part.set_transformation(matrix)
        self.updateGL()

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()

        dx = event.x() - self.last_mouse_pos.x()
        dy = -(event.y() - self.last_mouse_pos.y())

        self.last_mouse_pos = event.pos()

        if event.buttons() & QtCore.Qt.LeftButton:
            self.camera.user_orbit(dx, dy)
        elif event.buttons() & QtCore.Qt.RightButton:
            self.camera.user_pan(dx, dy)

        self.updateGL()

    def wheelEvent(self, event):
        self.camera.user_zoom(event.delta())

    def load_arm(self, arm_data, file_manager):
        self.graphics_parts = []

        for i, model_desc in enumerate(arm_data["MODELS"]):
            fd = open(file_manager.get_model_file(model_desc[1]), 'rU')
            self.graphics_parts.append(GraphicsPart(model_desc[0], fd))
            fd.close()

        self.updateGL()


class GraphicsPart(object):

    def __init__(self, name, file_object):
        self.name = name
        self.transformation = gl_identity

        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.2, 0.2, 1.0, 1.0))
        self.load_ascii_stl(file_object)
        glEndList()

    def set_transformation(self, transformation_matrix):
        self.transformation = transformation_matrix

    def draw(self):
        glMultMatrixf(self.transformation)
        glCallList(self.gl_list)

    def load_ascii_stl(self, file_object):
        glBegin(GL_TRIANGLES)
        for line in file_object:
            line = line.strip().split()
            if line[0] == "solid":
                pass
            elif line[0] == "facet":
                glNormal3f(*[float(x) for x in line[2:5]])
            elif line[0] == "vertex":
                glVertex3f(*[float(x) for x in line[1:4]])
        glEnd()


class Camera(object):
    """ Class which handles the camera """

    def __init__(self, cam_config):
        self._settings = cam_config
        self._position = array(cam_config["def_pos"])
        self._focus = array(cam_config["def_focus"])
        self._up = array(cam_config["def_up"])

    def user_pan(self, dx, dy):
        """ Pans the camera based on passed mouse movements.

        user_pan(int, int) -> None
        """
        sensetivity = self._settings["pan_sensetivity"]
        focus_to_cam = self._position - self._focus
        x = [self._position, self._focus]
        for i in range(len(x)):
            x[i] = x[i] + (-sensetivity*dy * tf.unit_vector(self._up))
            x[i] = x[i] + (sensetivity*dx * tf.unit_vector(
                cross(focus_to_cam, self._up)))
        self._position, self._focus = x

    def user_orbit(self, dx, dy):
        """ Orbits the camera based on passed mouse movements.

        user_pan(int, int) -> None

        Note: h denotes horizontal and v denotes vertical
        """
        sensetivity = self._settings["orbit_sensetivity"]
        focus_to_cam = self._position - self._focus

        dist_to_focus_h = norm(focus_to_cam[:2])
        dist_to_focus = norm(focus_to_cam)

        angleh = atan2(focus_to_cam[1], focus_to_cam[0])
        anglev = atan2(focus_to_cam[2], dist_to_focus_h)

        angleh -= sensetivity*dx
        anglev -= sensetivity*dy

        if anglev >= pi/2-0.1:
            anglev = pi/2-0.1
        if anglev <= -pi/2+0.1:
            anglev = -pi/2+0.1

        focus_to_cam = array(
            [cos(angleh)*cos(anglev)*dist_to_focus,
            sin(angleh)*cos(anglev)*dist_to_focus,
            sin(anglev)*dist_to_focus]
        )

        self._up = tf.unit_vector(-1 * cross(focus_to_cam,
                            cross(focus_to_cam, array([0, 0, 1]))))
        self._position = self._focus + focus_to_cam

    def user_zoom(self, scroll_y):
        """ Zooms the camera based on passed mouse movements.

        user_zoom(int) -> None
        """
        sensetivity = self._settings["zoom_sensetivity"]
        u_focus_to_cam = tf.unit_vector(self._position - self._focus)
        self._position = self._position + \
                         scroll_y*sensetivity * u_focus_to_cam
        if norm(self._position - self._focus) <= 1:
            self._focus = self._position + -1 * u_focus_to_cam
        return None

    def get_cam(self):
        """ Returns a list of values in the format required for many OpenGL
        functions.

        get_cam() -> list[9](float)
        """
        return list(self._position) + list(self._focus) + list(self._up)