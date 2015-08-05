from time import sleep


SEQUENCE_ELEMENT_TYPES = [
    "NodeElement"
]


class _SequenceElement(object):
    def __init__(self, queue_pos, arm):
        self.type = "UnNamed"
        self.queue_pos = queue_pos
        self.headers = ["Type"]

    def get_headers(self):
        return self.headers

    def delete_(self):
        raise(NotImplementedError)

    def get_table_value(self, header):
        if header == "Type":
            return self.type

    def set_values(self, arm):
        raise(NotImplementedError)

    def execute(self, arm):
        raise(NotImplementedError)


class NodeElement(_SequenceElement):
    def __init__(self, queue_pos, arm):
        super().__init__(queue_pos, arm)
        self.joint_angles = arm.joint_angles.copy()
        self.type = "Node"
        self.headers.extend(arm.get_joint_names())

    def delete_(self):
        self.joint_angles = {}

    def get_table_value(self, header):
        def_val = super().get_table_value(header)
        if def_val is not None:
            return def_val
        for key in self.joint_angles.keys():
            if str(key) == header:
                return str(self.joint_angles[key])

    def tie_values(self, arm):
        self.joint_angles = arm.joint_angles

    def untie_values(self, arm):
        self.joint_angles = arm.joint_angles.copy()

    def get_values(self, arm):
        arm.set_joint_angles(self.joint_angles.copy())


    def execute(self, arm):
        TIME = 3

        current = arm.joint_angles.copy()
        future = self.joint_angles.copy()
        difference = {}
        diff_list = []
        for key in current.keys():
            new_val = current[key] - future[key]
            difference[key] = new_val
            diff_list.append(abs(new_val))
        print(diff_list)
        if max(diff_list) == 0:
            return
        interval = TIME / max(diff_list)
        for key in difference.keys():
            difference[key] = new_val / max(diff_list)

        for i in range(max(diff_list)):
            new_current = {}
            for key in difference.keys():
                new_current[key] = arm.joint_angles[key] + difference[key]
            arm.set_joint_angles(new_current)
            sleep(interval)
        print(self.type, "executed")

    def hard_update(self, arm):
        self.headers = ["Type"]
        self.headers.extend(arm.get_joint_names())
        self.joint_angles = arm.joint_angles.copy()
