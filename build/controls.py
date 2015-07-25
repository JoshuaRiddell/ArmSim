from PyQt4 import QtGui, QtCore


class Angle(QtGui.QWidget):
    def __init__(self, parent, joints, minimum, maximum, default, name=None):
        super().__init__()

        self.parent = parent
        self.value = default
        self.minimum = minimum
        self.maximum = maximum
        self.joints = joints
        self.multiple = type(self.joints) == type([])
        self.name = name

        self.initGui()
        self.value_changed(self.value)

    def initGui(self):
        layout = QtGui.QVBoxLayout()

        control_layout = QtGui.QHBoxLayout()

        self.inputs = [QtGui.QSpinBox(), QtGui.QSlider(QtCore.Qt.Horizontal)]
        stretch_factors = [0, 1]

        for index, obj in enumerate(self.inputs):
            obj.valueChanged.connect(self.value_changed)
            obj.setRange(self.minimum, self.maximum)
            control_layout.addWidget(obj, stretch_factors[index])

        if self.name is not None:
            layout.addWidget(QtGui.QLabel("Angle: " + str(self.name)))
        else:
            layout.addWidget(QtGui.QLabel("Angle: " + str(self.joints)))
        layout.addLayout(control_layout)
        self.setLayout(layout)

    def value_changed(self, value):
        self.value = value
        for obj in self.inputs:
            obj.setValue(value)
        self.parent.update_arm_pos("set_angle", self.joint, self.value)
