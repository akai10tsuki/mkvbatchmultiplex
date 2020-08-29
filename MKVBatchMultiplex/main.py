#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
JobsTable
"""

# MAI0003

# import ctypes
import gettext
import logging
import os
import platform
import sys
import threading
import webbrowser

from collections import deque
from pathlib import Path

from PySide2.QtCore import QByteArray, Slot, Signal
from PySide2.QtGui import QColor, QFont, QIcon, Qt
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QMainWindow,
    QMessageBox,
    QMenuBar,
    QVBoxLayout,
    QToolTip,
    QStatusBar,
    QStyle,
    QSystemTrayIcon,
    QWidget,
)

import vsutillib.media as media

from vsutillib.pyqt import (
    centerWidget,
    checkColor,
    darkPalette,
    DualProgressBar,
    QFormatLabel,
    QOutputTextWidget,
    QActionWidget,
    QMenuWidget,
    QProgressIndicator,
    TabWidget,
    VerticalLine,
)

from . import config
from .dataset import TableData, tableHeaders
from .jobs import JobQueue
from .models import TableProxyModel, JobsTableModel
from .widgets import (
    CommandWidget,
    JobsHistoryViewWidget,
    JobsOutputErrorsWidget,
    JobsOutputWidget,
    JobsTableViewWidget,
    LogViewerWidget,
    PreferencesDialogWidget,
    RenameWidget,
)
from .utils import (
    Text,
    OutputWindows,
    Progress,
    QSystemTrayIconWidget,
    yesNoDialog,
    setLanguageMenus,
    SetLanguage,
    UiSetLanguage,
)


class MainWindow(QMainWindow):  # pylint: disable=R0902
    """Main window of application"""

    log = False
    trayIconMessageSignal = Signal(str, str, object)

    def __init__(self, parent=None, palette=None):
        super(MainWindow, self).__init__(parent)

        self.defaultPalette = palette
        self.parent = parent

        # initialize the gazillion variables
        self._initVars()

        # Widow Title self.appDirectory on _initVars()
        self.setWindowTitle(config.APPNAME + ": " + config.DESCRIPTION)
        self.setWindowIcon(
            QIcon(str(self.appDirectory.parent) + "/images/Itsue256x256.png")
        )

        # Setup User Interface
        self._initMenu()
        self._initControls()
        self._initUI()
        self._initHelper()

        # Restore configuration elements
        self.configuration(action=config.Action.Restore)
        self.setLanguage()

        # tray icon
        self.trayIcon = QSystemTrayIconWidget(self, self.windowIcon())
        self.trayIcon.show()

        # for taskbar icon to work show must be called in __init__
        self.show()

        # Must init after show call
        self.progressBar.initTaskbarButton()

        # self.trayIcon.showMessage(
        #    "Information - MKVBatchMultiplex",
        #    "Finished initialization.",
        #    QSystemTrayIcon.Information,
        # )

        # tray Icon message
        self.trayIconMessageSignal.connect(self.trayIcon.showMessage)

    def _initVars(self):

        #
        # Where am I running from
        #
        if getattr(sys, "frozen", False):
            # Running in a pyinstaller bundle
            self.appDirectory = Path(os.path.dirname(__file__))
        else:
            self.appDirectory = Path(os.path.realpath(__file__))

        self.controlQueue = deque()
        self.jobsQueue = JobQueue(self, controlQueue=self.controlQueue)
        self.setLanguageWidget = SetLanguage()
        self.uiSetLanguage = UiSetLanguage(self)
        self.progressBar = DualProgressBar(self, align=Qt.Horizontal)
        self.jobsLabel = QFormatLabel(Text.txt0085, init=[0, 0, 0, 0, 0],)
        self.progress = Progress(self, self.progressBar, self.jobsLabel)

        headers = tableHeaders()
        self.tableData = TableData(headerList=headers, dataList=[])
        self.model = JobsTableModel(self.tableData, self.jobsQueue)
        self.proxyModel = TableProxyModel(self.model)
        self.jobsQueue.proxyModel = self.proxyModel
        self.jobsQueue.progress = self.progress

        self.progressSpin = QProgressIndicator(self)
        self.setPreferences = PreferencesDialogWidget(self)

    def _initMenu(self):  # pylint: disable=too-many-statements

        menuBar = QMenuBar()
        # menuBar = self.menuBar()

        # File SubMenu
        fileMenu = QMenuWidget(Text.txt0020)
        closeIcon = self.style().standardIcon(QStyle.SP_DialogCloseButton)

        # Preferences
        actPreferences = QActionWidget(
            "&Preferences", self, shortcut="Ctrl+P", tooltip="Setup program options"
        )
        actPreferences.triggered.connect(self.setPreferences.getPreferences)

        # Exit application
        actExit = QActionWidget(
            closeIcon, Text.txt0021, self, shortcut=Text.txt0022, tooltip=Text.txt0023,
        )
        actExit.triggered.connect(self.close)

        # Abort
        actAbort = QActionWidget(Text.txt0024, self, tooltip=Text.txt0025)
        actAbort.triggered.connect(abort)

        # Add actions to SubMenu
        fileMenu.addAction(actPreferences)
        fileMenu.addSeparator()
        fileMenu.addAction(actExit)
        fileMenu.addSeparator()
        fileMenu.addAction(actAbort)
        menuBar.addMenu(fileMenu)

        # Help Menu
        actHelpContents = QActionWidget(Text.txt0061, self, textSuffix="...")
        actHelpContents.triggered.connect(lambda: _help(self.appDirectory, 0))
        actHelpUsing = QActionWidget(Text.txt0062, self)
        actHelpUsing.triggered.connect(lambda: _help(self.appDirectory, 1))
        actAbout = QActionWidget(Text.txt0063, self)
        actAbout.triggered.connect(self.about)
        actAboutQt = QActionWidget(Text.txt0064, self)
        actAboutQt.triggered.connect(self.aboutQt)
        helpMenu = QMenuWidget(Text.txt0060)
        helpMenu.addAction(actHelpContents)
        helpMenu.addAction(actHelpUsing)
        helpMenu.addSeparator()
        helpMenu.addAction(actAbout)
        helpMenu.addAction(actAboutQt)
        menuBar.addMenu(helpMenu)

        # Init status var
        statusBar = QStatusBar()  # pylint: disable=unused-variable
        statusBar.addPermanentWidget(VerticalLine())
        statusBar.addPermanentWidget(self.jobsLabel)
        statusBar.addPermanentWidget(VerticalLine())
        statusBar.addPermanentWidget(self.progressBar)
        statusBar.addPermanentWidget(self.progressSpin)

        self.setMenuBar(menuBar)
        self.setStatusBar(statusBar)

    def _initControls(self):

        # Widgets for tabs
        self.tableViewWidget = JobsTableViewWidget(
            self, self.proxyModel, self.controlQueue, "Jobs Table"
        )
        self.tableViewWidget.tableView.sortByColumn(0, Qt.AscendingOrder)
        self.renameWidget = RenameWidget(self)
        self.commandWidget = CommandWidget(self, self.proxyModel)
        self.jobsOutput = JobsOutputWidget(self)
        self.errorOutput = JobsOutputErrorsWidget(self)
        self.historyWidget = JobsHistoryViewWidget(groupTitle="Jobs Table")
        self.historyWidget.tableView.sortByColumn(0, Qt.DescendingOrder)
        self.logViewerWidget = LogViewerWidget()

        self.tabs = TabWidget(self)

        tabsList = []
        tabsList.append(
            [
                self.commandWidget,
                "Command",
                "Enter generated command and see any test output",
            ]
        )
        tabsList.append(
            [
                self.tableViewWidget,
                "Jobs",
                "Jobs table to manipulate job status and Queue",
            ]
        )
        tabsList.append(
            [
                self.jobsOutput,
                "Jobs Output",
                "Output generated by jobs and job handling",
            ]
        )
        tabsList.append(
            [
                self.errorOutput,
                "Jobs Errors",
                "Errors generated by processing or running of jobs",
            ]
        )
        tabsList.append(
            [
                self.renameWidget,
                "Rename Files",
                "Rename the output files ej. Series Name - S01E01.mkv, ...",
            ]
        )
        if config.data.get(config.ConfigKey.LogViewer):
            tabsList.append(
                [
                    self.logViewerWidget,
                    "Log Viewer",
                    "Messages registered in current running log",
                ]
            )
        else:
            self.logViewerWidget.tab = -1
            self.logViewerWidget.tabWidget = self.tabs
            self.logViewerWidget.title = "Log Viewer"
        if config.data.get(config.ConfigKey.JobHistory):
            tabsList.append(
                [self.historyWidget, "Jobs History", "Examine any jobs saved."]
            )
        else:
            self.historyWidget.tab = -1
            self.historyWidget.tabWidget = self.tabs
            self.historyWidget.title = "Jobs History"

        self.tabs.addTabs(tabsList)

    def _initHelper(self):
        """
        _initHelper setup signals, do any late binds and misc configuration
        """

        # progress spin
        self.progressSpin.displayedWhenStopped = True
        self.progressSpin.color = checkColor(
            QColor(42, 130, 218), config.data.get(config.ConfigKey.DarkMode)
        )
        self.progressSpin.delay = 60

        # Set output to contain output windows objects
        self.output = OutputWindows(
            self.commandWidget.outputWindow, self.jobsOutput, self.errorOutput,
        )
        self.commandWidget.output = self.output
        self.tableViewWidget.output = self.output
        self.jobsQueue.output = self.output
        self.commandWidget.rename = self.renameWidget
        self.commandWidget.outputWindow.setReadOnly(True)
        self.jobsOutput.setReadOnly(True)
        self.errorOutput.setReadOnly(True)
        # self.historyWidget.output.setReadOnly(True)
        self.jobsOutput.textChanged.connect(self.commandWidget.resetButtonState)

        # setup widgets setLanguage to SetLanguage change signal
        self.setLanguageWidget.addSlot(self.tableViewWidget.setLanguage)
        self.setLanguageWidget.addSlot(self.commandWidget.setLanguage)
        self.setLanguageWidget.addSlot(self.tabs.setLanguage)
        self.setLanguageWidget.addSlot(self.renameWidget.setLanguage)
        # self.setLanguageWidget.addSlot(self.historyWidget.setLanguage)
        self.setLanguageWidget.addSlot(self.setPreferences.retranslateUi)
        # connect to tabs widget tab change Signal
        self.tabs.currentChanged.connect(tabChange)

        # connect to runJobs Start/Stop SigNal
        self.jobsQueue.runJobs.startSignal.connect(self.progressSpin.startAnimation)
        self.jobsQueue.runJobs.finishedSignal.connect(self.progressSpin.stopAnimation)

        # connect log viewer
        config.logViewer.connect(self.logViewerWidget.logMessage)

    def _initUI(self):

        # Create Widgets
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.tabs)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        """
        Override QMainWindow.closeEvent

        Save configuration state before exit
        """

        language = config.data.get(config.ConfigKey.Language)
        bAnswer = False
        title = _(Text.txt0080)
        leadQuestionMark = "¿" if language == "es" else ""

        if threading.activeCount() > 1:
            msg = _(Text.txt0089) + ". " + leadQuestionMark + _(Text.txt0090) + "?"
        else:
            msg = leadQuestionMark + _(Text.txt0081) + "?"

        bAnswer = yesNoDialog(self, msg, title)

        if bAnswer:
            self.configuration(action=config.Action.Save)
            event.accept()
        else:
            event.ignore()

    def moveEvent(self, event):

        # Update geometry includes position
        base64Geometry = self.saveGeometry().toBase64()
        b = base64Geometry.data()  # b is a bytes string
        config.data.set(config.ConfigKey.Geometry, b)
        event.ignore()

    def resizeEvent(self, event):

        # Update geometry includes position
        base64Geometry = self.saveGeometry().toBase64()
        b = base64Geometry.data()  # b is a bytes string
        config.data.set(config.ConfigKey.Geometry, b)
        event.ignore()

    def setVisible(self, visible):
        """ Override setVisible """

        self.trayIcon.setMenuEnabled(visible)
        super().setVisible(visible)

    @Slot(str)
    def iconActivated(self, reason):
        """Systray Icon"""

        print("main is icon activated")
        if reason == QSystemTrayIcon.Trigger:
            pass
        if reason == QSystemTrayIcon.DoubleClick:
            pass
        if reason == QSystemTrayIcon.MiddleClick:
            pass

    def configuration(self, action=None):
        """
        Read and write configuration
        """

        defaultFont = QFont()
        defaultFont.fromString(config.data.get(config.ConfigKey.SystemFont))
        defaultFont.setPointSize(14)
        bLogging = False

        if action == config.Action.Reset:
            # Font
            self.setFont(defaultFont)
            self.setAppFont(defaultFont)
            # Logging
            self.enableLogging(bLogging)
            # Geometry
            self.setGeometry(0, 0, 1280, 720)
            centerWidget(self)

        elif action == config.Action.Restore:
            # Font
            if strFont := config.data.get(config.ConfigKey.Font):
                restoreFont = QFont()
                restoreFont.fromString(strFont)
                self.setFont(restoreFont)
                self.setAppFont(restoreFont)
            else:
                self.setFont(defaultFont)
                self.setAppFont(defaultFont)

            # Logging
            if bLogging := config.data.get(config.ConfigKey.Logging):
                self.enableLogging(bLogging)

            # Geometry
            if byteGeometry := config.data.get(config.ConfigKey.Geometry):
                self.restoreGeometry(QByteArray.fromBase64(QByteArray(byteGeometry)))
            else:
                self.setGeometry(0, 0, 1280, 720)
                centerWidget(self)

            # Current tab
            if tabIndex := config.data.get("Tab"):
                # setting tab to jobs
                # self.tabs.setCurrentIndexSignal.emit(0)
                self.tabs.setCurrentIndexSignal.emit(tabIndex)

        elif action == config.Action.Save:

            if action == config.Action.Save:
                config.data.saveToFile()

    def checkDependencies(self):
        """check if MediaInfo library is present"""

        if platform.system() == "Linux":
            libFiles = media.isMediaInfoLib()

            if not libFiles:
                self.output.command.emit(
                    "\nMediaInfo library not found can not process jobs.\n\n",
                    {"color": Qt.red},
                )
                # self.jobs.jobsStatus(JobStatus.Blocked)

    def enableLogging(self, state):
        """Activate logging"""

        self.log = state
        self.commandWidget.log = state
        self.jobsOutput.log = state
        self.errorOutput.log = state
        self.tableViewWidget.log = state
        self.jobsQueue.log = state
        msg = "MAI0001: Start Logging." if state else "MAI0002: Stop Logging."
        logging.info(msg)
        config.data.set(config.ConfigKey.Logging, state)

    def setAppFont(self, font):
        """
        Set font selected as application default font

        Arguments:
            font {QFont} -- font selected by user
        """

        for a in self.menuBar().actions():
            # menus on menubar are QAction classes
            # get the menu
            m = a.menu()
            m.setFont(font)

            for e in m.actions():
                if e.isSeparator():
                    continue
                elif isinstance(e, QActionWidget):
                    # subclass also QAction type but never a menu
                    continue
                elif isinstance(e, QAction):
                    try:
                        i = e.menu()
                        i.setFont(font)
                    except AttributeError:
                        continue

        QToolTip.setFont(font)
        config.data.set(config.ConfigKey.Font, font.toString())

    def setLanguage(self, language=None, menuItem=None):
        """
        Set application language the scheme permits runtime changes

        Keyword Arguments:
            language (str) -- language selected (default: {"en"})
            menuItem (QMenuWidget) -- menu object making the call for checkmark update
        """

        if language is None:
            language = config.data.get(config.ConfigKey.Language)

        lang = gettext.translation(
            config.NAME, localedir=str(config.LOCALE), languages=[language]
        )
        if self.uiSetLanguage.setLanguage(language):
            pass
        lang.install(names=("ngettext",))
        config.data.set(config.ConfigKey.Language, language)
        self.setWindowTitle(Text.txt0001)
        self.jobsLabel.template = " " + _(Text.txt0085) + " "
        self.progressBar.label = _(Text.txt0091) + ":"

        # Set langque main windows
        setLanguageMenus(self.menuBar().actions())

        # Update checkboxes in the select language menu
        if menuItem is not None:
            for a in self.languageMenu.actions():
                a.setChecked(False)
            menuItem.setChecked(True)

        # Update language on other window widgets
        self.setLanguageWidget.emitSignal()

    def about(self):
        """About"""
        aboutMsg = config.APPNAME + ": {}\n\n"
        aboutMsg += _(Text.txt0002) + ": {}\n"
        aboutMsg += _(Text.txt0003) + ": {}\n\n"
        aboutMsg += _(Text.txt0004) + ":\n{}\n"

        aboutMsg = aboutMsg.format(
            config.VERSION, config.AUTHOR, config.EMAIL, sys.version
        )
        QMessageBox.about(self, config.APPNAME, aboutMsg)

    def aboutQt(self):
        """About QT"""

        QMessageBox.aboutQt(self, config.APPNAME)


@Slot(int)
def tabChange(index):
    """
    tabChange take action when the tab change for save current tab index

    Args:
        index (int): index of current tab
    """

    config.data.set("Tab", index)


def _help(pth, index=0):
    """open web RTD page"""

    if index == 1:
        htmlPath = "file:///" + str(pth.parent) + "/html/using.html"
    else:
        htmlPath = "file:///" + str(pth.parent) + "/html/index.html"

    webbrowser.open(htmlPath, new=2, autoraise=True)


def abort():
    """Force Quit"""

    QApplication.quit()  # pylint: disable=E1101


def mainApp():
    """Main"""

    # PySide2 app
    app = QApplication(sys.argv)

    config.init(app=app)

    # Palette will change on macOS according to current theme
    # will create a poor mans dark theme for windows
    if platform.system() == "Windows":
        # pass
        darkPalette(app)
        config.data.set(config.ConfigKey.DarkMode, True)
        QOutputTextWidget.isDarkMode = True

    MainWindow()
    app.exec_()
    config.close()


if __name__ == "__main__":
    sys.exit(mainApp())
