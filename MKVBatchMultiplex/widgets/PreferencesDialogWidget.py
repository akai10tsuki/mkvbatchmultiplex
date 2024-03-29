"""
Preferences - Dialog with the various system configuration items
"""

import platform

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QWidget

from vsutillib.pyside6 import centerWidget

from .. import config
from ..ui import Ui_PreferencesDialog


class PreferencesDialogWidget(QDialog):
    """
    PreferencesDialogWidget change configuration parameters
    """

    translateInterfaceSignal = Signal()
    stateChangedAlgorithm = Signal()
    stateChangedCRC = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)

        #self.__parent = None
        self.parent = parent
        self.__pref = Preferences(self)

        # remove ? help symbol from dialog header
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.ui.cmbBoxInterfaceLanguage.setDuplicatesEnabled(False)
        self.radioButtons = [self.ui.rbZero, self.ui.rbOne, self.ui.rbTwo]
        self._initHelper()

    def _initUI(self):
        """
        Initialize widget members with systemConfiguration for the elements
        """
        #
        # Interface Language
        #
        language = config.data.get(config.ConfigKey.Language)
        index = 0
        self.ui.cmbBoxInterfaceLanguage.clear()
        for key, value in config.data.get(
                config.ConfigKey.InterfaceLanguages).items():

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

        # region Log Viewer
        #
        # Log Viewer get configuration
        #
        self.ui.chkBoxEnableLogViewer.setChecked(
            config.data.get(config.ConfigKey.LogViewer)
        )

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
        # endregion Log Viewer

        #
        # CRC
        #
        if config.data.get(config.ConfigKey.CRC32) is not None:
            doCRC = config.data.get(config.ConfigKey.CRC32)
            if (doCRC == 2):
                self.ui.chkBoxComputeCRC.setChecked(True)
            else:
                self.ui.chkBoxComputeCRC.setChecked(False)

        #
        # Use embedded mkvmerge
        #
        if config.data.get(config.ConfigKey.UseEmbedded) is not None:
            useEmbedded = config.data.get(config.ConfigKey.UseEmbedded)
            if (useEmbedded == 2):
                self.ui.chkBoxUseEmbedded.setChecked(True)
            else:
                self.ui.chkBoxUseEmbedded.setChecked(False)



        # region History
        #
        # Enable History
        #
        # Temporarily disable History
        #
        #if config.data.get(config.ConfigKey.JobHistoryDisabled):
        #    self.ui.chkBoxEnableJobHistory.setEnabled(False)
        #    self.ui.chkBoxAutoSaveJobHistory.setEnabled(False)
        #    self.ui.chkBoxEnableJobHistory.hide()
        #    self.ui.chkBoxAutoSaveJobHistory.hide()

        #if config.data.get(config.ConfigKey.JobHistory) is not None:
        #    self.ui.chkBoxEnableJobHistory.setChecked(
        #        config.data.get(config.ConfigKey.JobHistory)
        #    )
        #if config.data.get(config.ConfigKey.JobsAutoSave) is not None:
        #    self.ui.chkBoxAutoSaveJobHistory.setChecked(
        #        config.data.get(config.ConfigKey.JobsAutoSave)
        #    )
        # endregion History

        #
        # Restore Windows Size
        #
        self.ui.chkBoxRestoreWindowSize.setChecked(False)

        #
        # Algorithm
        #
        if config.data.get(config.ConfigKey.Algorithm) is not None:
            currentAlgorithm = config.data.get(config.ConfigKey.Algorithm)
            self.radioButtons[currentAlgorithm].setChecked(True)

    def _initHelper(self):
        """
        Connect to change signals of widget elements
        """

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
        self.ui.spinBoxFontSize.valueChanged.connect(
            self.__pref.currentFontSizeChanged)
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
        # CRC
        #
        self.ui.chkBoxComputeCRC.stateChanged.connect(
            self.__pref.enableCRCComputeStateChanged
        )

        #
        # useEmbedded
        #
        self.ui.chkBoxUseEmbedded.stateChanged.connect(
            self.__pref.useEmbeddedStateChange
        )

        #
        # Job History
        #
        #if config.data.get(config.ConfigKey.JobHistory) is not None:
        #    self.ui.chkBoxEnableJobHistory.stateChanged.connect(
        #        self.__pref.enableJobHistoryChanged
        #    )

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
        # Algorithm radio buttons
        #
        self.ui.rbZero.toggled.connect(
            lambda: self.__pref.toggledRadioButton(self.ui.rbZero)
        )
        self.ui.rbOne.toggled.connect(
            lambda: self.__pref.toggledRadioButton(self.ui.rbOne)
        )
        self.ui.rbTwo.toggled.connect(
            lambda: self.__pref.toggledRadioButton(self.ui.rbTwo)
        )

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

        rc = self.exec()
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
                config.data.set(config.ConfigKey.Language,
                                self.preferences.language)
                self.parent.translate()
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
                        if self.parent.logViewer.tab < 0:
                            self.parent.logViewer.unHideTab()
                            self.parent.logViewer.setAsCurrentTab()
                    else:
                        if self.parent.logViewer.tab >= 0:
                            self.parent.logViewer.hideTab()
            else:
                config.data.set(config.ConfigKey.LogViewer, False)
                if self.parent.logViewer.tab >= 0:
                    self.parent.logViewer.hideTab()

            #
            # CRC
            #
            if self.preferences.enableCRCCompute is not None:
                if config.data.get(config.ConfigKey.CRC32) is not None:
                    if (self.preferences.enableCRCCompute):
                        config.data.set(config.ConfigKey.CRC32, 2)
                    else:
                        config.data.set(config.ConfigKey.CRC32, 0)
                    self.stateChangedCRC.emit()
            #
            # useEmbedded
            #
            if self.preferences.useEmbedded is not None:
                if config.data.get(config.ConfigKey.UseEmbedded) is not None:
                    if self.preferences.useEmbedded:
                        config.data.set(config.ConfigKey.UseEmbedded, 2)
                    else:
                        config.data.set(config.ConfigKey.UseEmbedded, 0)

            #
            # Job History
            #
            #if config.data.get(config.ConfigKey.JobHistory) is not None:
            #    if self.preferences.enableJobHistory is not None:
            #        config.data.set(
            #            config.ConfigKey.JobHistory, self.preferences.enableJobHistory
            #        )
            #        if self.preferences.enableJobHistory:
            #            if self.parent.historyWidget.tab < 0:
            #                self.parent.historyWidget.unHideTab()
            #                self.parent.historyWidget.setAsCurrentTab()
            #        else:
            #            if self.parent.historyWidget.tab >= 0:
            #                self.parent.historyWidget.hideTab()

            #
            # Algorithm
            #
            if config.data.get(config.ConfigKey.Algorithm) is not None:
                for index, rb in enumerate(self.radioButtons):
                    if rb.isChecked():
                        config.data.set(config.ConfigKey.Algorithm, index)
                self.stateChangedAlgorithm.emit()

            #
            # Restore window size
            #
            if self.preferences.restoreWindowSize is not None:

                defaultGeometry = config.data.get(
                    config.ConfigKey.DefaultGeometry)
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
    """
    Preferences deals with the selection of preferences logic

    Args:
        QObject (QObject): generic PySide2 object
    """

    def __init__(self, parent):
        super().__init__(parent)

        #self.__parent = None
        self.parent = parent

        self._initVars()

    def _initVars(self):
        #self.enableJobHistory = None
        self.enableLogging = None
        self.enableLogViewer = None
        self.enableCRCCompute = None
        self.font = None
        self.fontSize = None
        self.language = None
        self.restoreWindowSize = None
        self.useEmbedded = None
        self.__changedData = False

    def __bool__(self):
        return self.__changedData

    @Slot(int)
    def interfaceLanguageChanged(self, index):
        """
        interfaceLanguageChanged interface language change signal

        Args:
            index (int): index in language combo box
        """
        language = self.parent.ui.cmbBoxInterfaceLanguage.itemText(index)
        if language:
            languageDictionary = config.data.get(
                config.ConfigKey.InterfaceLanguages)
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
        # Enable/Disable the Log Viewer checkbox
        self.parent.ui.chkBoxEnableLogViewer.setEnabled(self.enableLogging)

    @Slot(int)
    def enableCRCComputeStateChanged(self, value):
        self.enableCRCCompute = bool(value)
        if not self.__changedData:
            self.__changedData = True

    @Slot(int)
    def enableLogViewerStateChanged(self, value):
        self.enableLogViewer = bool(value)
        if not self.__changedData:
            self.__changedData = True

    #@Slot(int)
    #def enableJobHistoryChanged(self, value):

    #    self.enableJobHistory = bool(value)
    #    if not self.__changedData:
    #        self.__changedData = True

    @Slot(int)
    def useEmbeddedStateChange(self, value):
        self.useEmbedded = bool(value)
        if not self.__changedData:
            self.__changedData = True

    @Slot(int)
    def restoreWindowSizeStateChanged(self, value):

        self.restoreWindowSize = bool(value)
        if not self.__changedData:
            self.__changedData = True

    @Slot(object)
    def toggledRadioButton(self, rButton):  # pylint: disable=unused-argument

        if not self.__changedData:
            self.__changedData = True

    @Slot(object)
    def clickedButton(self, button):
        """
        clickedButton deals with the final button clicked

        Args:
            button (QPushButton): buttons for the Preferences Dialog
        """

        buttonRole = self.parent.ui.btnBox.buttonRole(button)

        if buttonRole in [QDialogButtonBox.AcceptRole,
                          QDialogButtonBox.ResetRole]:
            if buttonRole == QDialogButtonBox.ResetRole:
                self.parent.ui.chkBoxRestoreWindowSize.setChecked(True)
                self.parent.ui.chkBoxEnableLogging.setChecked(False)
                defaultFont = QFont()
                defaultFont.fromString(
                    config.data.get(config.ConfigKey.SystemFont))
                self.parent.ui.fcmbBoxFontFamily.setCurrentFont(
                    defaultFont.family())
                self.parent.ui.spinBoxFontSize.setValue(
                    defaultFont.pointSize())

    @Slot(bool)
    def restoreDefaults(self):
        """
        restoreDefaults restore application defaults
        """

        self.parent.ui.chkBoxRestoreWindowSize.setChecked(True)
        self.parent.ui.chkBoxEnableLogging.setChecked(False)
        self.parent.ui.chkBoxComputeCRC.setChecked(False)
        if config.data.get(config.ConfigKey.JobHistory) is not None:
            self.parent.ui.chkBoxEnableJobHistory.setChecked(False)
        self.parent.ui.chkBoxEnableLogViewer.setChecked(False)
        defaultFont = QFont()
        defaultFont.fromString(config.data.get(config.ConfigKey.SystemFont))
        self.parent.ui.fcmbBoxFontFamily.setCurrentFont(defaultFont.family())
        self.parent.ui.spinBoxFontSize.setValue(defaultFont.pointSize())
        if config.data.get(config.ConfigKey.Algorithm) is not None:
            self.parent.radioButtons[config.ALGORITHMDEFAULT].setChecked(True)

    def reset(self):
        self._initVars()
