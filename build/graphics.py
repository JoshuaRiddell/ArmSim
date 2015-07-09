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

import os
import vector as vec
from file_io import *
from math import sin, cos, atan2, pi

import pyglet
from pyglet.gl import *
from pyglet_obj.obj_batch import OBJ

###############################################################################
# Global constants
###############################################################################


MODELS_DIRECTORY = 'models'


def initialise():
    """ Sets up OpenGL to display simulation.

    initialise() -> None
    """
    glClearColor(0, 0, 0, 1)
    glEnable(GL_DEPTH_TEST)

    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) # wireframe option

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_array(0, -200, 300, 0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, GLfloat_array(.5, .5, 1, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, GLfloat_array(1, 1, 1, 1))
    glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_array(0, 200, 300, 0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, GLfloat_array(.5, .5, 1, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, GLfloat_array(1, 1, 1, 1))


class Camera(object):
    """ Class which handles the camera """

    def __init__(self, position, focus, up):
        self._position = position
        self._focus = focus
        self._up = up

        self._settings = load_config_file('camera')

    def user_pan(self, dx, dy):
        """ Pans the camera based on passed mouse movements.

        user_pan(int, int) -> None
        """
        sensetivity = self._settings["pan_sensetivity"]
        focus_to_cam = vec.sub(self._position, self._focus)
        x = [self._position, self._focus]
        for i in range(len(x)):
            x[i] = vec.add(x[i], vec.scalar_mult(-sensetivity*dy,
                                                 vec.unit(self._up)))
            x[i] = vec.add(x[i], vec.scalar_mult(sensetivity*dx,
                    vec.unit(vec.cross_prod3(focus_to_cam, self._up))))
        self._position, self._focus = x

    def user_orbit(self, dx, dy):
        """ Orbits the camera based on passed mouse movements.

        user_pan(int, int) -> None

        Note: h denotes horizontal and v denotes vertical
        """
        sensetivity = self._settings["orbit_sensetivity"]
        focus_to_cam = vec.sub(self._position, self._focus)

        dist_to_focus_h = vec.mag(focus_to_cam[:2])
        dist_to_focus = vec.mag(focus_to_cam)

        angleh = atan2(focus_to_cam[1], focus_to_cam[0])
        anglev = atan2(focus_to_cam[2], dist_to_focus_h)

        angleh -= sensetivity*dx
        anglev -= sensetivity*dy

        if anglev >= pi/2-0.01:
            anglev = pi/2-0.01
        if anglev <= -pi/2-0.01:
            anglev = -pi/2-0.01

        focus_to_cam = [cos(angleh)*cos(anglev)*dist_to_focus,
                        sin(angleh)*cos(anglev)*dist_to_focus,
                        sin(anglev)*dist_to_focus]

        self._up = vec.unit(vec.scalar_mult(-1, vec.cross_prod3(focus_to_cam,
                            vec.cross_prod3(focus_to_cam, vec.VERTICAL))))
        self._position = vec.add(self._focus, focus_to_cam)

    def user_zoom(self, scroll_y):
        """ Zooms the camera based on passed mouse movements.

        user_zoom(int) -> None
        """
        sensetivity = self._settings["zoom_sensetivity"]
        u_focus_to_cam = vec.unit(vec.sub(self._position, self._focus))
        self._position = vec.add(self._position,
                                 vec.scalar_mult(-scroll_y*sensetivity,
                                                 u_focus_to_cam))
        if vec.mag(vec.sub(self._position, self._focus)) <= 1:
            self._focus = vec.add(self._position,
                                  vec.scalar_mult(-1, u_focus_to_cam))
        return None

    def get_cam(self):
        """ Returns a list of values in the format required for many OpenGL
        functions.

        get_cam() -> list[9](float)
        """
        return self._position + self._focus + self._up


class GraphicsPart(object):
    """ Parent class for definitions of the vertices for a openGL shape.

    GraphicsPart() -> None
    """

    def __init__(self, filename, trans=[0, 0, 0], direct=[0, 0, 1]):
        self._trans = trans
        self._direct = direct
        self._axis_rotation = 0

        self.name = filename
        self.obj = OBJ(os.path.join(os.getcwd(), MODELS_DIRECTORY, filename
                       + ".obj"))

        self._batch = pyglet.graphics.Batch()
        self.obj.add_to(self._batch)

    def update_pos(self, trans=None, direct=None, angle=None):
        """ Updates variables describing the position of the current object.

        update_pos(list(float, float, float), list(float, float, float))
                   -> None
        """
        if trans is not None:
            self._trans = trans
        if direct is not None:
            self._direct = direct
        if angle is not None:
            self._axis_rotation = angle

    def draw(self, camera):
        """ Draw this part using OpenGL. Note, does not clear any buffers.

        draw(float, float, float, float, float, float, float, float, float)
             -> None
        """
        axis = vec.cross_prod3(vec.VERTICAL, self._direct)
        angle = vec.angle_between(vec.VERTICAL, self._direct)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(*camera)
        glTranslatef(*self._trans)
        glRotatef(angle, *axis)
        glRotatef(self._axis_rotation, *vec.VERTICAL)
        self._batch.draw()
        glLoadIdentity()

    def __repr__(self):
        return self.type


###############################################################################
# Misc functions
###############################################################################


def GLfloat_array(*args):
        return (GLfloat * len(args))(*args)


def GLint_array(*args):
        return (GLint * len(args))(*args)
