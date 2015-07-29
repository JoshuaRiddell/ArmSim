from PyQt4 import QtGui, QtCore


class Angle(QtGui.QWidget):
    def __init__(self, parent, joints, minimum, maximum, default, name=None):
        super().__init__()

        self.arm = parent.arm
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
        if self.multiple:
            x = self.value
            for joint in self.joints:
                self.arm.set_angle(joint[:2], eval(joint[2]))
        else:
            self.arm.set_angle(self.joints, self.value)

    def pull_values(self):
        joint_angles = self.arm.joint_angles
        if self.multiple:
            joint = self.joints[0][:2]
        else:
            joint = self.joints

        self.value = joint_angles[joint]
        for obj in self.inputs:
            obj.setValue(self.value)
            obj.update()
            obj.repaint()
        self.update()
        self.repaint()
