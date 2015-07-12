from PyQt4.QtOpenGL import *
from PyQt4 import QtGui


class SimWidget(QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
