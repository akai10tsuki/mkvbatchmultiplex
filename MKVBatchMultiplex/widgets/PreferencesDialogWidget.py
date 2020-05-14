"""
 preferences dialog
"""


from PySide2.QtCore import QObject, Qt, Slot
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QDialog, QDialogButtonBox

from vsutillib.pyqt import centerWidget

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
        self.ui.chkBoxEnableLoging.setChecked(config.data.get(config.ConfigKey.Loging))
        #
        # Restore Windows Size
        #
        self.ui.chkBoxRestoreWindowSize.setChecked(False)

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
        if rc:
            self.applyChanges()

        return rc

    def applyChanges(self):

        if self.preferences:
            if self.preferences.language is not None:
                config.data.set(config.ConfigKey.Language, self.preferences.language)
                self.parent.setLanguage()

            if (self.preferences.font is not None) or (
                self.preferences.fontSize is not None
            ):
                font = QFont()
                font.fromString(config.data.get(config.ConfigKey.Font))

                if self.preferences.font is not None:
                    font = self.preferences.font

                if self.preferences.fontSize is not None:
                    font.setPointSize(self.preferences.fontSize)

                self.parent.setFont(font)
                self.parent.setAppFont(font)
                config.data.set(config.ConfigKey.Font, font.toString())

            if self.preferences.enableLoging is not None:
                config.data.set(config.ConfigKey.Loging, self.preferences.enableLoging)
                self.parent.enableLoging(self.preferences.enableLoging)

            if self.preferences.restoreWindowSize is not None:

                defaultGeometry = config.data.get(config.ConfigKey.DefaultGeometry)
                self.parent.setGeometry(
                    defaultGeometry[0],
                    defaultGeometry[1],
                    defaultGeometry[2],
                    defaultGeometry[3],
                )
                centerWidget(self.parent)

                # Update geometry includes position
                base64Geometry = self.parent.saveGeometry().toBase64()
                b = base64Geometry.data()  # b is a bytes string
                config.data.set(config.ConfigKey.Geometry, b)


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

        buttonRole = self.parent.ui.btnBox.buttonRole(button)

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
