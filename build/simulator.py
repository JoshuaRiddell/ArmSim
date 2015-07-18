import sys
import math

from PyQt4 import QtCore, QtGui, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *


class SimWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.object = None
        self.colour = QtGui.QColor.fromCmykF(0, 0, 0, 0.0)

    def initializeGL(self):
        print("called")
        self.qglClearColor(self.colour.dark())
        glShadeModel(GL_FLAT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(235, -227, 311, -9, 58, 83, -0.3379, 0.3931, 0.8551)
        for gl_list in self.gl_lists:
            glCallList(gl_list)

    def resizeGL(self, width, height):
        print("resize called")
        side = min(width, height)
        if side < 0:
            return

        glViewport((width - side) // 2, (height - side) // 2, side, side)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, width / float(height), 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)

    def load_arm(self, arm_data, file_manager):
        self.gl_lists = []

        for i, model_desc in enumerate(arm_data["MODELS"]):
            self.gl_lists.append(glGenLists(1))
            glNewList(self.gl_lists[i], GL_COMPILE)

            print(file_manager.get_model_file(model_desc[0]))
            fd = open(file_manager.get_model_file(model_desc[0]), 'rU')

            glBegin(GL_TRIANGLES)
            for line in fd:
                line = line.strip().split()
                if line[0] == "solid":
                    pass
                elif line[0] == "facet":
                    glNormal3f(*[float(x) for x in line[2:5]])
                elif line[0] == "vertex":
                    glVertex3f(*[float(x) for x in line[1:4]])
            glEnd()
            glEndList()
            fd.close()
