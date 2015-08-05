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

        self.sequence = [
            sqe.NodeElement(1, self.parent.arm),
            sqe.NodeElement(2, self.parent.arm),
            sqe.NodeElement(3, self.parent.arm),
            sqe.NodeElement(4, self.parent.arm),
            sqe.NodeElement(5, self.parent.arm),
            sqe.NodeElement(6, self.parent.arm),
            sqe.NodeElement(7, self.parent.arm),
            sqe.NodeElement(8, self.parent.arm),
            sqe.NodeElement(9, self.parent.arm),
            sqe.NodeElement(10, self.parent.arm),
            sqe.NodeElement(11, self.parent.arm)
        ]

        self.update_values()

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

    def cell_activated(self, row, col, prev_row, prev_col):
        if prev_row != -1:
            self.sequence[prev_row].untie_values(self.parent.arm)
        self.sequence[row].get_values(self.parent.arm)
        self.sequence[row].tie_values(self.parent.arm)
        self.parent.arm.calc_forward_kinematics()
        self.update_values()

    def run(self):
        execute_thread = ExecuteThread(self.sequence, self.parent.arm)
        execute_thread.start()

class ExecuteThread(Thread):
    def __init__(self, sequence, arm):
        super().__init__()
        self.sequence = sequence
        self.arm = arm

    def run(self):
        for element in self.sequence:
            element.execute(self.arm)