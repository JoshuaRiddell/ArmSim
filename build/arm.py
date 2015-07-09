#   ArmSim                                                             #
#   By: Joshua Riddell                                                 #
#                                                                      #
#  Permission is hereby granted, free of charge, to any person         #
#  obtaining a copy of this software and associated documentation      #
#  files (the "Software"), to deal in the Software without             #
#  restriction, including without limitation the rights to use,        #
#  copy, modify, merge, publish, distribute, sublicense, and/or sell   #
#  copies of the Software, and to permit persons to whom the           #
#  Software is furnished to do so.                                     #
#                                                                      #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,     #
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES     #
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND            #
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR        #
#  ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF      #
#  CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION  #
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.     #


VERTICAL_OFFSET = 88
BASE_HEIGHT = 49
ARM1_LEN = 103
ARM2_LEN = 123
AXIS_ROTATOR_LEN = 25

### UPDATE ACCURACY OF VALUES BELOW
PINCER_CONST_LEN = 85  # length between the pincer and next point of rotation
PINCER_ROTATE_LEN = 30
PINCER_OPEN_WIDTH = 54

from math import *
import vector as vec


class Effector(object):
    """ Defines the resources describing the arm at a single position/direction.

    """

    def __init__(self, origin_to_endpoint, direction, pincer):
        """ Initialises values.

        EffectorPosition(list(int,int,int), list(int,int,int), bool) -> None
        """

        self.pos_vect = origin_to_endpoint
        self.dir_vect = direction
        self.pincer = pincer

        self._angles = []
        self._joints = []

        self.calc_angles()

    # def get_posVect(self):
    #     """ Return the class variable "pos_vect"

    #     get_posVect() -> list[3]
    #     """
    #     return self.pos_vect

    # def get_dirVect(self):
    #     """ Return the class variable "dir_vect"

    #     get_dirVect() -> list[3]
    #     """
    #     return self.dir_vect

    # def get_pincer(self):
    #     """ Return the class variable "pincer"

    #     get_pincer() -> int
    #     """
    #     return self.pincer

    def set_arm(self, pos=None, direct=None, pincer=None):
        """ Sets the arm vectors and calculates the angles and positions.

        set_arm(pos=list[3], direct=list[3]) -> None
        """
        if pos is not None:
            self.pos_vect = pos
        if direct is not None:
            self.dir_vect = direct
        if pincer is not None:
            self.pincer = pincer
        if direct is None and pos is None and pincer is None:
            return
        self.calc_angles()

    def calc_angles(self):
        """ Calculates the angles (in degrees) required for the arm based on
        the end effector position. Also calculates the joints which describe
        the location and direction of the graphics objects.

        calc_angles(Effector) -> None
        """

        angles = []
        joints = []

        pos_vec = self.pos_vect[:]  # Pass by value
        pos_vec[2] -= VERTICAL_OFFSET

        ############################ SOLVE ARM ################################
        try:
            unit_direction = vec.unit(self.dir_vect)

            ### Pincer
            # Calculate angle for the pincer
            pincer_angle = acos((self.pincer)/float(PINCER_OPEN_WIDTH))
            # Get the length of the pincer from the point of rotation to the pincer
            pincer_length = PINCER_CONST_LEN+sin(pincer_angle)*PINCER_ROTATE_LEN

            ### Middle half
            # Calculate the vector to get from the end effector to half of the arm
            half_to_endpoint = vec.scalar_mult(pincer_length, unit_direction)
            # Vector which gets half way down the arm
            half_arm_pos = vec.sub(pos_vec, half_to_endpoint)
            # Magnitude of above vector
            half_arm_pos_mag = vec.mag(half_arm_pos)

            if half_arm_pos_mag > ARM1_LEN + ARM2_LEN:
                return None  # specified position was not possible

            # angle between the first and second main segments of the arm
            theta_arm1_2 = acos((ARM1_LEN**2 + ARM2_LEN**2 - half_arm_pos_mag**2)
                                / (2 * ARM1_LEN * ARM2_LEN))
            # Angle of elevation for half way down the arm
            half_arm_pos_elevation = atan2(half_arm_pos[2],
                                           vec.mag(half_arm_pos[:2]))
            # Elevation of the first arm segment
            seg1_elevation = asin((sin(theta_arm1_2) * ARM2_LEN) /
                                  (half_arm_pos_mag)) + half_arm_pos_elevation
            # Angle that the first half of the arm makes with the ground plane
            half_flat_angle = atan2(half_arm_pos[1], half_arm_pos[0])

            # Calculate directional vectors for the main two arm segments
            new_ratio = cos(seg1_elevation)
            joint2_to_joint3_unit = vec.unit([
                new_ratio*cos(half_flat_angle)*half_arm_pos_mag,
                new_ratio*sin(half_flat_angle)*half_arm_pos_mag,
                sin(seg1_elevation)*half_arm_pos_mag
                ])
            joint2_to_joint3 = vec.scalar_mult(ARM1_LEN, joint2_to_joint3_unit)
            joint3_to_joint4 = vec.sub(half_arm_pos, joint2_to_joint3)

            # Get a vector perpendicular to the direction of half of the arm
            v1 = vec.unit(vec.cross_prod3(joint3_to_joint4, joint2_to_joint3))
            # Project the directional vector onto the plane with normal vector in
            # the direction of the second arm segment
            plane_projection = vec.plane_projection(self.dir_vect,
                                                    joint3_to_joint4)
            # Angle for the axis rotator is the angle between the above two
            # vectors
            axis_rotator = 90 - vec.angle_between(v1, plane_projection)

            joint3_to_joint4_unit = vec.unit(joint3_to_joint4)

            half_flat_angle_degrees = half_flat_angle*180/pi

            end = vec.change_direction([0, 1, 0], self.dir_vect)
            to_end = vec.change_direction([0, 1, 0], joint3_to_joint4_unit)
            to_end = vec.rotate_about_vec(to_end, joint3_to_joint4_unit,
                                          axis_rotator + half_flat_angle_degrees)

            if to_end[0] > 0:
                last_angle = -vec.angle_between(end, to_end)
            else:
                last_angle = vec.angle_between(end, to_end)

            if self.dir_vect[2] > 0:
                last_seg_angle = vec.angle_between(joint3_to_joint4, self.dir_vect)
            else:
                last_seg_angle = -vec.angle_between(joint3_to_joint4, self.dir_vect)


            ############################### ANGLES ################################
            ### 0 Base servo 1 ###
            angles.append(half_flat_angle_degrees / 2)

            ### 1 Base servo 2 ###
            angles.append(angles[0])

            ### 2 First arm segment ###
            angles.append(-seg1_elevation*180/pi + 90)

            ### 3 Second arm segment ###
            angles.append((pi - theta_arm1_2)*180/pi)

            ### 4 Axis rotator ###
            angles.append(axis_rotator)

            ### 5 Last segment ###
            angles.append(last_seg_angle)

            ### 6 Final axis rotator ###
            angles.append(0)

            ### 7 Pincer ###
            angles.append(-pincer_angle*180/pi+30)

            for i in range(len(angles)):
                angles[i] = round(angles[i], 1)

            ############################### JOINTS ################################
            ### Joint offset corrections ###
            half_arm_pos[2] += VERTICAL_OFFSET

            ### 0 Base ###
            joints.append(([0, 0, 0],
                           [0, 0, 1],
                           0))

            ### 1 Base rotator ###
            joints.append(([0, 0, BASE_HEIGHT],
                           [0, 0, 1],
                           half_flat_angle_degrees))

            ### 2 First arm segment ###
            joints.append(([0, 0, VERTICAL_OFFSET],
                           joint2_to_joint3_unit,
                           half_flat_angle_degrees))

            ### 3 Second arm segment ###
            joints.append((vec.add([0, 0, VERTICAL_OFFSET], joint2_to_joint3),
                           vec.unit(joint3_to_joint4),
                           half_flat_angle_degrees))

            ### 4 Axis rotator ###
            joints.append((vec.sub(half_arm_pos,
                                   vec.scalar_mult(AXIS_ROTATOR_LEN,
                                                   joint3_to_joint4_unit)),
                           joint3_to_joint4_unit,
                           angles[4] + half_flat_angle_degrees))

            ### 5 Last segment ###
            joints.append((half_arm_pos, vec.unit(half_to_endpoint), last_angle))

            ### 6 Final axis rotator ###
            joints.append((vec.sub(self.pos_vect,
                                   vec.scalar_mult(pincer_length-AXIS_ROTATOR_LEN,
                                                   unit_direction)),
                           self.dir_vect,
                           last_angle + 90))

            for i in range(len(joints)):
                tup = ([round(x, 1) for x in joints[i][0]],
                       [round(x, 4) for x in joints[i][1]],
                       joints[i][2])
                joints[i] = tup

            self._angles = angles
            self._joints = joints
        except Exception as message:
            print(message)
            return None

    def get_joints(self):
        """ Returns the calculated joints.

        get_joints() -> list(tuple(list[3], list[3], float))
        """
        return self._joints

    def get_angles(self):
        """ Returns the calculated angles.

        get_angles() -> list(float)
        """
        return self._angles

    def __repr__(self):
        return 'Pos: {0}, Dir: {1}, Pinc: {2}, Flp: {3}'.format(
            self.pos_vect, self.dir_vect, self.pincer, self.flip)
