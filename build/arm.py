from PyQt4 import QtGui
from numpy import array, dot, around, append
import transformations as tf
from math import pi

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

        self.joint_angles = {}
        for chain in self.chains:
            for i in range(len(chain)):
                if chain[i] == ORIGIN_KEYWORD:
                    continue
                self.joint_angles[(chain[i-1], chain[i])] = 0

        self.member_points = {ORIGIN_KEYWORD: array([0, 0, 0])}
        self.arm_chain = None

    def calc_forward_kinematics(self):
        self.arm_chain = []

        for chain in self.chains:
            for member in self.members.values():
                member.reset()
            self.arm_chain.append(self.transform_members(
                chain))

        for key in self.member_points.keys():
            print(key, self.member_points[key])

    def transform_members(self, chain):
        angle = self.joint_angles[tuple(chain[:2])]
        trans = self.members[chain[1]].get_rotation(angle)
        for vector in chain[1:]:
            self.members[vector].transform(trans)

        origin = self.member_points[chain[0]]
        origin = origin + self.members[chain[1]].get_vector()
        self.member_points[chain[1]] = origin

        if len(chain) == 2:
            return
        else:
            return self.transform_members(chain[1:])

    def set_angle(self, joint, value):
        self.joint_angles[joint] = value
        self.calc_forward_kinematics()

    def set_point(self, joint, value):
        pass


class Member(object):
    def __init__(self, length, axis_normal, direction, normal):
        self.length = length
        self.vectors = []
        for vector in [axis_normal, direction, normal]:
            self.vectors.append(append(tf.unit_vector(array(vector)), [1]))
        self.backup = self.vectors[:]

    def get_rotation(self, angle):
        return tf.rotation_matrix(angle*pi/180, self.vectors[0][:3])

    def get_vector(self):
        return dot(self.length, self.vectors[1][:3])

    def transform(self, matrix):
        for i, vector in enumerate(self.vectors):
            self.vectors[i] = dot(vector, matrix)

    def reset(self):
        self.vectors = self.backup[:]

    def __repr__(self):
        return "Member object; direction:" + repr(around(self.vectors[1], 1))
