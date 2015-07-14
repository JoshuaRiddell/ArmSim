import sys
import math

from PyQt4 import QtCore, QtGui, QtOpenGL
from OpenGL.GL import *


class SimWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def initialise_gl(self):
        pass

    def load_arm(self, arm_data):
        pass
