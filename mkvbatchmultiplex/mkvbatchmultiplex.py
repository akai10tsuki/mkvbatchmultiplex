#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
mkvBatchMultiplex
=================

Program for batch processing mkvmerge commands

The program will take command line argument from mkvtoolnix-gui
from MKVToolNix

Multiplexer->Show command line

It will analyze the command and apply the same multiplex instructions to all
the files in the same directory if more than one file is involved in the
command they must match in numbers.

Develop on Windows

Works on:

    * Tested on ubuntu 18.04

Libraries and programs used:

    python 3.6-3.7
    pymediainfo 4.0
    mediainfo-17.10->18.12
    PySide2 5.12

Target program:
    MKVToolNix - tested with versions v17.0.0-34.0.0
"""
# MWW0001

import logging
import logging.handlers
import sys
import os
import platform
import webbrowser
from pathlib import Path
from queue import Queue
from collections import deque

from PySide2.QtCore import QByteArray, Qt, QThreadPool, Signal
from PySide2.QtGui import QIcon, QFont
from PySide2.QtWidgets import (QAction, QApplication, QDesktopWidget, qApp,
                               QMainWindow, QMessageBox, QToolBar, QVBoxLayout,
                               QWidget, QFontDialog, QToolTip)

import vsutillib.media as media
import vsutillib.pyqt as pyqt

from . import config
from .widgets import (DualProgressBar, MKVCommandWidget, MKVTabsWidget,
                      FormatLabel, MKVOutputWidget, MKVJobsTableWidget,
                      MKVRenameWidget)
from .jobs import JobQueue, JobStatus
from . import utils


class MKVMultiplexApp(QMainWindow):  # pylint: disable=R0902
    """Main window of application"""

    log = False
    raiseErrors = False
    outputMainSignal = Signal(str, dict)
    outputQueue = Signal(str, dict)
    outputError = Signal(str, dict)
    addJob = Signal(int, str)
    setJobStatus = Signal(int, str)

    def __init__(self, parent=None):
        super(MKVMultiplexApp, self).__init__(parent)

        self.workQueue = deque()
        self.jobProcessQueue = Queue()
        self.jobSubprocessQueue = Queue()
        self.threadpool = QThreadPool()
        self.jobs = JobQueue(self.workQueue)
        self.actSetupLogging = None
        self.menuItems = []

        if getattr(sys, 'frozen', False):
            # Running in pyinstaller bundle
            self.appDirectory = Path(os.path.dirname(__file__))  # pylint: disable=E1101,W0212
        else:
            self.appDirectory = Path(os.path.realpath(__file__))

        self.setWindowTitle("MKVMERGE: Batch Multiplex")
        self.setWindowIcon(
            QIcon(
                str(self.appDirectory.parent) +
                "/images/mkvBatchMultiplex.png"))

        # menu and widgets
        self._initMenu()
        self._initHelper()

        # Read configuration elements
        self.restoreConfig()

        self.checkDependencies()

    def _initHelper(self):

        # Create Widgets

        self.renameWidget = MKVRenameWidget(self)

        self.commandWidget = MKVCommandWidget(self, self.threadpool, self.jobs,
                                              self.jobProcessQueue,
                                              self.jobSubprocessQueue,
                                              self.renameWidget)
        self.outputQueueWidget = MKVOutputWidget(self)
        self.outputErrorWidget = MKVOutputWidget(self)
        self.jobsWidget = MKVJobsTableWidget(self, self.jobProcessQueue,
                                             self.jobSubprocessQueue)

        # Connect signals to print in outputWidgets and update jobsWidget
        self.jobs.setOutputSignal(
            outputJobSlotConnection=self.outputQueueWidget.makeConnection,
            outputErrorSlotConnection=self.outputErrorWidget.makeConnection,
            addJobToTableSlotConnection=self.jobsWidget.makeConnectionAddJob,
            updateStatusSlotConnection=self.jobsWidget.
            makeConnectionSetJobStatus,
            clearOutput=self.clearOutput)

        # Connect to signal when a row is clicked on jobsWidget job output
        # will update in outputWidgets
        self.jobs.connectToShowJobOutput(self.jobsWidget.showJobOutput)
        self.jobs.connectToStatus(self.jobsWidget.jobsTable.updateJobStatus)

        self.renameWidget.setAccessibleName('renameWidget')
        # Create tabs and insert Widgets
        self.tabsWidget = MKVTabsWidget(self, self.commandWidget,
                                        self.jobsWidget,
                                        self.outputQueueWidget,
                                        self.outputErrorWidget,
                                        self.renameWidget)

        self.tabs = self.tabsWidget.tabs
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.tabsWidget)
        self.setCentralWidget(widget)

        # restore config

    def _initMenu(self):

        menuBar = self.menuBar()

        actExit = QAction(
            QIcon(str(self.appDirectory.parent) + "/images/cross-circle.png"),
            "&Exit", self)
        actExit.setShortcut("Ctrl+E")
        actExit.setStatusTip("Exit application")
        actExit.triggered.connect(self.close)

        actAbort = QAction("Abort", self)
        actAbort.setStatusTip("Force exit")
        actAbort.triggered.connect(abort)

        fileMenu = menuBar.addMenu("&File")
        fileMenu.addAction(actExit)
        fileMenu.addAction(actAbort)

        self.menuItems.append(fileMenu)

        self.actSetupLogging = QAction("Enable logging", self, checkable=True)
        self.actSetupLogging.setStatusTip(
            "Enable session logging in ~/.mkvBatchMultiplex/mkvBatchMultiplex.log"
        )
        self.actSetupLogging.triggered.connect(self.setupLogging)

        actSelectFont = QAction("Font", self)
        actSelectFont.setStatusTip("")
        actSelectFont.triggered.connect(self.selectFont)

        actRestoreDefaults = QAction("Restore Defaults", self)
        actRestoreDefaults.triggered.connect(self.restoreDefaults)

        settingsMenu = menuBar.addMenu("&Settings")
        settingsMenu.addAction(self.actSetupLogging)
        settingsMenu.addAction(actSelectFont)
        settingsMenu.addAction(actRestoreDefaults)

        self.menuItems.append(settingsMenu)

        # Help Menu

        actHelpContents = QAction("Contents...", self)
        actHelpContents.triggered.connect(lambda: self.help(0))

        actHelpUsing = QAction("Using", self)
        actHelpUsing.triggered.connect(lambda: self.help(1))

        actAbout = QAction("About", self)
        actAbout.triggered.connect(self.about)

        actAboutQt = QAction("About QT", self)
        actAboutQt.triggered.connect(self.aboutQt)

        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(actHelpContents)
        helpMenu.addAction(actHelpUsing)
        helpMenu.addAction(actAbout)
        helpMenu.addAction(actAboutQt)

        self.menuItems.append(helpMenu)

        tb = QToolBar("Exit", self)
        tb.addAction(actExit)
        self.addToolBar(tb)

        self.progressbar = DualProgressBar(align=Qt.Horizontal)
        self.jobsLabel = FormatLabel(
            "Job(s): {0:3d} Current: {1:3d} File: {2:3d} of {3:3d} Errors: {4:3d}",
            init=[0, 0, 0, 0, 0])

        statusBar = self.statusBar()
        statusBar.addPermanentWidget(self.jobsLabel)
        statusBar.addPermanentWidget(self.progressbar)

    def resetFont(self, font):
        """
        Set font to the GUI elements

        Args:
            font (str): new font
        """
        for m in self.menuItems:
            m.setFont(font)

        # hack until discover why is ingnoring parent font or unable to use it
        # using only family and point size on new QFont works??
        self.jobsWidget.jobsTable.setFont(
            QFont(font.family(), font.pointSize()))

        QToolTip.setFont(font)

    def clearOutput(self):
        """Clear output for JobQueue"""

        self.outputQueueWidget.clear()
        self.outputErrorWidget.clear()

    def closeEvent(self, event):
        """
        Save window state before exit
        """

        self.commandWidget.textOutputWindow.makeConnection(
            self.outputMainSignal)
        jobsStatus = self.jobs.jobsStatus()

        if jobsStatus == JobStatus.Aborted:

            event.accept()

        else:

            if jobsStatus == JobStatus.Running:

                result = pyqt.messageBoxYesNo(
                    self, "Confirm Abort...",
                    "Jobs running are you sure you want to stop them?",
                    QMessageBox.Warning)

            else:

                result = pyqt.messageBoxYesNo(
                    self, "Confirm Exit...               ",
                    "Are you sure you want to exit?", QMessageBox.Question)

            if result == QMessageBox.Yes:
                self.saveConfig()

                if jobsStatus == JobStatus.Running:
                    self.outputMainSignal.emit(
                        "\nJobs running aborting jobs...\n\n",
                        {'color': Qt.blue})
                    self.jobSubprocessQueue.put(JobStatus.Abort)
                    event.ignore()

                else:
                    event.accept()
            else:
                event.ignore()

    def setupLogging(self, state):
        """Activate logging"""
        if state:
            self.log = True
            logging.info("MW0001: Start logging.")
        else:
            self.log = False
            logging.info("MW0002: Stop logging.")

        # Setup logging
        MKVCommandWidget.setLogging(self.log)

        MKVTabsWidget.log = self.log
        MKVOutputWidget.log = self.log
        MKVJobsTableWidget.log = self.log
        JobQueue.log = self.log

    def selectFont(self):
        """Select Font"""

        font = self.font()

        fontDialog = QFontDialog()
        utils.centerWidgets(fontDialog, self)

        valid, font = fontDialog.getFont(font)

        if valid:
            self.setFont(font)
            self.resetFont(font)

    def saveConfig(self):
        """
        set configuration data to save
        """

        config.data.set(Key.kLogging, self.actSetupLogging.isChecked())

        base64Geometry = self.saveGeometry().toBase64()
        b = base64Geometry.data()
        config.data.set(Key.kGeometry, b)

        font = self.font()
        config.data.set(Key.kFont, font.toString())

        index = self.tabs.currentIndex()
        if index != 4:
            index = 0
        config.data.set(Key.kTab, index)

    def restoreConfig(self, resetDefaults=False):
        """Restore configuration if any"""

        defaultFont = QFont("Segoe UI", 9)

        bLogging = False

        if resetDefaults:
            self.setFont(defaultFont)
            self.resetFont(defaultFont)
            self.actSetupLogging.setChecked(bLogging)
            self.setupLogging(bLogging)
            self.setGeometry(0, 0, 1280, 720)
            self.tabs.setCurrentIndex(1)

            utils.centerWidgets(self)

        else:

            # restore font
            strFont = config.data.get(Key.kFont)
            if strFont is not None:
                restoreFont = QFont()
                restoreFont.fromString(strFont)
                self.setFont(restoreFont)
                self.resetFont(restoreFont)
            else:
                self.setFont(defaultFont)

            # restore logging status
            bLogging = config.data.get(Key.kLogging)
            if bLogging is not None:
                self.actSetupLogging.setChecked(bLogging)
                self.setupLogging(bLogging)

            # restore window size and position
            byteGeometry = config.data.get(Key.kGeometry)
            if byteGeometry is not None:
                # byteGeometry is bytes string
                self.restoreGeometry(
                    QByteArray.fromBase64(QByteArray(byteGeometry)))
            else:
                self.setGeometry(0, 0, 1280, 720)
                utils.centerWidgets(self)

            # restore open tab
            tabIndex = config.data.get(Key.kTab)
            if tabIndex:
                self.tabs.setCurrentIndex(tabIndex)

    def restoreDefaults(self):
        """restore defaults settings"""

        result = QMessageBox.question(self, "Confirm Restore...",
                                      "Restore default settings ?",
                                      QMessageBox.Yes | QMessageBox.No)

        if result == QMessageBox.Yes:
            self.restoreConfig(resetDefaults=True)

    def checkDependencies(self):
        """check if MediaInfo library is present"""

        if platform.system() == "Linux":

            libFiles = media.isMediaInfoLib()

            if not libFiles:
                self.commandWidget.textOutputWindow.insertText(
                    "\nMediaInfo library not found can not process jobs.\n\n",
                    {'color': Qt.red})
                self.jobs.jobsStatus(JobStatus.Blocked)

    def help(self, index=0):
        """open web RTD page"""

        if index == 1:
            htmlPath = "file:///" + str(
                self.appDirectory.parent) + "/html/using.html"
        else:
            htmlPath = "file:///" + str(
                self.appDirectory.parent) + "/html/index.html"

        webbrowser.open(htmlPath, new=2, autoraise=True)

    def about(self):
        """About"""
        aboutMsg = "MKVBatchMultiplex: {}\n\n"
        aboutMsg += "Author: {}\n"
        aboutMsg += "email: {}\n\n"
        aboutMsg += "Python Vertion:\n{}\n"

        aboutMsg = aboutMsg.format(config.VERSION, config.AUTHOR, config.EMAIL,
                                   sys.version)
        QMessageBox.about(self, 'MKVBatchMultiplex', aboutMsg)

    def aboutQt(self):
        """About QT"""
        QMessageBox.aboutQt(self, 'MKVBatchMultiplex')


class Key:
    """Keys for configuration"""

    kLogging = "logging"
    kGeometry = "geometry"
    kFont = "font"
    kTab = "tab"
    kTabText = "tabText"


def centerWidgetsToDelete(widget, parent=None):
    """center widget based on parent or screen geometry"""

    if parent is None:
        parent = widget.parentWidget()

    if parent:
        widget.move(parent.frameGeometry().center() -
                    widget.frameGeometry().center())

    else:
        widget.move(QDesktopWidget().availableGeometry().center() -
                    widget.frameGeometry().center())


def abort():
    """Force Quit"""

    qApp.quit()  # pylint: disable=E1101


def mainApp():
    """Main"""

    config.init()

    app = QApplication(sys.argv)
    win = MKVMultiplexApp()
    win.show()
    app.exec_()

    config.close()
