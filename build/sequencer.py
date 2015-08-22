import seq_elements as sqe
from PyQt4 import QtGui
from threading import Thread


class SequencerWidget(QtGui.QTableWidget):
    def __init__(self, parent):
        super().__init__()
        self.currentCellChanged.connect(self.cell_activated)
        self.parent = parent
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.sequence = []
        self.current_row = -1
        self.running = False

        self.sequence = [
            sqe.NodeElement(0, self.parent.arm)
        ]

        self.update_values()

    def add_seq(self):
        new_element = sqe.NodeElement(len(self.sequence), self.parent.arm)
        new_element.joint_angles = self.parent.arm.joint_angles.copy()
        self.sequence.append(new_element)
        self.update_values()
        self.cell_activated(len(self.sequence)-1)

    def update_values(self):
        header_names = []
        added_headers = set()
        add_header = added_headers.add
        for element in self.sequence:
            header_names.extend(
                [x for x in element.get_headers()
                 if not(x in added_headers or add_header(x))]
                )

        self.setColumnCount(len(header_names))
        self.setHorizontalHeaderLabels(header_names)

        self.setRowCount(len(self.sequence))

        for i, element in enumerate(self.sequence):
            for j, header in enumerate(header_names):
                newitem = QtGui.QTableWidgetItem(element.get_table_value(header))
                self.setItem(i, j, newitem)

        self.resizeRowsToContents()

    def hard_update(self):
        for element in self.sequence:
            element.hard_update(self.parent.arm)

        self.update_values()

    def cell_activated(self, row, col=None, prev_row=None, prev_col=None):
        if self.running:
            return
        print("prev_row", prev_row)
        print("current row", self.current_row)
        if prev_row is None or self.current_row == -1:
            prev_row = self.current_row
        if prev_row != -1:
            self.sequence[prev_row].untie_values(self.parent.arm)
        if row != -1:
            self.sequence[row].get_values(self.parent.arm)
            self.sequence[row].tie_values(self.parent.arm)
            self.parent.arm.calc_forward_kinematics()
        self.update_values()
        self.current_row = row

    def run(self):
        # print("run", self.running)
        if self.running:
            return
        self.cell_activated(-1, -1)
        self.running = True
        execute_thread = ExecuteThread(self, self.sequence, self.parent.arm)
        execute_thread.start()

class ExecuteThread(Thread):
    def __init__(self, parent, sequence, arm):
        super().__init__()
        self.parent = parent
        self.sequence = sequence
        self.arm = arm

    def run(self):
        self.sequence[0].init_execute(self.arm)

        for element in self.sequence:
            element.execute(self.arm)

        parent = self.parent
        parent.running = False