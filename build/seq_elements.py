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
        print(self.queue_pos, "tied")
        self.joint_angles = arm.joint_angles
        print(self.queue_pos, self.joint_angles)

    def untie_values(self, arm):
        print(self.queue_pos, "untied")
        self.joint_angles = arm.joint_angles.copy()
        print(self.queue_pos, self.joint_angles)

    def get_values(self, arm):
        print(self.queue_pos, self.joint_angles)
        arm.set_joint_angles(self.joint_angles.copy())

    def init_execute(self, arm):
        arm.set_joint_angles(self.joint_angles)

    def execute(self, arm):
        TIME = 3

        current = arm.joint_angles.copy()
        future = self.joint_angles.copy()

        diff_dict = {}
        diff_list = []
        for key in current.keys():
            new_val = future[key] - current[key]
            diff_dict[key] = new_val
            diff_list.append(abs(new_val))

        if abs(max(diff_list)) < 1:
            return

        count = 100
        tim_interval = TIME / count

        for key in diff_dict.keys():
            diff_dict[key] = diff_dict[key] / count

        for i in range(count):
            for key in arm.joint_angles.keys():
                arm.joint_angles[key] += diff_dict[key]
            arm.calc_forward_kinematics(False)
            sleep(tim_interval)

    def hard_update(self, arm):
        self.headers = ["Type"]
        self.headers.extend(arm.get_joint_names())
        self.joint_angles = arm.joint_angles.copy()
