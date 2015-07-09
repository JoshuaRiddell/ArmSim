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

import vector as vec
import threading
from time import sleep
from itertools import chain
import pyglet
from pyglet_gui.manager import Manager
from pyglet_gui.gui import Label
from pyglet_gui.core import Viewer
from pyglet_gui.buttons import Button, OneTimeButton as Otb
from pyglet_gui.containers import GridContainer
from pyglet_gui.text_input import TextInput
import pyglet_gui.constants as pygui_constants

COLUMN_WIDTH = 240


class Sequencer(object):
    def __init__(self, parent, ver_offset=-650, **kwargs):
        ###### Converting the use of self.elements to be able to wrap to a new number of columns
        self.parent = parent
        self.kwargs = kwargs

        self.elements = []

        self.current_column = 0
        self.column_heights = [0]

        self.ver_offset = ver_offset
        self.selected_id = None

    def add_module(self, module_type, args):
        self.elements.append(
            OBJ_DICT[module_type](
                self,
                len(self.elements),
                *args,
                anchor=pygui_constants.ANCHOR_TOP_LEFT,
                offset=(0, 0),
                **self.kwargs
                )
            )

        self.elements[-1].set_offset(self.get_offset(self.elements[-1].height))
        self.radio_select(len(self.elements)-1)

    def load_data(self, data):
        self.clear()
        for element in data:
            self.add_module(element[0], element[1])

    def get_offset(self, height):
        current_height = self.column_heights[self.current_column]
        projected_height = self.ver_offset - current_height - height
        if abs(projected_height) > self.parent.height:
            self.current_column += 1
            self.column_heights.append(0)
        offset = (self.current_column*COLUMN_WIDTH+5,
                  self.ver_offset-self.column_heights[self.current_column]-5)
        self.column_heights[self.current_column] += height + 5
        return offset

    def radio_select(self, ID, update=True):
        for element in self.elements:
            element.deselect()

        self.selected_id = ID
        if ID is not None:
            sequence_obj = self.elements[ID]
            sequence_obj.selected_button.change_state()

            if isinstance(sequence_obj, PositionElement) and update:
                self.parent.update_sliders(*sequence_obj.get_values())

    def update_joints(self, pos=None, direct=None, pincer=None):
        if self.selected_id is None:
            return

        sequence_obj = self.elements[self.selected_id]
        if isinstance(sequence_obj, PositionElement):
            sequence_obj.update_params(pos=pos[:],
                                       direct=direct[:],
                                       pincer=pincer)

    def delete_(self, ID):
        if self.elements[ID].selected_button.is_pressed:
            self.radio_select(None)
        self.elements[ID].delete()
        self.elements.pop(ID)
        for element in self.elements[ID-1:]:
            element.ID = self.elements.index(element)
        if self.selected_id is not None:
            self.selected_id -= 1
        self.repack()

    def repack(self):
        self.current_column = 0
        self.column_heights = [0]
        for element in self.elements:
            offset = self.get_offset(element.height)
            element.set_offset(offset)

    def clear(self):
        for element in self.elements:
            element.delete()
        self.elements = []
        self.current_column = 0
        self.column_heights = [0]
        self.selected_id = None

    def run(self, update_cb):
        self.execute_thread = ExecuteThread(self, update_cb)
        self.execute_thread.start()

    def stop(self):
        if not self.execute_thread.exit:
            self.execute_thread.exit = True
            self.execute_thread.join()


class ExecuteThread(threading.Thread):
    def __init__(self, sequencer, update_cb):
        super().__init__()
        self.update_cb = update_cb
        self.sequencer = sequencer
        self.elements = sequencer.elements
        self.exit = False

    def run(self):
        current_val = None
        for element in self.elements:
            if self.exit:
                break
            current_val = element.execute(current_val, self.update_cb)
            pyglet.clock.schedule_once(lambda x: self.sequencer.radio_select(self.elements.index(element), update=False), 0)
        self.exit = True


