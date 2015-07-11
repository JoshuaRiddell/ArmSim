import file_io
import sys

from PyQt4 import QtGui, QtCore, QtOpenGL

CONFIG = file_io.load_config()


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        centralWidget = QtGui.QWidget()
        self.setCentralWidget(centralWidget)

        self.file_manager = file_io.FileManager(self,
                                                CONFIG["def_arm"],
                                                CONFIG["def_arms_directory"])

        self.initMenus()

        screen = QtGui.QDesktopWidget()
        width = screen.availableGeometry().width()
        height = screen.availableGeometry().height()
        self.resize(width/2 - 15, height - 40)
        self.move(0, 0)
        self.setWindowTitle("ArmSim")
        self.show()

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

    def test(self):
        print("ran")




if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    sys.exit(app.exec_())
