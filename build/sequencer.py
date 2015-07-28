import seq_elements as sqe
from PyQt4 import QtGui


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
            sqe.NodeElement(3, self.parent.arm)
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

        data = {'col1':['1','2','3'], 'col2':['4','5','6'], 'col3':['7','8','9']}

        headers = []
        for i, key in enumerate(data.keys()):
            headers.append(key)
            for j, val in enumerate(data[key]):
                newitem = QtGui.QTableWidgetItem(val)
                self.setItem(i, j, newitem)

        self.resizeColumnsToContents()
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
