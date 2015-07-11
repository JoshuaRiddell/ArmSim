from PyQt4.QtOpenGL import *
from PyQt4 import QtGui


class SimWidget(QGLWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
