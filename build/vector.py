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


from math import sqrt, cos, sin, acos, pi

VERTICAL = [0, 0, 1]


def mag(vector):
    """ Returns the magnitude of the list as per vector arithmetic.

    mag(list(float)) -> float
    """
    return sqrt(sum(element**2 for element in vector))


def add(vector1, vector2):
    """ Returns the sum of the two specified vectors elementwise.

    add(list(float), list(float)) -> list(float)
    """
    return [a + b for a, b in zip(vector1, vector2)]


def sub(vector1, vector2):
    """ Returns vector1 - vector2, elementwise.

    sub(list(float), list(float)) -> list(float)
    """
    return [a - b for a, b in zip(vector1, vector2)]


def scalar_mult(scalar, vector):
    """ Return the result of scalar multiplied by the vector

    scalar_mult(float, list(float)) -> list(float)
    """
    return [scalar*element for element in vector]


def dot_prod(vector1, vector2):
    """ Return the dot product of two vectors.

    dot_prod(list(float), list(float)) -> float
    """
    return sum([a * b for a, b in zip(vector1, vector2)])


def cross_prod3(vector1, vector2):
    """ Return the cross product of two vectors.

    cross_prod(list[3](float), list[3](float)) -> list[3](float)

    This is limited to 3D vectors as the determinant of a 3x3 matrix is used.
    """
    return [vector1[1]*vector2[2]-vector1[2]*vector2[1],
            -(vector1[0]*vector2[2]-vector1[2]*vector2[0]),
            vector1[0]*vector2[1]-vector1[1]*vector2[0]]


def unit(vector):
    """ Return the unit vector corresponding with vector.
    """
    magnitude = mag(vector)
    return [element/magnitude for element in vector]


def angle_between(vector1, vector2):
    """ Return the angle between the two vectors in degrees. Uses definition
    of dot product
    """
    numerator = dot_prod(vector1, vector2)
    denominator = mag(vector1)*mag(vector2)
    return acos(numerator/float(denominator)) * 180 / pi


def matrix_mult(matrix, vector):
    """ Returns transformation matrix multiplied by the specified vector.
    """
    return_vector = []

    for i in range(len(vector)):
        result = 0
        for j in range(len(matrix)):
            result += matrix[i][j] * vector[j]
        return_vector.append(result)
    return return_vector


def rotate_about_vec(vector, axis, theta):
    """ Rotates 'vector' about 'axis', 'theta' degrees.

    rotate_about_vec(list[3](float), list[3](float), float) -> list[3](float)
    """
    axis = unit(axis)
    theta = theta / 180 * pi
    a = cos(theta/2)
    b, c, d = scalar_mult(-sin(theta/2), axis)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    rot_mat = [[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
               [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
               [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]]
    return matrix_mult(rot_mat, vector)


def plane_projection(vector, plane_normal):
    """ Projects 'vector' onto the plane with normal, 'plane_normal'.

    plane_projection(list[3](float), list[3](float)) -> list[3](float)
    """
    a = dot_prod(vector, plane_normal) / \
        mag(plane_normal)**2
    scaled_normal = scalar_mult(a, plane_normal)

    return sub(vector, scaled_normal)


def change_direction(vector, direction):
    """ Imitates the vector translation performed in the graphics module.

    change_direction(list[3](float), list[3](float)) -> list[3](float)
    """
    axis = cross_prod3(VERTICAL, direction)
    if mag(axis) == 0:
        axis = [0 for x in range(len(axis)-1)] + [1]
        angle = 0
    else:
        angle = angle_between(VERTICAL, direction)
    return rotate_about_vec(vector, axis, angle)
