"""
MKVBatchMultiplex entry point
"""

# MAI0004

# region imports
import ctypes
import logging
import os
import platform
import re
import sys

from collections import deque
from pathlib import Path
from typing import Optional

from PySide6.QtCore import (
    QByteArray,
    QEvent,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import(
    QColor,
    QFont,
    QIcon,
    QPalette,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QStatusBar,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from vsutillib.mkv import getMKVMerge, getMKVMergeEmbedded, getMKVMergeVersion
from vsutillib.pyside6 import (
    centerWidget,
    checkColor,
    darkPalette,
    DualProgressBar,
    HorizontalLine,
    QActionWidget,
    QActivityIndicator,
    QFormatLabel,
    QMenuWidget,
    QOutputTextWidget,
    QProgressIndicator,
    QSystemTrayIconWidget,
    setAppStyle,
    TabWidget,
    VerticalLine,
)

from . import config
from .dataset import TableData, tableHeaders
from .jobs import JobQueue
from .models import TableProxyModel, JobsTableModel
from .utils import (
    icons,
    configMessagesCatalog,
    executeMKVToolnix,
    OutputWindows,
    Progress,
    Text,
    Translate,
    UiSetMessagesCatalog,
    yesNoDialog,
)
from .widgets import (
    CommandWidget,
    JobsOutputErrorsWidget,
    JobsOutputWidget,
    JobsTableViewWidget,
    LogViewerWidget,
    PreferencesDialogWidget,
    RenameWidget,
)
# endregion imports


class MainWindow(QMainWindow):
    """ Main window of application """

    trayIconMessageSignal = Signal(str, str, object)

    # region Initialization

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.parent = parent

        self.setWindowIcon(QIcon(QPixmap(":/images/Itsue256x256.png")))

        # Language setup has to be early so _() is defined
        self.translateInterface = Translate()
        self.uiTranslateInterface = UiSetMessagesCatalog(self)
        configMessagesCatalog(self)

        self._initVars()
        self._initHelper()
        self._initUI()

        self.createActions()
        self.createMenus()
        self.createToolbars()
        self.createStatusbar()

        self.configuration(action=config.Action.Restore)

        self.translate()

        self.setUnifiedTitleAndToolBarOnMac(True)
        self.trayIcon.show()
        self.show()

    def _initVars(self) -> None:

        #
        # Where am I running from
        #

        self.log = False

        # if getattr(sys, "frozen", False):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running in a pyinstaller bundle
            self.appDirectory = Path(os.path.dirname(__file__)).parent
        elif "__compiled__" in globals():
            # Running in a Nuitka bundle
            self.appDirectory = Path(os.path.dirname(__file__)).parent
        else:
            self.appDirectory = Path(os.path.realpath(__file__)).parent

        self.trayIcon = QSystemTrayIconWidget(self, self.windowIcon())

        self.setPreferences = PreferencesDialogWidget(self)
        self.translateInterface.addSlot(self.setPreferences.retranslateUi)
        self.activitySpinner = QActivityIndicator(self)

        self.controlQueue = deque()

        self.jobsQueue = JobQueue(self, controlQueue=self.controlQueue, appDir=self.appDirectory)

        # mkvmerge executables

        self.mkvmerge = getMKVMerge()
        self.mkvmergeEmbedded = getMKVMergeEmbedded(self.appDirectory)

        # Model view
        headers = tableHeaders()
        self.tableData = TableData(headerList=headers, dataList=[])
        self.model = JobsTableModel(self.tableData, self.jobsQueue)
        self.proxyModel = TableProxyModel(self.model)

        # renameWidget is referenced in CommandWidget
        self.rename = RenameWidget(self)

        self.commandEntry = CommandWidget(self, self.proxyModel, self.rename)
        self.jobsOutput = JobsOutputWidget(self)
        self.errorOutput = JobsOutputErrorsWidget(self, log=False)

        # Widgets for tabs
        self.jobsTableView = JobsTableViewWidget(
            self, self.proxyModel, self.controlQueue, _(Text.txt0130)
        )

        # historyWidget and logViewerWidget cannot have parent declared
        # They don't always display and create artifacts when not shown
        # self.historyWidget = JobsHistoryViewWidget(self, groupTitle=_(Text.txt0130))
        # self.historyWidget.tableView.sortByColumn(0, Qt.DescendingOrder)

        # Log view
        self.logViewer = LogViewerWidget()

        # Set output to contain output windows objects
        self.output = OutputWindows(
            self.commandEntry.outputWindow,
            self.jobsOutput,
            self.errorOutput,
        )

        self.tabs = TabWidget(self)

        # Progress information setup
        self.progressBar = DualProgressBar(self, align=Qt.Horizontal)
        self.jobsLabel = QFormatLabel(
            Text.txt0085,
            init=[0, 0, 0, 0, 0],
        )
        self.progress = Progress(self, self.progressBar, self.jobsLabel)

        self.progressSpin = QProgressIndicator(self)

    def _initHelper(self) -> None:
        # work in progress spin
        self.activitySpinner.displayedWhenStopped = True
        self.activitySpinner.color = checkColor(
            QColor(42, 130, 218),
            config.data.get(config.ConfigKey.DarkMode)
        )
        self.activitySpinner.delay = 60

        # Output references setup
        self.commandEntry.output = self.output
        self.jobsTableView.output = self.output
        self.jobsQueue.output = self.output
        self.commandEntry.outputWindow.setReadOnly(True)
        self.jobsOutput.setReadOnly(True)
        self.errorOutput.setReadOnly(True)
        #self.historyWidget.output.setReadOnly(True)
        self.jobsOutput.textChanged.connect(
            self.commandEntry.clearButtonState)

        # Jobs Queue
        self.jobsQueue.progress = self.progress
        self.jobsQueue.proxyModel = self.proxyModel

        # Translation
        self.translateInterface.addSlot(self.commandEntry.translate)
        self.translateInterface.addSlot(self.jobsTableView.translate)
        self.translateInterface.addSlot(self.rename.translate)
        self.translateInterface.addSlot(self.tabs.translate)

        # Tabs
        tabsList = []
        tabsList.append(
            [
                self.commandEntry,
                _(Text.txt0133),
                _(Text.txt0148),
            ]
        )
        tabsList.append(
            [
                self.jobsTableView,
                _(Text.txt0140),
                _(Text.txt0144),
            ]
        )
        tabsList.append(
            [
                self.jobsOutput,
                _(Text.txt0141),
                _(Text.txt0145),
            ]
        )
        tabsList.append(
            [
                self.errorOutput,
                _(Text.txt0152),
                _(Text.txt0146),
            ]
        )
        tabsList.append(
            [
                self.rename,
                _(Text.txt0143) + "+",
                _(Text.txt0147),
            ]
        )
        if config.data.get(config.ConfigKey.LogViewer):
            tabsList.append(
                [
                    self.logViewer,
                    _(Text.txt0149),
                    _(Text.txt0151),
                ]
            )
        else:
            self.logViewer.tab = -1
            self.logViewer.tabWidget = self.tabs
            self.logViewer.title = _(Text.txt0149)
        self.tabs.addTabs(tabsList)

        # Signal connections

        # runJobs Start/Stop
        self.jobsQueue.runJobs.startSignal.connect(
            self.activitySpinner.startAnimation)
        self.jobsQueue.runJobs.finishedSignal.connect(
            self.activitySpinner.stopAnimation)

        # Tabs change signal
        self.tabs.currentChanged.connect(tabChange)

        # tray Icon message
        self.trayIconMessageSignal.connect(self.trayIcon.showMessage)

        # Algorithm
        self.setPreferences.stateChangedAlgorithm.connect(
            self.commandEntry.setDefaultAlgorithm)

        # CRC
        self.setPreferences.stateChangedCRC.connect(
            self.commandEntry.setDefaultCRC)

        # connect log viewer
        config.logViewer.connect(self.logViewer.logMessage)

        # connect JobHistory and commandWidget may not implement
        #self.historyWidget.pasteCommandSignal.connect(self.commandWidget.updateCommand)
        #self.historyWidget.updateAlgorithmSignal.connect(
        #    self.commandWidget.updateAlgorithm
        #)

    def _initUI(self):

        # Create Widgets
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.tabs)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    # endregion Initialization

    # region Events

    def closeEvent(self, event: QEvent) -> None:

        language = config.data.get(config.ConfigKey.Language)
        bAnswer = False
        title = _(Text.txt0080)
        leadQuestionMark = "¿" if language == "es" else ""
        msg = leadQuestionMark + _(Text.txt0081) + "?"

        bAnswer = yesNoDialog(self, msg, title)
        if bAnswer:
            self.configuration(action=config.Action.Save)
            event.accept()
        else:
            event.ignore()

    #def moveEvent(self, event):
    #    print("x=`{}`, y=`{}`".format(event.pos().x(), event.pos().y()))
    #    super(MainWindow, self).moveEvent(event)

    # endregion Events

    # region Overrides

    def setVisible(self, visible):
        """ Override setVisible """

        self.trayIcon.setMenuEnabled(visible)
        super().setVisible(visible)

    # endregion Overrides

    # region Interface

    def createActions(self) -> None:
        """Actions to use in menu interface"""

        self.actPreferences = QActionWidget(
            Text.txt0050,
            self,
            shortcut=Text.txt0026,
            statusTip=Text.txt0051,
            triggered=self.setPreferences.getPreferences
        )

        icon = QIcon(QPixmap(":/images/cross.png"))
        #icon = QIcon(QPixmap(":/images/exit.png"))
        # exitIcon = self.style().standardIcon(QStyle.SP_DialogCloseButton)
        self.actExit = QActionWidget(
            icon,
            Text.txt0021,
            self,
            shortcut=Text.txt0022,
            statusTip=Text.txt0023,
            triggered=self.close
        )

        icon = QIcon(QPixmap(":/images/mkvtoolnix_logo.png"))
        self.actMKVToolnix = QActionWidget(
            icon,
            " ",
            self,
            statusTip=_("Execute embedded mkvtoolnix-gui."),
            triggered=lambda: executeMKVToolnix(self.appDirectory, output=self.output, log=self.log)
        )

        self.actAbort = QActionWidget(
            Text.txt0024,
            self,
            statusTip=Text.txt0025
        )
        self.actAbort.triggered.connect(abort)

        # No status tip statusTip=Text.txt0065,
        self.actAbout = QActionWidget(
            Text.txt0063,
            self,
            triggered=self.about
        )

        # No status statusTip=Text.txt0066,
        self.actAboutQt = QActionWidget(
            Text.txt0064,
            self,
            triggered=QApplication.aboutQt
        )

        self.translateInterface.addSlot(self.actPreferences.translate)
        self.translateInterface.addSlot(self.actExit.translate)
        self.translateInterface.addSlot(self.actAbort.translate)
        self.translateInterface.addSlot(self.actAbout.translate)
        self.translateInterface.addSlot(self.actAboutQt.translate)

    def createMenus(self) -> None:
        """Create the application menus"""

        menuBar = QMenuBar()

        #
        # File menu
        #
        self.fileMenu = QMenuWidget(Text.txt0020)

        #self.fileMenu.setStyleSheet(
        #    """
        #    QMenuWidget::item-line:separator {

        #        color: white;

        #    }
        #    """
        #)

        self.fileMenu.addAction(self.actPreferences)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actAbort)

        menuBar.addMenu(self.fileMenu)
        self.translateInterface.addSlot(self.fileMenu.translate)

        #
        # Help menu
        #
        self.helpMenu = QMenuWidget(Text.txt0060)
        self.helpMenu.addAction(self.actAbout)
        self.helpMenu.addAction(self.actAboutQt)

        menuBar.addMenu(self.helpMenu)
        self.translateInterface.addSlot(self.helpMenu.translate)

        # Attach menu
        self.setMenuBar(menuBar)

    def createToolbars(self) -> None:
        self.fileToolbar = self.addToolBar("File")
        self.fileToolbar.addAction(self.actMKVToolnix)
        #self.fileToolbar.addAction(self.actExit)

    def createStatusbar(self) -> None:

        statusBar = QStatusBar()
        statusBar.addPermanentWidget(VerticalLine())
        statusBar.addPermanentWidget(self.jobsLabel)
        statusBar.addPermanentWidget(VerticalLine())
        statusBar.addPermanentWidget(self.progressBar)
        statusBar.addPermanentWidget(self.activitySpinner)

        self.setStatusBar(statusBar)

    # endregion Interface

    # region Configuration

    def configuration(self, action: str) -> None:
        """
        Read/Write configuration
        """

        defaultFont = QFont()
        defaultFont.fromString(config.data.get(config.ConfigKey.SystemFont))
        defaultFont.setPointSize(14)
        bLogging = False

        if action == config.Action.Reset:
            self.setFont(defaultFont)
            self.setAppFont(defaultFont)

            self.enableLogging(bLogging)

            self.setGeometry(0, 0, 1280, 70)
            centerWidget(self)
        elif action == config.Action.Restore:
            if strFont := config.data.get(config.ConfigKey.Font, defaultFont):
                restoreFont = QFont()
                restoreFont.fromString(strFont)
                self.setFont(restoreFont)
                self.setAppFont(restoreFont)

            if bLogging := config.data.get(config.ConfigKey.Logging):
                self.enableLogging(bLogging)

            if byteGeometry := config.data.get(config.ConfigKey.Geometry):
                self.restoreGeometry(
                    QByteArray.fromBase64(QByteArray(byteGeometry)))
            else:
                self.setGeometry(0, 0, 1280, 720)
                centerWidget(self)
        elif action == config.Action.Save:
            # Update geometry includes position
            base64Geometry = self.saveGeometry().toBase64()
            b = base64Geometry.data()  # b is a bytes string
            config.data.set(config.ConfigKey.Geometry, b)

    def enableLogging(self, state):
        """Activate logging"""

        QOutputTextWidget.logWithCaller = config.data.get(config.ConfigKey.LogWithCaller)

        self.log = state
        self.commandEntry.log = state
        self.jobsOutput.log = state
        self.jobsQueue.log = state
        self.jobsTableView.log = state
        msg = "MAI0001: Start Logging." if state else "MAI0002: Stop Logging."
        logging.info(msg)
        config.data.set(config.ConfigKey.Logging, state)

    def translate(self, language: Optional[str] = None) -> None:
        """
        Set application language the scheme permits runtime changes

        Keyword Arguments:
            language (str) -- language selected (default: {"en"})
        """

        configMessagesCatalog(self, language)

        self.setWindowTitle(_(Text.txt0001))

        self.translateInterface.signal()

    def setAppFont(self, font):
        """
        Set font selected as application default font

        Arguments:
            font {QFont} -- font selected by user
        """

        for action in self.menuBar().actions():
            if not action.isSeparator():
                action.setFont(font)

        for action in self.fileMenu.actions():
            if not action.isSeparator():
                action.setFont(font)

        for action in self.helpMenu.actions():
            if not action.isSeparator():
                action.setFont(font)

        QToolTip.setFont(font)
        config.data.set(config.ConfigKey.Font, font.toString())

    # endregion Configuration

    def about(self) -> None:
        """About"""

        rePythonVersion = re.compile(r"^(.*?) (.*?) (.*?) ")
        pythonVersion = sys.version

        if tmpMatch := rePythonVersion.match(sys.version):
            pythonVersion = tmpMatch[1]

        mkvSystem = getMKVMergeVersion(self.mkvmerge)
        mkvEmbedded = getMKVMergeVersion(self.mkvmergeEmbedded)

        aboutMsg = (f"{config.APPNAME}: {config.VERSION}                   \n\n"
                    f"{_(Text.txt0002)}: {config.AUTHOR}\n"
                    f"{_(Text.txt0003)}: {config.EMAIL}\n\n"
                    f"{_(Text.txt0004)}: {pythonVersion}\n\n"
                    f"{_(Text.txt0067)}: {mkvSystem}\n"
                    f"{_(Text.txt0068)}: {mkvEmbedded}\n")

        QMessageBox.about(self, config.APPNAME, aboutMsg)

@Slot(int)
def tabChange(index):
    """
    tabChange take action when the tab change for save current tab index

    Args:
        index (int): index of current tab
    """

    config.data.set("Tab", index)


def abort():
    """Force Quit"""

    logging.warning("MAI0004: Application Aborted")
    QApplication.exit(1)  # pylint: disable=E1101


def mainApp():
    """Main function"""

    if platform.system() == "Windows":
        # with this the icon in the task bar will change to the one set
        # for the application myAppID is an arbitrary string
        myAppID = "akai10tsuki.MKVBatchMultiplex.mkv.3.0.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myAppID)
        # setup dark mode
        sys.argv += ['-platform', 'windows:darkmode=2']

    app = QApplication(sys.argv)
    config.init(app=app)
    MainWindow()

    # set Fusion style palette adjust for Linux disable button text
    setAppStyle(app)

    app.exec()

    config.close()

# This if for Pylance _() is not defined
def _(dummy):
    return dummy


del _


if __name__ == '__main__':
    sys.exit(mainApp())
