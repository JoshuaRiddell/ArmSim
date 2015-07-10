import file_io
import sys

from PyQt4 import QtGui, QtCore, QtOpenGL


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        centralWidget = QtGui.QWidget()
        self.setCentralWidget(centralWidget)

        self.file_manager = file_io.FileManager(self)

        self.initMenus()

        screen = QtGui.QDesktopWidget()
        width = screen.availableGeometry().width()
        height = screen.availableGeometry().height()
        self.resize(width/2 - 15, height - 40)
        self.move(0, 0)
        self.setWindowTitle("ArmSim")
        self.show()

    def initMenus(self):
        file_menu = [
            "&File",
            [
                {
                    "name": "&Open",
                    "shortcut": "Ctrl+O",
                    "tip": "Open a SEQ File",
                    "cb": self.file_manager.open
                },
                {
                    "name": "&Save",
                    "shortcut": "Ctrl+S",
                    "tip": "Save Current File",
                    "cb": self.file_manager.save
                },
                {
                    "name": "&Save As...",
                    "shortcut": "Ctrl+Shift+S",
                    "tip": "Save As New File",
                    "cb": self.file_manager.save_as
                },
                {
                    "name": "&Exit",
                    "shortcut": "Ctrl+Q",
                    "tip": "Exit Application",
                    "cb": QtGui.qApp.quit
                }
            ]
        ]

        menubar = self.menuBar()

        for menu in [file_menu]:
            newMenu = menubar.addMenu(menu[0])
            for action in menu[1]:
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
