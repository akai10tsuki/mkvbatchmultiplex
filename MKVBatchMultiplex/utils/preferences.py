"""
 preferences dialog
"""


from PySide2.QtCore import QObject, Slot
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QDialogButtonBox

from .PreferencesDialogUI import PreferencesDialogUI

from .. import config

class Preferences(QObject):

    def __init__(self, parent, prefDialog):
        super().__init__(parent)

        self.parent = parent
        self.prefDialog = prefDialog
        self.font = None
        self.fontSize = None
        self.enableLoging = None
        self.restoreWindowSize = None
        self.__changedData = False

    @Slot(object)
    def currentFontChanged(self, font):

        self.font = font
        if not self.__changedData:
            self.__changedData = True

    @Slot(int)
    def currentFontSizeChanged(self, value):

        self.fontSize = value
        if not self.__changedData:
            self.__changedData = True

    @Slot(int)
    def enableLogingStateChanged(self, value):

        self.enableLoging = bool(value)
        if not self.__changedData:
            self.__changedData = True

    @Slot(int)
    def restoreWindowSizeStateChanged(self, value):

        self.restoreWindowSize = bool(value)
        if not self.__changedData:
            self.__changedData = True

    @Slot(object)
    def clickedButton(self, button):

        buttonRole = self.prefDialog.btnBox.buttonRole(button)

        if buttonRole in [QDialogButtonBox.AcceptRole, QDialogButtonBox.ResetRole]:
            if buttonRole == QDialogButtonBox.ResetRole:
                self.prefDialog.chkBoxRestoreWindowSize.setChecked(True)
                self.prefDialog.chkBoxEnableLoging.setChecked(False)
                defaultFont = QFont()
                defaultFont.fromString(config.data.get(config.ConfigKey.SystemFont))
                self.prefDialog.fcmbBoxFontFamily.setCurrentFont(defaultFont.family())
                self.prefDialog.spinBoxFontSize.setValue(defaultFont.pointSize())


def preferences(mainWindow):

    uiDir = str(mainWindow.appDirectory.parent) + "/ui"

    dlgOptions = PreferencesDialogUI(uiDir)

    pref = Preferences(mainWindow, dlgOptions)

    #
    # Buttons
    #
    dlgOptions.btnBox.clicked.connect(pref.clickedButton)

    #
    # Interface Language
    #
    language = config.data.get(config.ConfigKey.Language)
    index = 0
    for key, value in config.data.get(config.ConfigKey.InterfaceLanguages).items():
        dlgOptions.cmbBoxInterfaceLanguage.addItem(value)
        if key == language:
            dlgOptions.cmbBoxInterfaceLanguage.setCurrentIndex(index)
            languageIndex = index
        index += 1
    #
    # Font & Size
    #
    font = mainWindow.font()
    dlgOptions.fcmbBoxFontFamily.setCurrentFont(font.family())
    dlgOptions.spinBoxFontSize.setValue(font.pointSize())
    dlgOptions.fcmbBoxFontFamily.currentFontChanged.connect(pref.currentFontChanged)
    dlgOptions.spinBoxFontSize.valueChanged.connect(pref.currentFontSizeChanged)
    #
    # Loging
    #
    if bLoging := config.data.get(config.ConfigKey.Loging):
        dlgOptions.chkBoxEnableLoging.setChecked(True)
    dlgOptions.chkBoxEnableLoging.stateChanged.connect(pref.enableLogingStateChanged)
    #
    # Window size
    #
    dlgOptions.chkBoxRestoreWindowSize.stateChanged.connect(pref.restoreWindowSizeStateChanged)


    if dlgOptions.exec_():
        if pref:
            print("YEEEEEAH!!!, YEEEEEAH!!")
    else:
        print("Bummer!!")
    # if bLoging := config.data.get(config.ConfigKey.Loging):
    #    mainWindow.actEnableLoging.setChecked(bLoging)
    #    mainWindow.enableLoging(bLoging)
