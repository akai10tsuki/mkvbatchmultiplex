"""
 test script to display working UI used the class that the UI is based
"""

import sys

from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox
from Ui_PreferencesDialog import Ui_PreferencesDialog
from Ui_ProjectInfoDialog import Ui_ProjectInfoDialog
from Ui_ProjectInfoOkDialog import Ui_ProjectInfoOkDialog
from Ui_SearchTextDialog import Ui_SearchTextDialog


#class MainWindow(QMainWindow):
#    def __init__(self):
#        super().__init__()
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

class PreferencesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)

class ProjectInfoDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ProjectInfoDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.setStandardButtons(QDialogButtonBox.Ok)

class ProjectInfoOkDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ProjectInfoOkDialog()
        self.ui.setupUi(self)

class SearchTextDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SearchTextDialog()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PreferencesDialog()
    window.show()

    sys.exit(app.exec())
