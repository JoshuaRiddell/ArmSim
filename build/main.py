import file_io
import arm
import simulator
import sequencer
import controls

import sys

from PyQt4 import QtGui, QtCore, QtOpenGL

MENU_FILE = 'menus.conf'
CONFIG_FILE = 'config.conf'

CONFIG = eval(file_io.load_config(CONFIG_FILE))


class MainWindow(QtGui.QMainWindow):
    """ Main top level class, contains instances of all other main classes"""

    def __init__(self):
        """ Initialise all main classes.
        """
        super(MainWindow, self).__init__()

        self.file_manager = file_io.FileManager(self,
                                                CONFIG["def_arm"],
                                                CONFIG["def_arms_directory"])
        self.arm = arm.Arm(self)
        self.arm_data = None
        self.sim_widget = simulator.SimWidget(self, CONFIG["cam_config"])
        self.controls_area = controls.ControlsArea(self)
        self.sequencer_widget = sequencer.SequencerWidget(self)

        # update the simulator window every 33ms (~30fps)
        self.main_clock = QtCore.QTimer()
        QtCore.QObject.connect(self.main_clock, QtCore.SIGNAL("timeout()"),
                               self.sim_widget.update_display)
        self.main_clock.start(33)

        self.initMenus()
        self.initGui()
        self.setStyleSheet("QSplitter::handle {background-color: rgb(150,150,150)}")

        self.setWindowTitle("ArmSim")
        self.setGeometry(-1500, 100, 900, 600)
        # self.show()
        self.showMaximized()

    def initMenus(self):
        """ Initialise top bar menu items by importing from configuration file.
        """
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
        ### Begin Sequencer
        sequencer = QtGui.QWidget()
        sequencer_layout = QtGui.QVBoxLayout()
        run_button = QtGui.QPushButton("Run")
        run_button.clicked.connect(self.sequencer_widget.run)
        add_button = QtGui.QPushButton("Add")
        add_button.clicked.connect(self.sequencer_widget.add_seq)
        sequencer_layout.addWidget(QtGui.QLabel("Sequencer"), 0)
        sequencer_layout.addWidget(run_button, 0)
        sequencer_layout.addWidget(add_button, 0)
        sequencer_layout.addWidget(self.sequencer_widget, 0)
        sequencer.setLayout(sequencer_layout)
        ### End Sequencer

        ### Begin Left Panel Layout
        panel_widget = QtGui.QSplitter(QtCore.Qt.Vertical)
        panel_widget.addWidget(self.controls_area)
        panel_widget.addWidget(sequencer)
        ### End Left Panel Layout

        ### Begin Overall Layout
        main_container = QtGui.QSplitter(QtCore.Qt.Horizontal)
        main_container.addWidget(panel_widget)
        main_container.addWidget(self.sim_widget)
        # main_container.splitterMoved.connect(self.splitter_update)

        self.setCentralWidget(main_container)
        ### End Overall Layout

        # self.resizeEvent()

    # def update_control_values(self):
    #     for control in self.controls_area:
    #         control.pull_values()

    def load_arm(self, arm_data):
        self.arm.load_arm(arm_data)
        self.sim_widget.load_arm(arm_data, self.file_manager)
        self.arm_data = arm_data
        self.controls_area.update_controls(arm_data)
        self.sequencer_widget.hard_update()

    def update_arm_pos(self, arm_func, *args):
        getattr(self.arm, arm_func)(*args)

    # def splitter_update(self, index=None, stretch=None):
    #     self.controls_area_widget.setFixedWidth(self.controls_area_area.frameRect().width())

    # def resizeEvent(self, event=None):
    #     self.splitter_update()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    sys.exit(app.exec_())
