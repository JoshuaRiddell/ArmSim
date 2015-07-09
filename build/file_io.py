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
import ast
import pyglet
from pyglet_gui.gui import PopupConfirm, PopupMessage, Frame, Label
from pyglet_gui.containers import HorizontalContainer, VerticalContainer
from pyglet_gui.text_input import TextInput
from pyglet_gui.manager import Manager
from pyglet_gui.buttons import Button


CONFIG_DIRECTORY = 'config'
SEQUENCES_DIRECTORY = 'sequences'

###############################################################################
# Configuration functions
###############################################################################


def load_config_file(filename):
    """ Returns a dictionary containing the configuration elements in the file:
    'filename' contained in the subfolder of the cwd: 'folder'.

    load_config_file(str, str) -> dict
    """
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, CONFIG_DIRECTORY))
    settings_file = open(filename, "rU")
    usr_settings = {}
    for line in settings_file:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        split_line = [x for x in line.split(" ") if x != ""]
        try:
            usr_settings[split_line[0]] = int(split_line[1])
        except ValueError:
            usr_settings[split_line[0]] = float(split_line[1])

    settings_file.close()
    os.chdir(cwd)
    return usr_settings


def load_servo_poi(filename):
    """ Returns a list of lists containing the configuration elements in the
    file: 'filename' contained in the subfolder of the cwd: 'folder'.

    load_config_file(str, str) -> dict
    """
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, CONFIG_DIRECTORY))
    settings_file = open(filename, "rU")
    data = []
    for line in settings_file:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        else:
            split_line = [int(x) for x in line.split(" ") if x != ""]
            data.append(split_line[1:])
    settings_file.close()
    os.chdir(cwd)
    return data


class SequencerData(object):
    def __init__(self, **kwargs):
        self.window_kwargs = kwargs
        self.filename = None

    def write_sequence(self, sequencer_list, force_filename=False, returned_filename=None):
        if returned_filename is not None:
            self.filename = returned_filename
        if force_filename or self.filename is None:
            PopupTextInput(on_ok=lambda x: self.write_sequence(sequencer_list,
                                                               returned_filename=x),
                           **self.window_kwargs)
            return
        cwd = os.getcwd()
        directory = os.path.join(cwd, SEQUENCES_DIRECTORY)
        try:
            os.chdir(directory)
        except:
            os.mkdir(directory)
            os.chdir(directory)
        fd = open(self.filename, "w")
        for element in sequencer_list:
            fd.write("{0:<12}{1}".format(element.type, element.get_values()) + "\n")
        fd.close()
        os.chdir(cwd)

    def read_sequence(self, returned_filename=None, cb=None):
        if cb is not None:
            self.cb = lambda x: cb(x)
        if returned_filename is not None:
            self.filename = returned_filename
        else:
            PopupTextInput(on_ok=self.read_sequence, **self.window_kwargs)
            return
        cwd = os.getcwd()
        directory = os.path.join(cwd, SEQUENCES_DIRECTORY)
        try:
            os.chdir(directory)
            fd = open(self.filename, "rU")
        except:
            fd.close()
            os.chdir(cwd)
            PopupMessage(text="File does not exist", **self.window_kwargs)
            return

        try:
            sequencer_list = []
            for line in fd:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                line = line.replace(" ", "")
                split_line = line.split(sep="[", maxsplit=1)
                if len(split_line) != 2:
                    raise
                split_line[1] = ast.literal_eval("[" + split_line[1])
                sequencer_list.append(split_line)
        except:
            fd.close()
            os.chdir(cwd)
            PopupMessage(text="File has invalid contents", **self.window_kwargs)
            return
        fd.close()
        os.chdir(cwd)
        self.cb(sequencer_list)


class PopupTextInput(PopupConfirm):
    def __init__(self, text="Please type a filename:", ok="Ok", cancel="Cancel",
                 window=None, batch=None, group=None, theme=None,
                 on_ok=None, on_cancel=None):
        self._input = TextInput(text="untitled.seq")

        def on_ok_click(_):
            if on_ok is not None:
                on_ok(self._input.get_text())
            self.delete()

        def on_cancel_click(_):
            self.delete()

        Manager.__init__(self, content=Frame(
            VerticalContainer([
                Label(text),
                self._input,
                HorizontalContainer([Button(ok, on_press=on_ok_click),
                                     None,
                                     Button(cancel, on_press=on_cancel_click)]
                )])
        ), window=window, batch=batch, group=group, theme=theme, is_movable=False)
