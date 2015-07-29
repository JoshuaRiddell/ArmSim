from time import sleep
from PyQt4 import QtGui


SEQUENCE_ELEMENT_TYPES = [
    "NodeElement"
]


class _SequenceElement(object):
    def __init__(self, queue_pos, arm):
        self.name = "UnNamed"
        self.queue_pos = queue_pos
        self.headers = ["QPos", "Name"]

    def get_headers(self):
        return self.headers

    def delete_(self):
        raise(NotImplementedError)

    def get_table_value(self, header):
        if header == "QPos":
            return self.queue_pos
        if header == "Name":
            return self.name

    def set_values(self, arm):
        raise(NotImplementedError)

    def execute(self, arm):
        raise(NotImplementedError)


class NodeElement(_SequenceElement):
    def __init__(self, queue_pos, arm):
        super().__init__(queue_pos, arm)
        self.joint_angles = arm.joint_angles.copy()
        self.name = "Node"
        self.headers.extend(arm.get_joint_names())

    def delete_(self):
        self.joint_angles = {}

    def get_table_value(self, header):
        super().get_table_value(header)
        for key in self.joint_angles.keys():
            if str(key) == header:
                return self.joint_angles[key]

    def tie_values(self, arm):
        self.joint_angles = arm.joint_angles

    def untie_values(self, arm):
        self.joint_angles = arm.joint_angles.copy()

    def get_values(self, arm):
        arm.set_joint_angles(self.joint_angles.copy())

    def hard_update(self, arm):
        self.headers = ["QPos"]
        self.headers.extend(arm.get_joint_names())
        self.joint_angles = arm.joint_angles.copy()
