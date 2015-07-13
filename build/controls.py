from PyQt4 import QtGui, QtCore


class Angle(QtGui.QWidget):
    def __init__(self, parent, joint, minimum, maximum, default):
        super().__init__(parent)
        self.initGui()

        self.value = default
        self.minimum = minimum
        self.maximum = maximum
        self.joint = joint

    def initGui(self):
        layout = QtGui.QVBoxLayout()

        control_layout = QtGui.QHBoxLayout()

        self.inputs = [QtGui.QSpinBox(), QtGui.QSlider(QtCore.Qt.Horizontal)]
        stretch_factors = [0, 1]

        for index, obj in enumerate(self.inputs):
            obj.valueChanged.connect(self.value_changed)
            control_layout.addWidget(obj, stretch_factors[index])

        layout.addLayout(control_layout)
        self.setLayout(layout)

    def value_changed(self, value):
        print(value)
        for obj in self.inputs:
            obj.setValue(value)
