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

        self.__parent = None
        self.parent = parent
        self.prefDialog = prefDialog

        self._initVars()

    def _initVars(self):
        self.enableLogging = None
        self.font = None
        self.fontSize = None
        self.language = None
        self.restoreWindowSize = None
        self.__changedData = False

    def __bool__(self):
        return self.__changedData

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        self.__parent = value

    @Slot(int)
    def interfaceLanguageChanged(self, index):

        language = self.prefDialog.cmbBoxInterfaceLanguage.itemText(index)
        languageDictionary = config.data.get(config.ConfigKey.InterfaceLanguages)
        key = list(languageDictionary.keys())[
            list(languageDictionary.values()).index(language)
        ]
        self.language = key
        if not self.__changedData:
            self.__changedData = True

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
    def enableLoggingStateChanged(self, value):

        self.enableLogging = bool(value)
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
                self.prefDialog.chkBoxEnableLogging.setChecked(False)
                defaultFont = QFont()
                defaultFont.fromString(config.data.get(config.ConfigKey.SystemFont))
                self.prefDialog.fcmbBoxFontFamily.setCurrentFont(defaultFont.family())
                self.prefDialog.spinBoxFontSize.setValue(defaultFont.pointSize())

    def reset(self):
        self._initVars()

class SetPreferences(QObject):
    def __init__(self, parent):
        super().__init__(parent)

        self.__prefDialog = None
        self.__pref = None
        self.parent = parent

        self._initHelper()

    def _initHelper(self):
        """
        _initHelper init used classes and make all signal connections
        """

        uiDir = str(self.parent.appDirectory.parent) + "/ui"
        self.__prefDialog = PreferencesDialogUI(uiDir)
        self.__pref = Preferences(self.parent, self.__prefDialog)

        #
        # Interface Language
        #
        self.__prefDialog.cmbBoxInterfaceLanguage.currentIndexChanged.connect(
            self.__pref.interfaceLanguageChanged
        )
        #
        # Font & Size
        #
        self.__prefDialog.fcmbBoxFontFamily.currentFontChanged.connect(
            self.__pref.currentFontChanged
        )
        self.__prefDialog.spinBoxFontSize.valueChanged.connect(
            self.__pref.currentFontSizeChanged
        )
        #
        # Logging
        #
        self.__prefDialog.chkBoxEnableLogging.stateChanged.connect(
            self.__pref.enableLoggingStateChanged
        )
        #
        # Window size
        #
        self.__prefDialog.chkBoxRestoreWindowSize.stateChanged.connect(
            self.__pref.restoreWindowSizeStateChanged
        )
        #
        # Buttons
        #
        self.__prefDialog.btnBox.clicked.connect(self.__pref.clickedButton)

    def _initUI(self):

        #
        # Interface Language
        #
        language = config.data.get(config.ConfigKey.Language)
        index = 0
        for key, value in config.data.get(config.ConfigKey.InterfaceLanguages).items():
            self.__prefDialog.cmbBoxInterfaceLanguage.addItem(value)
            if key == language:
                self.__prefDialog.cmbBoxInterfaceLanguage.setCurrentIndex(index)
            index += 1
        #
        # Font & Size
        #
        font = self.parent.font()
        self.__prefDialog.fcmbBoxFontFamily.setCurrentFont(font.family())
        self.__prefDialog.spinBoxFontSize.setValue(font.pointSize())
        #
        # Logging
        #
        if bLogging := config.data.get(config.ConfigKey.Logging):
            self.__prefDialog.chkBoxEnableLogging.setChecked(bLogging)

    def getPreferences(self, applyChanges=False):

        self._initUI()
        self.__pref.reset()

        rc = self.__prefDialog.exec_()
        if not rc:
            self.__pref.reset()

        if applyChanges:
            self.applyChanges()

        return rc

    def applyChanges(self):

        if self.__pref:
            print("YEEEEEAH!!!, YEEEEEAH!!")
        else:
            print("Bummer!!")


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
    dlgOptions.cmbBoxInterfaceLanguage.currentIndexChanged.connect(
        pref.interfaceLanguageChanged
    )
    #
    # Font & Size
    #
    font = mainWindow.font()
    dlgOptions.fcmbBoxFontFamily.setCurrentFont(font.family())
    dlgOptions.spinBoxFontSize.setValue(font.pointSize())
    dlgOptions.fcmbBoxFontFamily.currentFontChanged.connect(pref.currentFontChanged)
    dlgOptions.spinBoxFontSize.valueChanged.connect(pref.currentFontSizeChanged)
    #
    # Logging
    #
    if bLogging := config.data.get(config.ConfigKey.Logging):
        dlgOptions.chkBoxEnableLogging.setChecked(True)
    dlgOptions.chkBoxEnableLogging.stateChanged.connect(pref.enableLoggingStateChanged)
    #
    # Window size
    #
    dlgOptions.chkBoxRestoreWindowSize.stateChanged.connect(
        pref.restoreWindowSizeStateChanged
    )

    if dlgOptions.exec_():
        if pref:
            print("YEEEEEAH!!!, YEEEEEAH!!")
    else:
        print("Bummer!!")
    # if bLogging := config.data.get(config.ConfigKey.Logging):
    #    mainWindow.actEnableLogging.setChecked(bLogging)
    #    mainWindow.enableLogging(bLogging)
