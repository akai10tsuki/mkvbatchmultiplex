"""
 preferences dialog
"""

import platform

from PySide2.QtCore import QObject, Qt, Slot
from PySide2.QtGui import QFont, QPalette, QColor
from PySide2.QtWidgets import QDialog, QDialogButtonBox

from vsutillib.pyqt import centerWidget

from .. import config
from ..ui import Ui_PreferencesDialog


class PreferencesDialogWidget(QDialog):
    """
    PreferencesDialogWidget change configuration parameters
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)

        self.__parent = None
        self.parent = parent
        self.__pref = Preferences(self)

        # remove ? help symbol from dialog header
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.ui.cmbBoxInterfaceLanguage.setDuplicatesEnabled(False)
        self._initHelper()

    def _initUI(self):
        #
        # Interface Language
        #
        language = config.data.get(config.ConfigKey.Language)
        index = 0
        self.ui.cmbBoxInterfaceLanguage.clear()
        for key, value in config.data.get(config.ConfigKey.InterfaceLanguages).items():
            self.ui.cmbBoxInterfaceLanguage.addItem(value)
            if key == language:
                self.ui.cmbBoxInterfaceLanguage.setCurrentIndex(index)
            index += 1
        #
        # Font & Size
        #
        font = QFont()
        font.fromString(config.data.get(config.ConfigKey.Font))
        self.ui.fcmbBoxFontFamily.setCurrentFont(font.family())
        self.ui.spinBoxFontSize.setValue(font.pointSize())
        #
        # Logging is boolean value
        #
        isLogging = config.data.get(config.ConfigKey.Logging)
        self.ui.chkBoxEnableLogging.setChecked(
            config.data.get(config.ConfigKey.Logging)
        )
        #
        # Enable Log Viewer
        #
        self.ui.chkBoxEnableLogViewer.setChecked(
            config.data.get(config.ConfigKey.LogViewer)
        )
        #
        # Does not follow global palette fully
        #
        if platform.system() == "Windows":
            disabledColor = QColor(127, 127, 127)
            chkBoxPalette = self.ui.chkBoxEnableLogViewer.palette()
            chkBoxPalette.setColor(
                QPalette.Disabled, QPalette.WindowText, disabledColor
            )
            self.ui.chkBoxEnableLogViewer.setPalette(chkBoxPalette)
        if not isLogging:
            self.ui.chkBoxEnableLogViewer.setEnabled(False)
        #
        # Enable History
        #
        if config.data.get(config.ConfigKey.JobHistory) is not None:
            self.ui.chkBoxEnableJobHistory.setChecked(
                config.data.get(config.ConfigKey.JobHistory)
            )
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
        # Logging
        #
        self.ui.chkBoxEnableLogging.stateChanged.connect(
            self.__pref.enableLoggingStateChanged
        )
        self.ui.chkBoxEnableLogViewer.stateChanged.connect(
            self.__pref.enableLogViewerStateChanged
        )
        #
        # Job History
        #
        if config.data.get(config.ConfigKey.JobHistory) is not None:
            self.ui.chkBoxEnableJobHistory.stateChanged.connect(
                self.__pref.enableJobHistoryChanged
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
        #
        # Restore Defaults
        #
        self.ui.btnRestoreDefaults.clicked.connect(self.__pref.restoreDefaults)

    # @property
    # def parent(self):
    #    return self.__parent

    # @parent.setter
    # def parent(self, value):
    #    self.__parent = value

    @property
    def preferences(self):
        return self.__pref

    def getPreferences(self):
        """Show dialog to set preferences"""

        self._initUI()
        self.preferences.reset()

        rc = self.exec_()
        if rc:
            self.applyChanges()

        return rc

    def applyChanges(self):
        """Activate changes selected on Preferences Dialog"""

        if self.preferences:
            #
            # Language
            #
            if self.preferences.language is not None:
                config.data.set(config.ConfigKey.Language, self.preferences.language)
                self.parent.setLanguage()
            #
            # Font & Size
            #
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
            #
            # Logging
            #
            if self.preferences.enableLogging is not None:
                config.data.set(
                    config.ConfigKey.Logging, self.preferences.enableLogging
                )
                self.parent.enableLogging(self.preferences.enableLogging)
            #
            # LogViewer
            #
            loggingOn = config.data.get(config.ConfigKey.Logging)
            if loggingOn:
                if self.preferences.enableLogViewer is not None:
                    config.data.set(
                        config.ConfigKey.LogViewer, self.preferences.enableLogViewer
                    )
                    if self.preferences.enableLogViewer:
                        if self.parent.logViewerWidget.tab < 0:
                            self.parent.logViewerWidget.unHideTab()
                            self.parent.logViewerWidget.setAsCurrentTab()
                    else:
                        if self.parent.logViewerWidget.tab >= 0:
                            self.parent.logViewerWidget.hideTab()
            else:
                config.data.set(
                    config.ConfigKey.LogViewer, False
                )
                if self.parent.logViewerWidget.tab >= 0:
                    self.parent.logViewerWidget.hideTab()
            #
            # Job History
            #
            if config.data.get(config.ConfigKey.JobHistory) is not None:
                if self.preferences.enableJobHistory is not None:
                    config.data.set(
                        config.ConfigKey.JobHistory, self.preferences.enableJobHistory
                    )
                    if self.preferences.enableJobHistory:
                        if self.parent.historyWidget.tab < 0:
                            self.parent.historyWidget.unHideTab()
                            self.parent.historyWidget.setAsCurrentTab()
                    else:
                        if self.parent.historyWidget.tab >= 0:
                            self.parent.historyWidget.hideTab()
            #
            # Restore window size
            #
            if self.preferences.restoreWindowSize is not None:

                defaultGeometry = config.data.get(config.ConfigKey.DefaultGeometry)
                self.parent.setGeometry(
                    defaultGeometry[0],
                    defaultGeometry[1],
                    defaultGeometry[2],
                    defaultGeometry[3],
                )
                # Center window some title bar goes out of screen
                centerWidget(self.parent)
                # Update geometry includes position
                base64Geometry = self.parent.saveGeometry().toBase64()
                b = base64Geometry.data()  # b is a bytes string
                config.data.set(config.ConfigKey.Geometry, b)

    def retranslateUi(self):
        self.ui.retranslateUi(self)


class Preferences(QObject):
    def __init__(self, parent):
        super().__init__(parent)

        self.__parent = None
        self.parent = parent

        self._initVars()

    def _initVars(self):
        self.enableJobHistory = None
        self.enableLogging = None
        self.enableLogViewer = None
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
        if language:
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
        self.parent.ui.chkBoxEnableLogViewer.setEnabled(self.enableLogging)

    @Slot(int)
    def enableLogViewerStateChanged(self, value):

        self.enableLogViewer = bool(value)
        if not self.__changedData:
            self.__changedData = True

    @Slot(int)
    def enableJobHistoryChanged(self, value):

        self.enableJobHistory = bool(value)
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
                self.parent.ui.chkBoxEnableLogging.setChecked(False)
                defaultFont = QFont()
                defaultFont.fromString(config.data.get(config.ConfigKey.SystemFont))
                self.parent.ui.fcmbBoxFontFamily.setCurrentFont(defaultFont.family())
                self.parent.ui.spinBoxFontSize.setValue(defaultFont.pointSize())

    @Slot(bool)
    def restoreDefaults(self):

        self.parent.ui.chkBoxRestoreWindowSize.setChecked(True)
        self.parent.ui.chkBoxEnableLogging.setChecked(False)
        if config.data.get(config.ConfigKey.JobHistory) is not None:
            self.parent.ui.chkBoxEnableJobHistory.setChecked(False)
        self.parent.ui.chkBoxEnableLogViewer.setChecked(False)
        defaultFont = QFont()
        defaultFont.fromString(config.data.get(config.ConfigKey.SystemFont))
        self.parent.ui.fcmbBoxFontFamily.setCurrentFont(defaultFont.family())
        self.parent.ui.spinBoxFontSize.setValue(defaultFont.pointSize())

    def reset(self):
        self._initVars()
