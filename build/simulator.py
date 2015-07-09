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

import pyglet
from file_io import load_config_file
from pyglet.gl import *
import graphics

SIM_SETTINGS = load_config_file('simulator')


class SimulationWindow(pyglet.window.Window):
    def __init__(self, settings, joints):

        ### Create instance of the window ###
        user_settings = graphics.load_config_file('graphics')
        self.view_settings = graphics.load_config_file('view')

        try:
            # Try with multisampling (antialiasing)
            if SIM_SETTINGS["force_no_multisampling"]:
                raise pyglet.window.NoSuchConfigException
            config = Config(sample_buffer=user_settings["sample_buffer"],
                            samples=user_settings["samples"],
                            depth_size=user_settings["depth_size"],
                            double_buffer=user_settings["double_buffer"])
            super().__init__(*settings[:2],
                             resizable=True,
                             caption="ArmSim - Simulator",
                             config=config)
        except pyglet.window.NoSuchConfigException:
            # No multisampling if not possible on current hardware
            super().__init__(*settings[:2],
                             caption="ArmSim - Simulator",
                             resizable=True)
        self.set_location(*settings[2:])
        self.set_minimum_size(320, 320)

        ### Initialise resources for displaying graphics ###
        self.cam = graphics.Camera([235, -227, 311],
                                   [-9, 58, 83],
                                   [-0.3379, 0.3931, 0.8551])

        ordered_names = ['base',
                         'joint1',
                         'joint2',
                         'joint3',
                         'joint4',
                         'joint5',
                         'joint6']
        self.parts = []
        for part_name in ordered_names:
            self.parts.append(graphics.GraphicsPart(part_name))

        self.activated = True
        self.update_joints(joints)
        graphics.initialise()

    def on_resize(self, width, height):
        """ Is called when the window is resized. Ensures viewport and projection
        are set correctly for the current window size.

        on_resize(int, int) -> None
        """
        user_settings = self.view_settings
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(user_settings['fov'], width / float(height),
                       user_settings['near_limit'], user_settings['far_limit'])
        glMatrixMode(GL_MODELVIEW)
        return pyglet.event.EVENT_HANDLED

    def on_draw(self, event=None):
        """ Draws the parts in the simulation window.

        on_draw(list(GraphicsPart), Camera) -> None
        """
        self.clear()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for graphics_part in self.parts:
            graphics_part.draw(self.cam.get_cam())

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """ Called when the mouse wheel is scrolled over the window.
        """
        self.cam.user_zoom(scroll_y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if modifiers == SIM_SETTINGS["shift"]:
            self.cam.user_pan(dx, dy)
        else:
            self.cam.user_orbit(dx, dy)

    def update_joints(self, joints):
        for joint in joints:
            i = joints.index(joint)
            self.parts[i].update_pos(*joint)

    def set_visible(self, visible):
        super().set_visible(visible)
        self.on_resize(self.width, self.height)
