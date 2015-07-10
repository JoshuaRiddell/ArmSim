import os
import ast
from PyQt4 import QtGui

CONFIG_DIRECTORY = 'config'
SEQUENCES_DIRECTORY = 'Sequences'


class FileManager(object):
    def __init__(self, parent):
        self.parent = parent
        self.cd = os.path.dirname(os.path.realpath(__file__))
        self.sequences = os.path.join(self.cd, SEQUENCES_DIRECTORY)
        self.current_file = None

    def open(self):
        if not os.path.exists(self.sequences):
            os.mkdir(self.sequences)
        fname = QtGui.QFileDialog.getOpenFileName(self.parent,
                                "Open sequence file", self.sequences,
                                "Sequence Files (*.seq);;All Files (*)")
        if not fname:
            return
        fd = open(fname, "rU")

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
            raise
        except:
            fd.close()
            QtGui.QMessageBox.warning(self.parent, "Invalid File",
                "The file you have chosen has invalid contents.")
        fd.close()
        self.parent.sequencer.load_data(sequencer_list)

    def save(self):
        if self.current_file is None:
            self.save_as()
            return

        try:
            fd = open(self.current_file, "w")
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
            fd.write(format_string.format(element.type, element.get_values()) + "\n")
        fd.close()

    def save_as(self):
        if not os.path.exists(self.sequences):
            os.mkdir(self.sequences)
        self.current_file = QtGui.QFileDialog.getOpenFileName(self.parent,
                                "Save sequence file", self.sequences,
                                "Sequence Files (*.seq);;All Files (*)")
        if not self.current_file.endswith(".seq"):
            self.current_file += ".seq"
        self.save()
