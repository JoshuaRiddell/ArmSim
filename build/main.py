# http://doc.qt.io/qt-5/qmlfirststeps.html

import file_io
import arm
import simulator
from controls import Angle

import sys

from PyQt4 import QtGui, QtCore, QtOpenGL

MENU_FILE = 'menus.conf'
CONFIG_FILE = 'config.conf'
CONTROLS_FILE = 'controls.conf'

CONFIG = eval(file_io.load_config(CONFIG_FILE))


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.file_manager = file_io.FileManager(self,
                                                CONFIG["def_arm"],
                                                CONFIG["def_arms_directory"])
        self.arm = arm.Arm()
        self.arm_data = None
        self.sim_widget = simulator.SimWidget()

        self.initMenus()
        self.initGui()
        self.setStyleSheet("QSplitter::handle {background-color: rgb(150,150,150)}")

        self.setWindowTitle("ArmSim")
        self.setGeometry(-1500, 100, 900, 600)
        # self.show()
        self.showMaximized()

    def initMenus(self):
        menu_items = eval(file_io.load_config(MENU_FILE))
        menubar = self.menuBar()

        for menu in menu_items:
            newMenu = menubar.addMenu(menu[0])
            for action in menu[1]:
                if action["name"] == "sep":
                    newMenu.addSeparator()
                    continue
                newAction = QtGui.QAction(action["name"], self)
                newAction.setShortcut(action["shortcut"])
                newAction.setStatusTip(action["tip"])
                newAction.triggered.connect(action["cb"])
                newMenu.addAction(newAction)

    def initGui(self):
        ### Begin Controls
        self.controls_area = QtGui.QScrollArea()
        self.controls_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.update_controls()

        controls_ = QtGui.QWidget()
        controls_layout = QtGui.QVBoxLayout()
        controls_layout.addWidget(QtGui.QLabel("Controls"), 0)
        controls_layout.addWidget(self.controls_area, 1)
        controls_.setLayout(controls_layout)
        ### End Controls

        ### Begin Sequencer
        sequencer_area = QtGui.QTableWidget()
        sequencer_area.setColumnCount(3)
        sequencer_area.setRowCount(5)

        data = {'col1':['1','2','3'], 'col2':['4','5','6'], 'col3':['7','8','9']}

        headers = []
        for i, key in enumerate(data.keys()):
            headers.append(key)
            for j, val in enumerate(data[key]):
                newitem = QtGui.QTableWidgetItem(val)
                sequencer_area.setItem(i, j, newitem)
        sequencer_area.setHorizontalHeaderLabels(headers)

        sequencer_area.resizeColumnsToContents()
        sequencer_area.resizeRowsToContents()

        sequencer = QtGui.QWidget()
        sequencer_layout = QtGui.QVBoxLayout()
        sequencer_layout.addWidget(QtGui.QLabel("Sequencer"))
        sequencer_layout.addWidget(sequencer_area)
        sequencer.setLayout(sequencer_layout)
        ### End Sequencer

        ### Begin Left Panel Layout
        panel_widget = QtGui.QSplitter(QtCore.Qt.Vertical)
        panel_widget.addWidget(controls_)
        panel_widget.addWidget(sequencer)
        ### End Left Panel Layout

        ### Begin Overall Layout
        main_container = QtGui.QSplitter(QtCore.Qt.Horizontal)
        main_container.addWidget(panel_widget)
        main_container.addWidget(self.sim_widget)
        main_container.splitterMoved.connect(self.splitter_update)

        self.setCentralWidget(main_container)
        ### End Overall Layout

        self.resizeEvent()

    def update_controls(self):
        self.controls_widget = QtGui.QWidget(self.controls_area)
        controls_widget_layout = QtGui.QVBoxLayout()

        if self.arm_data is not None:
            for i, control in enumerate(self.arm_data["CONTROLS"]):
                new_control = eval(control)
                controls_widget_layout.addWidget(new_control)

        self.controls_widget.setLayout(controls_widget_layout)
        self.controls_area.setWidget(self.controls_widget)
        self.splitter_update()

    def splitter_update(self, index=None, stretch=None):
        self.controls_widget.setFixedWidth(self.controls_area.frameRect().width())

    def load_arm(self, arm_data):
        self.arm.load_arm(arm_data)
        self.arm_data = arm_data
        self.update_controls()

    def update_arm_pos(self, arm_func, *args):
        getattr(self.arm, arm_func)(*args)

    def resizeEvent(self, event=None):
        self.splitter_update()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    sys.exit(app.exec_())
