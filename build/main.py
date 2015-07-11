import file_io
import arm
import simulator

import sys

from PyQt4 import QtGui, QtCore, QtOpenGL

CONFIG = file_io.load_config()


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.file_manager = file_io.FileManager(self,
                                                CONFIG["def_arm"],
                                                CONFIG["def_arms_directory"])
        self.effector = arm.Effector()
        self.sim_widget = simulator.SimWidget()

        self.initMenus()
        self.initControls()

        self.setWindowTitle("ArmSim")
        self.showMaximized()

    def initMenus(self):
        menu_items = eval(file_io.load_menu_file())
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

    def initControls(self):
        centralWidget = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        centralWidget.setLayout(grid)
        self.setCentralWidget(centralWidget)

        button = QtGui.QPushButton("Hello World")
        grid.addWidget(button, 0, 0)
        grid.addWidget(self.sim_widget, 0, 1)

    def test(self):
        print("ran")


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    sys.exit(app.exec_())
