from os.path import join, realpath, dirname, isfile, splitext, exists
import os
import ast
from PyQt4 import QtGui

CONFIG_DIRECTORY = 'config'
CONFIG_EXT = '.conf'
SEQUENCES_DIRECTORY = 'sequences'
MODELS_DIRECTORY = 'models'

ARM_MARKER = ">>> "

APP_DIR = dirname(realpath(__file__))


class FileManager(object):
    def __init__(self, parent, arm_file, arms_dir):
        self.parent = parent
        self.current_sequence = None
        self.arm_data = {}

        if isfile(arm_file):
            self.arm_file = arm_file
        elif isfile(join(APP_DIR, arms_dir, splitext(arm_file)[0],
                         arm_file)):
            self.arm_file = join(APP_DIR, arms_dir, splitext(arm_file)[0],
                                 arm_file)
        else:
            QtGui.QMessageBox.warning(
                self.parent, "Invalid Arm File",
                "The default arm file specified in config.conf does not" +
                " exist. Please load an arm file from the file menu")
            self.arm_file = None

        if self.arm_file is not None:
            self._update_directories()
        else:
            self.current_dir = APP_DIR
            self.sequences_dir = None

    def open_arm(self):
        self.arm_file = QtGui.QFileDialog.getOpenFileName(
            self.parent,
            "Open arm file", self.current_dir,
            "Arm Files (*.arm);;All Files (*)")
        if not self.arm_file:
            return

        try:
            fd = open(self.arm_file)
            arm_dictionary = {}
            current_field = ""
            for line in fd:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                if line.startswith(ARM_MARKER):
                    field_list = line[len(ARM_MARKER):].split(" ")
                    if len(field_list) == 2:
                        current_field = field_list[1]
                        arm_dictionary[current_field] = []
                    else:
                        current_field = ""
                    continue
                try:
                    arm_dictionary[current_field].append(eval(line))
                except NameError:
                    arm_dictionary[current_field].append(line)
            fd.close()
            self.arm_data = arm_dictionary
            self._update_directories()
            self.parent.load_arm(self.arm_data)
        except Exception as error:
            QtGui.QMessageBox.warning(
                self.parent, "Invalid Arm File",
                "The arm file you have loaded has invalid contents \n\n" +
                "Error: \n" + str(error))

    def new_seq(self):
        if self._directory_check() is None:
            return

        self.current_sequence = QtGui.QFileDialog.getSaveFileName(
            self.parent,
            "New sequence file", self.sequences_dir,
            "Sequence Files (*.seq);;All Files (*)")
        if not self.current_sequence.endswith(".seq"):
            self.current_sequence += ".seq"
        fd = open(self.current_sequence, "w")
        fd.close()
        #self.parent.sequencer.load_data([])

    def open_seq(self):
        if self._directory_check() is None:
            return
        self.current_sequence = QtGui.QFileDialog.getOpenFileName(
            self.parent,
            "Open sequence file", self.sequences_dir,
            "Sequence Files (*.seq);;All Files (*)")
        fd = open(self.current_sequence, "rU")

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
            QtGui.QMessageBox.warning(self.parent, "Invalid File",
                "The file you have chosen has invalid contents.")

        fd.close()
        #self.parent.sequencer.load_data(sequencer_list)

    def save_seq(self):
        if self.current_sequence is None:
            self.save_as()
            return

        try:
            fd = open(self.current_sequence, "w")
        except:
            QtGui.QMessageBox.warning(self.parent, "Invalid File",
                "File save failed, chances are you don't have write access.")
            self.save_as()
            return

        types = []
        for element in self.parent.sequencer.current_sequence:
            types.append(len(element.type))
        format_string = "{0:<" + str(max(types) + 5) + "}{1}"
        for element in self.parent.sequencer.current_sequence:
            fd.write(format_string.format(element.type,
                                          element.get_values()) + "\n")
        fd.close()

    def save_seq_as(self):
        if not exists(self.sequences):
            os.mkdir(self.sequences)
        self.current_sequence = QtGui.QFileDialog.getSaveFileName(self.parent,
                                "Save sequence file", self.sequences,
                                "Sequence Files (*.seq);;All Files (*)")
        if not self.current_sequence.endswith(".seq"):
            self.current_sequence += ".seq"
        self.save()

    def get_arm_data(self):
        return self.arm_data

    def get_model_file(self, model_name):
        file_path = join(self.models_dir, model_name)
        if isfile(file_path):
            return file_path
        else:
            return None

    def _directory_check(self):
        if self.sequences_dir is None:
            QtGui.QMessageBox.warning(self.parent, "Arm File Not Loaded",
                "You must first load an arm file before you can use this" +
                " function")
            return
        return True

    def _update_directories(self):
        self.current_dir = dirname(realpath(self.arm_file))
        self.sequences_dir = join(self.current_dir, SEQUENCES_DIRECTORY)
        if not exists(self.sequences_dir):
            os.mkdir(self.sequences_dir)
        self.models_dir = join(self.current_dir, MODELS_DIRECTORY)
        if not exists(self.models_dir):
            os.mkdir(self.models_dir)


def load_config(filename):
    """ Loads menu list
    """
    fd = open(join(APP_DIR, CONFIG_DIRECTORY, filename), 'rU')
    menu_string = ""
    for line in fd:
        menu_string += line
    return menu_string
