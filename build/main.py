import file_io
import arm
import simulator

import sys

from PyQt4 import QtGui, QtCore, QtOpenGL

MENU_FILE = 'menus.conf'
CONFIG_FILE = 'config.conf'

CONFIG = eval(file_io.load_config(CONFIG_FILE))


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.file_manager = file_io.FileManager(self,
                                                CONFIG["def_arm"],
                                                CONFIG["def_arms_directory"])
        self.effector = arm.Arm()
        self.sim_widget = simulator.SimWidget()

        self.initMenus()
        self.initGui()

        self.setWindowTitle("ArmSim")
        self.show()
        # self.showMaximized()

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
        controls_label = QtGui.QLabel("Controls")
        controls_area = QtGui.QScrollArea()
        controls_widget = QtGui.QWidget()
        controls_layout = QtGui.QVBoxLayout()

        for i in range(10):
            controls_layout.addWidget(QtGui.QPushButton("Hello World"))

        sequencer_label = QtGui.QLabel("Sequencer")

        panel_container = QtGui.QVBoxLayout()
        panel_container.addWidget(controls_label, 0)
        panel_container.addWidget(controls_area, 1)
        panel_container.addWidget(sequencer_label, 0)

        main_container = QtGui.QHBoxLayout()
        main_container.addLayout(panel_container, 2)
        main_container.addWidget(self.sim_widget, 3)

        central_widget = QtGui.QWidget(self)
        central_widget.setLayout(main_container)
        self.setCentralWidget(central_widget)

        # button_layout -> button_widget -> scroll_area -> panel_container -> main_container -> central_widget

    def load_arm(self, arm_data):
        self.effector.load_arm(self.arm_data)
        print("Load data")


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    sys.exit(app.exec_())
