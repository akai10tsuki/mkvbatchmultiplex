"""
 preferences dialog
"""


from PySide2.QtCore import QObject, Qt, Slot
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QDialog, QDialogButtonBox

from .. import config
from ..ui import Ui_PreferencesDialog


class PreferencesDialogWidget(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)

        self.__parent = None
        self.parent = parent
        self.__pref = Preferences(self)

        # remove ? help symbol from dialog header
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._initHelper()

    def _initUI(self):

        #
        # Interface Language
        #
        language = config.data.get(config.ConfigKey.Language)
        index = 0
        for key, value in config.data.get(config.ConfigKey.InterfaceLanguages).items():
            self.ui.cmbBoxInterfaceLanguage.addItem(value)
            if key == language:
                self.ui.cmbBoxInterfaceLanguage.setCurrentIndex(index)
            index += 1
        #
        # Font & Size
        #
        font = self.parent.font()
        self.ui.fcmbBoxFontFamily.setCurrentFont(font.family())
        self.ui.spinBoxFontSize.setValue(font.pointSize())
        #
        # Loging
        #
        if bLoging := config.data.get(config.ConfigKey.Loging):
            self.ui.chkBoxEnableLoging.setChecked(bLoging)

    def _initHelper(self):

        #
        # Interface Language
        #
        self.ui.cmbBoxInterfaceLanguage.currentIndexChanged.connect(
            self.__pref.interfaceLanguageChanged
        )
        #
        # Font & Size
        #
        self.ui.fcmbBoxFontFamily.currentFontChanged.connect(
            self.__pref.currentFontChanged
        )
        self.ui.spinBoxFontSize.valueChanged.connect(self.__pref.currentFontSizeChanged)
        #
        # Loging
        #
        self.ui.chkBoxEnableLoging.stateChanged.connect(
            self.__pref.enableLogingStateChanged
        )
        #
        # Window size
        #
        self.ui.chkBoxRestoreWindowSize.stateChanged.connect(
            self.__pref.restoreWindowSizeStateChanged
        )
        #
        # Buttons
        #
        self.ui.btnBox.clicked.connect(self.__pref.clickedButton)

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        self.__parent = value

    @property
    def preferences(self):
        return self.__pref

    def getPreferences(self, applyChanges=False):

        self._initUI()
        self.preferences.reset()

        rc = self.exec_()
        if not rc:
            self.preferences.reset()
        if applyChanges:
            self.applyChanges()

        return rc

    def applyChanges(self):

        if self.preferences:
            print("YEEEEEAH!!!, YEEEEEAH!!")
        else:
            print("Bummer!!")


class Preferences(QObject):
    def __init__(self, parent):
        super().__init__(parent)

        self.__parent = None
        self.parent = parent

        self._initVars()

    def _initVars(self):
        self.enableLoging = None
        self.font = None
        self.fontSize = None
        self.language = None
        self.restoreWindowSize = None
        self.__changedData = False

    def __bool__(self):
        return self.__changedData

    @Slot(int)
    def interfaceLanguageChanged(self, index):

        language = self.parent.ui.cmbBoxInterfaceLanguage.itemText(index)
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

        buttonRole = self.parent.btnBox.buttonRole(button)

        if buttonRole in [QDialogButtonBox.AcceptRole, QDialogButtonBox.ResetRole]:
            if buttonRole == QDialogButtonBox.ResetRole:
                self.parent.ui.chkBoxRestoreWindowSize.setChecked(True)
                self.parent.ui.chkBoxEnableLoging.setChecked(False)
                defaultFont = QFont()
                defaultFont.fromString(config.data.get(config.ConfigKey.SystemFont))
                self.parent.ui.fcmbBoxFontFamily.setCurrentFont(defaultFont.family())
                self.parent.ui.spinBoxFontSize.setValue(defaultFont.pointSize())

    def reset(self):
        self._initVars()
