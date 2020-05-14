"""
 test script to display working UI used the class that the UI is based
"""

import sys
from PySide2.QtWidgets import QApplication, QDialog, QMainWindow
from PySide2.QtCore import QFile
from Ui_PreferencesDialog import Ui_PreferencesDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

class PreferencesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PreferencesDialog()
    window.show()

    sys.exit(app.exec_())