class _SequenceElement(Manager):
    def __init__(self, master=None, ID=None, **kwargs):
        self.master = master
        self.ID = ID

        self.selected_button = RadioButton("Select", on_press=self.toggle_selected)

        self.elements = [[Label(self.type),
                         self.selected_button,
                         Otb("X", on_release=self.delete_)]] + self.elements

        self.elements = self.elements + [[Viewer(60, 0), Viewer(125, 0)]]

        elements = GridContainer(self.elements, padding=2)
        super().__init__(elements, **kwargs)

    def toggle_selected(self, state=None):
        if self.selected_button.is_pressed:
            self.master.radio_select(None)
        else:
            self.master.radio_select(self.ID)

    def deselect(self):
        if self.selected_button.is_pressed:
            self.selected_button.change_state()

    def is_different(self, new_values):
        old_values = self.get_values()

        for ov, nv in zip(old_values, new_values):
            i = old_values.index(ov)
            if isinstance(ov, list):
                for oe, ne in zip(ov, nv):
                    if abs(oe-ne) > self.tolerances[i]:
                        return True
            else:
                if abs(ov-nv) > self.tolerances[i]:
                    return True
        return False

    def set_offset(self, offset):
        self.offset = offset
        self.set_position(*self.get_position())

    def delete_(self, event=None):
        self.master.delete_(self.ID)

    def get_path(self):
        return ['sequence']

    def load_graphics(self):
        theme = self.theme[self.get_path()]
        self._border = theme['image'].generate(theme['gui_color'], **self.get_batch('panel'))

    def unload_graphics(self):
        self._border.unload()

    def layout(self):
        self._border.update(self.x, self.y, self.width, self.height)
        super().layout()

    def redraw_labels(self):
        return None

    def get_values(self):
        return None

    def execute(self, prev_val, update_cb):
        sleep(1)
        return prev_val


class PositionElement(_SequenceElement):
    def __init__(self, master, ID, position, direction, pincer, **kwargs):
        self.type = "Node"

        self.position = position
        self.direction = direction
        self.pincer = pincer
        self.tolerances = {0: 3, 1: 0.03, 2: 3}

        self.pos_label = Label(self.get_pos())
        self.dir_label = Label(self.get_dir())
        self.pincer_label = Label(self.get_pincer())

        self.elements = [
            [Label("Pos:"), self.pos_label],
            [Label("Dir:"), self.dir_label],
            [Label("Pinc:"), self.pincer_label]
            ]

        super().__init__(master, ID, **kwargs)

    def update_params(self, pos=None, direct=None, pincer=None):
        new_values = [pos, direct, pincer]
        if self.is_different(new_values):
            self.position = pos
            self.direction = direct
            self.pincer = pincer
            self.redraw_labels()

    def disp_vector(self, vector):
        string = str([round(x) for x in vector])
        return string

    def get_pos(self):
        return self.disp_vector(self.position)

    def get_dir(self):
        return self.disp_vector([x*100 for x in self.direction])

    def get_pincer(self):
        return str(round(self.pincer))

    def get_values(self):
        return [self.position, self.direction, self.pincer]

    def redraw_labels(self):
        self.pos_label.set_text(self.get_pos())
        self.dir_label.set_text(self.get_dir())
        self.pincer_label.set_text(self.get_pincer())

    def execute(self, prev_val, update_cb):
        new_val = self.get_values()
        if prev_val is None:
            update_cb(*new_val)
        else:
            prev_val = list(chain(prev_val[0], prev_val[1], [prev_val[2]]))
            new_val = list(chain(new_val[0], new_val[1], [new_val[2]]))
            differences = []
            zipped = list(zip(prev_val, new_val))
            for i in range(len(prev_val)):
                pv, nv = zipped[i]
                differences.append(nv-pv)

            scaled_differences = []
            for i in range(len(differences)):
                if 2 < i < 6:
                    scaled_differences.append(differences[i] * 100)
                elif i == 6:
                    scaled_differences.append(differences[i] * 2)
                else:
                    scaled_differences.append(differences[i])

            iterations = round(max([abs(x) for x in scaled_differences]))
            time = max([abs(x) for x in scaled_differences]) / 40
            for n in range(iterations):
                for i in range(len(differences)):
                    prev_val[i] += differences[i] / iterations
                update_cb(prev_val[:3], prev_val[3:6], prev_val[6])
                sleep(time/iterations)

        return self.get_values()


class TimeDelay(_SequenceElement):
    def __init__(self, master, ID, time, **kwargs):
        self.type = "Delay"
        self.time = time

        self.time_input = TextInput(text=str(self.time),
                                    length=10,
                                    padding=5,
                                    on_input=self.update_time)

        self.elements = [
            [Label("Time:"), self.time_input]
            ]

        super().__init__(master, ID, **kwargs)

    def get_time(self):
        return str(self.time)

    def update_time(self, text):
        try:
            self.time = float(text)
        except:
            self.time_input.set_text(str(self.time))

    def get_values(self):
        return [self.time]

    def execute(self, prev_val, update_cb):
        sleep(*self.get_values())
        return prev_val


class RadioButton(Button):
    def change_state(self):
        self._is_pressed = not self._is_pressed
        self.reload()
        self.reset_size()

    def on_mouse_press(self, x, y, button, modifiers):
        self._on_press(self._is_pressed)


OBJ_DICT = {
    "Node": PositionElement,
    "Delay": TimeDelay
}
