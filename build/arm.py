from PyQt4 import QtGui
from numpy import array

ORIGIN_KEYWORD = "origin"


class Arm(object):
    """ Defines the robotic arm
    """

    def __init__(self, **kwargs):
        """ Initialises arm values.
        """
        pass

    def load_arm(self, arm_dictionary):
        self.members = {}
        for member in arm_dictionary["MEMBERS"]:
            self.members[member[0]] = Member(*member[1:])

        self.chains = arm_dictionary["VECTOR_CHAINS"]

        self.joints = {}
        for chain in self.chains:
            for i in range(len(chain)):
                if chain[i] == "origin":
                    continue
                self.joints[(chain[i-1], chain[i])] = 0
        print(self.joints, self.members, self.chains, sep="\n")

    def calc_forward_kinematics(self):
        for chain in self.chains:
            pass

    def set_angle(self, joint, value):
        self.joints[joint] = value
        print(self.joints)

    def set_point(self, joint, value):
        pass


class Member(object):
    def __init__(self, length, axis_normal, direction, normal):
        self.length = length
        self.axis_normal = array(axis_normal)
        self.direction = array(direction)
        self.normal = array(normal)

    def __repr__(self):
        return "Member object; direction:" + str(self.direction)
