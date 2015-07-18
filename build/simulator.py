import sys
import math

from PyQt4 import QtCore, QtGui, QtOpenGL
from OpenGL.GL import *


class SimWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.object = None
        self.colour = QtGui.QColor.fromCmykF(0.5, 0.5, 0.5, 0.0)

    def initializeGL(self):
        print("called")
        self.qglClearColor(self.colour.dark())
        glShadeModel(GL_FLAT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

    def resizeGL(self, width, height):
        print("resize called")
        side = min(width, height)
        if side < 0:
            return

        glViewport((width - side) // 2, (height - side) // 2, side, side)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        glMatrixMode(GL_MODELVIEW)

    def load_arm(self, arm_data):
        for model_desc in arm_data["MODELS"]:
            pass


class graphicsObject(object):
    pass
