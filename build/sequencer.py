import seq_elements as sqe
from PyQt4 import QtGui

class SequencerWidget(QtGui.QTableWidget):
    def __init__(self):
        super().__init__()
        self.sequence = []

    def update_values(self):
        self.setColumnCount(3)
        self.setRowCount(5)

        data = {'col1':['1','2','3'], 'col2':['4','5','6'], 'col3':['7','8','9']}

        headers = []
        for i, key in enumerate(data.keys()):
            headers.append(key)
            for j, val in enumerate(data[key]):
                newitem = QtGui.QTableWidgetItem(val)
                self.setItem(i, j, newitem)
        self.setHorizontalHeaderLabels(headers)

        self.resizeColumnsToContents()
        self.resizeRowsToContents()