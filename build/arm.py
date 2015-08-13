from PyQt4 import QtGui
from numpy import array, dot, cross, around, append
import transformations as tf
from math import pi

ORIGIN_KEYWORD = "origin"


class Arm(object):
    """ Defines the robotic arm
    """

    def __init__(self, parent, **kwargs):
        """ Initialises arm values.
        """
        self.parent = parent
        self.joint_angles = {}
        self.member_points = {}

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

        self.member_points = {ORIGIN_KEYWORD: (array([0, 0, 0]), None)}
        self.arm_chain = None

    def calc_forward_kinematics(self, update_seq=True):
        self.arm_chain = []

        for chain in self.chains:
            for member in self.members.values():
                member.reset()

            origin = self.member_points[ORIGIN_KEYWORD][0]
            for index, member_name in enumerate(chain):
                if index == 0:
                    continue

                angle = self.joint_angles[tuple(chain[index-1:index+1])]
                trans = self.members[chain[index]].get_rotation_matrix(angle)

                for sub_member_name in chain[index:]:
                    self.members[sub_member_name].transform(trans)

                self.member_points[chain[index]] = self.members[chain[index]].get_graphics_matrix(*origin)

                origin = origin + self.members[chain[index]].get_vector()

        if update_seq:
            self.parent.sequencer_widget.update_values()

    def transform_members(self, chain):
        angle = self.joint_angles[tuple(chain[:2])]
        trans = self.members[chain[1]].get_rotation_matrix(angle)
        for vector in chain[1:]:
            self.members[vector].transform(trans)

        origin = self.member_points[chain[0]][0]
        self.member_points[chain[1]] = (origin, self.members[chain[1]])
        origin = origin + self.members[chain[1]].get_vector()
        try:
            self.member_points[chain[2]] = (origin, None)
        except:
            self.member_points["end_effector"] = (origin, None)

        if len(chain) == 2:
            return
        else:
            return self.transform_members(chain[1:])

    def set_angle(self, joint, value):
        self.joint_angles[joint] = value
        self.calc_forward_kinematics()

    def set_point(self, joint, value):
        pass

    def set_joint_angles(self, joint_angles):
        self.joint_angles = joint_angles
        self.parent.update_control_values()

    def get_joint_names(self):
        joint_name_list = []
        for key in self.joint_angles.keys():
            joint_name_list.append(str(key))
        return joint_name_list


class Member(object):
    def __init__(self, length, axis_normal, x, y, z):
        self.length = length
        self.axes = []
        for vector in [x, y, z]:
            self.axes.append(append(tf.unit_vector(array(vector)), [1]))
        self.axis_normal = append(tf.unit_vector(array(axis_normal)), [1])

        self.backup = [self.axis_normal, self.axes]

    def get_rotation_matrix(self, angle):
        return tf.rotation_matrix(angle*pi/180, self.axis_normal[:3])

    def get_graphics_matrix(self, transx, transy, transz):
        translation_matrix = []
        for axis_vector in self.axes:
            translation_matrix.append(list(axis_vector)[:3] + [0])
        translation_matrix.append([transx, transy, transz, 1])
        return translation_matrix

    def get_vector(self):
        return dot(self.length, self.axes[2][:3])

    def transform(self, matrix):
        for i, axis_vector in enumerate(self.axes):
            self.axes[i] = dot(axis_vector, matrix)
        self.axis_normal = dot(self.axis_normal, matrix)

    def reset(self):
        self.axis_normal = self.backup[0][:]
        self.axes = self.backup[1][:]

    def __repr__(self):
        return "Member object; direction:" + repr(around(self.vectors[1], 1))
