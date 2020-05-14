"""
 Preferences Dialog box using Qt Designer

Returns:
    QDialog: PySide2 dialog box
"""

import sys

from PySide2.QtWidgets import QApplication, QDialogButtonBox, QMainWindow, QPushButton
from PySide2.QtCore import QFile, QIODevice, Qt
from PySide2.QtUiTools import QUiLoader

from vsutillib.pyqt import darkPalette


def PreferencesDialogUI(uiDir):

    ui_file_name = uiDir + "/PreferencesDialog.ui"
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        raise ValueError("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))

    loader = QUiLoader()
    DPreferences = loader.load(ui_file)
    ui_file.close()
    if not DPreferences:
        raise ValueError(loader.errorString())

    DPreferences.btnBox.clear()
    btnRestoreDefaults = QPushButton(" " + "Restore Defaults" + " ")
    btnApply = QPushButton("Ok")
    btnCancel = QPushButton("Cancel")
    btnCancel.setDefault(True)

    DPreferences.btnBox.addButton(btnRestoreDefaults, QDialogButtonBox.ResetRole)
    DPreferences.btnBox.addButton(btnApply, QDialogButtonBox.AcceptRole)
    DPreferences.btnBox.addButton(btnCancel, QDialogButtonBox.RejectRole)

    DPreferences.setWindowFlags(DPreferences.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    return DPreferences


class Example(QMainWindow):
    def __init__(self):
        super().__init__()

        dlgOptions = PreferencesDialogUI(".")

        dlgOptions.cmbBoxInterfaceLanguage.addItems(
            ["English (Inglés)", "Español (Spanish)"]
        )
        dlgOptions.cmbBoxInterfaceLanguage.setCurrentIndex(1)
        font = dlgOptions.font()
        dlgOptions.fcmbBoxFontFamily.setCurrentFont(font.family())
        dlgOptions.spinBoxFontSize.setValue(font.pointSize())

        if dlgOptions.exec_():
            print("Yeah!!")
        else:
            print("Bummer!!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # print(app.styleSheet())
    darkPalette(app)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
