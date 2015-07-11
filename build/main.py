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
        file_menu = [
            "&File",
            [
                {
                    "name": "&Open Arm File...",
                    "shortcut": "Ctrl+Shift+O",
                    "tip": "Open a SEQ File",
                    "cb": self.file_manager.open_arm
                },
                {
                    "name": "sep"
                },
                {
                    "name": "&New Sequence...",
                    "shortcut": "Ctrl+N",
                    "tip": "Save As New File",
                    "cb": self.file_manager.new_seq
                },
                {
                    "name": "&Open Sequence...",
                    "shortcut": "Ctrl+O",
                    "tip": "Save As New File",
                    "cb": self.file_manager.open_seq
                },
                {
                    "name": "&Save Sequence",
                    "shortcut": "Ctrl+S",
                    "tip": "Save Current File",
                    "cb": self.file_manager.save_seq
                },
                {
                    "name": "&Save Sequence As...",
                    "shortcut": "Ctrl+Shift+S",
                    "tip": "Save As New File",
                    "cb": self.file_manager.save_seq_as
                },
                {
                    "name": "sep"
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
