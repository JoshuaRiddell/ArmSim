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


from server import NetworkHandler, HOST, PORT
from sequencer import Sequencer
import sys
import math
import graphics
import arm
import pyglet
from pyglet.gl import *
from file_io import SequencerData

from theme import theme
from simulator import SimulationWindow
from pyglet_gui.gui import Label
from pyglet_gui.manager import Manager
from pyglet_gui.containers import VerticalContainer, HorizontalContainer,\
    GridContainer
from pyglet_gui.option_selectors import Dropdown
import pyglet_gui.constants as pygui_constants
from pyglet_gui.sliders import HorizontalSlider
from pyglet_gui.buttons import Checkbox, OneTimeButton as Otb
from pyglet_gui.core import Viewer

import toolbar_menu as tbm

##
TOP_PADDING = 10
RIGHT_PADDING = 20
LEFT_PADDING = 20
SEQUENCER_OFFSET = 430

WINDOW_LOCATION = (8, 30)
MINIMUM_SIZE = (460, 700)
HEIGHT_OFFSET = 80

##

###############################################################################
# Pyglet main window definitions
###############################################################################


class SequencerWindow(pyglet.window.Window):
    def __init__(self):
        display = pyglet.window.Display()
        default_screen = display.get_default_screen()

        ### Init main window ###
        super().__init__(int(default_screen.width/2-15),
                         default_screen.height-HEIGHT_OFFSET,
                         resizable=True,
                         vsync=True,
                         caption="ArmSim")
        self.set_location(*WINDOW_LOCATION)
        self.set_minimum_size(*MINIMUM_SIZE)
        self.batch = pyglet.graphics.Batch()
        window_kwargs = {"window":        self,
                         "theme":         theme.get_theme(),
                         "batch":         self.batch,
                         "is_movable":    False}

        ### Main Toolbar ###
        Manager(HorizontalContainer(
                [tbm.MenuDropdown(["File", "Open", "Save", "Save As...",
                                   "Quit"], on_select=self.file_menu)],
                padding=15),
                anchor=pygui_constants.ANCHOR_TOP_LEFT,
                offset=(LEFT_PADDING, -TOP_PADDING),
                **window_kwargs)

        ### Quickbuttons ###
        Manager(HorizontalContainer([
            Otb("Save", on_release=lambda x: self.quickbuttons("Save")),
            Otb("Run...", on_release=lambda x: self.quickbuttons("Run...")),
            Otb("STOP", on_release=lambda x: self.quickbuttons("STOP"))],
            padding=10),
            anchor=pygui_constants.ANCHOR_TOP_LEFT,
            offset=(LEFT_PADDING, -TOP_PADDING-50),
            **window_kwargs)

        ### Manipulator panel ###
        Manager(Label("Manipulator", font_size=20, italic=True),
                anchor=pygui_constants.ANCHOR_TOP_LEFT,
                offset=(LEFT_PADDING, -TOP_PADDING-90),
                **window_kwargs)

        self.pos_slider = [100, 0, 300]
        self.dir_slider = [0, 0, 1]
        self.pincer = 40

        bar_width = 500
        self.slider_settings = []
        for i in range(3):
            if i == 0:
                self.sliders = [[Label("Position: ")]]
                a_dict = {0: ['x', -250, 250, self.pos_slider[0]],
                          1: ['y', -250, 250, self.pos_slider[1]],
                          2: ['z', 100, 400, self.pos_slider[2]],
                          'c': lambda a: lambda x, a=a: self.slider_cb(0,x,a)}
            elif i == 1:
                self.sliders.append([Label("Direction:")])
                a_dict = {0: ['x', -1, 1, self.dir_slider[0]],
                          1: ['y', -1, 1, self.dir_slider[1]],
                          2: ['z', -1, 1, self.dir_slider[2]],
                          'c': lambda a: lambda x, a=a: self.slider_cb(1,x,a)}

            elif i == 2:
                self.sliders.append([Label("Pincer:")])
                a_dict = {0: ['x', 0, 50, 40],
                          'c': lambda a: lambda x, a=a: self.slider_cb(2,x,a)}

            for j in range(len(a_dict)-1):
                self.sliders.append([Label(a_dict[j][0], font_size=10),
                                HorizontalSlider(width=bar_width,
                                                 min_value=a_dict[j][1],
                                                 max_value=a_dict[j][2],
                                                 value=a_dict[j][3],
                                                 on_set=a_dict['c'](j),
                                                 steps=50
                                                 )])

                self.slider_settings.append(a_dict[j][1:3])

        self.slider_container = GridContainer(self.sliders + [[Viewer(80, 0)]],
                                              padding=0)

        Manager(self.slider_container,
                anchor=pygui_constants.ANCHOR_TOP_LEFT,
                offset=(LEFT_PADDING, -TOP_PADDING-125),
                **window_kwargs)

        # Get rid of slider titles so we have a list with just the sliders in
        for i in [0, 3, 6]:
            self.sliders.pop(i)

        feedback_container = VerticalContainer([
            Label("Feedback", font_size=20, italic=True),
            Checkbox(label="Simulator Window", is_pressed=True,
                     on_press=self.simulator_toggle),
            Checkbox(label="Raspberry Pi Mirror",
                     on_press=self.rpi_network_toggle)],
            align=pygui_constants.HALIGN_RIGHT)

        Manager(feedback_container,
                anchor=pygui_constants.ANCHOR_TOP_RIGHT,
                offset=(-RIGHT_PADDING, -TOP_PADDING-135),
                **window_kwargs)

        self.sequencer_add_dropdown = Dropdown(["Node", "Delay"])

        sequencer_actions_container = VerticalContainer([
            Label("Sequencer Actions", font_size=20, italic=True),
            Otb(label="Clear", on_release=lambda x: self.clear_sequencer()),
            HorizontalContainer([Otb(
                label="Add",
                on_release=lambda x: self.sequencer_add(
                    self.sequencer_add_dropdown._selected)),
                self.sequencer_add_dropdown])],
            align=pygui_constants.HALIGN_RIGHT)

        Manager(sequencer_actions_container,
                anchor=pygui_constants.ANCHOR_TOP_RIGHT,
                offset=(-RIGHT_PADDING, -TOP_PADDING-270),
                **window_kwargs)

        Manager(Label("Sequencer", font_size=20, italic=True),
                anchor=pygui_constants.ANCHOR_TOP_LEFT,
                offset=(LEFT_PADDING, -SEQUENCER_OFFSET),
                **window_kwargs)

        self.sequencer = Sequencer(self, ver_offset=-SEQUENCER_OFFSET-40,
                                   **window_kwargs)

        self.server = NetworkHandler(HOST, PORT)

        self.effector = arm.Effector(self.pos_slider,
                                     self.dir_slider,
                                     self.pincer)

        sim_window_settings = (int(default_screen.width/2-15),
                               default_screen.height-80,
                               int(default_screen.width/2+8),
                               30)
        self.sim_win = SimulationWindow(sim_window_settings,
                                        self.effector.get_joints())

        self.sequencer_data = SequencerData(window=self,
                                            batch=self.batch,
                                            theme=theme.get_theme())

    def slider_cb(self, slider_id, value, axis):
        if slider_id == 0:
            self.pos_slider[axis] = value
        elif slider_id == 1:
            self.dir_slider[axis] = value
        else:
            self.pincer = value
        self.update_joints(pos=self.pos_slider,
                           direct=self.dir_slider,
                           pincer=self.pincer)
        self.sequencer.update_joints(pos=self.pos_slider,
                                     direct=self.dir_slider,
                                     pincer=self.pincer)

    def update_sliders(self, pos, direct, pincer):
        values = pos + direct + [pincer]
        for i in range(7):
            settings = self.slider_settings[i]
            self.sliders[i][1].set_knob_pos((values[i]-settings[0]) /
                                            (settings[1]-settings[0]))

    def update_joints(self, pos=None, direct=None, pincer=None, update_all=None):
        self.effector.set_arm(pos=pos, direct=direct, pincer=pincer)

        if self.sim_win.activated:
            self.sim_win.update_joints(self.effector.get_joints())

        if self.server.is_connected:
            self.server.send_angles(self.effector.get_angles(), update_all)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        for i in range(7):
            slider = self.sliders[i][1]
            slider.min_width = width - (400 + RIGHT_PADDING)
            slider.reset_size()
            slider.reload()
        self.slider_container._update_max_vectors()
        self.slider_container.reset_size()
        self.sequencer.repack()

    def clear_sequencer(self):
        self.sequencer.clear()

    def rpi_network_toggle(self, activate):
        if activate:
            self.server.connect()
        else:
            self.server.disconnect()

    def sequencer_add(self, ID):
        if ID == "Node":
            args = (self.pos_slider[:],
                    self.dir_slider[:],
                    self.pincer)
        elif ID == "Delay":
            args = (1, )
        self.sequencer.add_module(ID, args)

    def simulator_toggle(self, activate):
        self.sim_win.set_visible(activate)
        self.on_resize(self.width, self.height)

    def quickbuttons(self, name):
        if name == "Save":
            self.sequencer_data.write_sequence(self.sequencer.elements)
        elif name == "Run...":
            self.sequencer.run(self.update_joints)
        elif name == "STOP":
            self.sequencer.stop()

    def file_menu(self, name):
        if name == "Open":
            self.sequencer_data.read_sequence(cb=self.sequencer.load_data)
        elif name == "Save":
            self.sequencer_data.write_sequence(self.sequencer.elements)
        elif name == "Save As...":
            self.sequencer_data.write_sequence(self.sequencer.elements,
                                               force_filename=True)
        elif name == "Quit":
            self.on_close()

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def update(self, event=None):
        if self.sim_win.activated:
            self.sim_win.on_draw()

    def on_close(self):
        pyglet.app.exit()


def main():
    seq_win = SequencerWindow()
    pyglet.clock.schedule_interval(seq_win.update, 1/60)
    pyglet.clock.schedule_interval(
        lambda dt: seq_win.update_joints(update_all=True), 1)
    pyglet.app.run()

if __name__ == '__main__':
    main()
