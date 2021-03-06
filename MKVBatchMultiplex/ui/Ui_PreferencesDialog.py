# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreferencesDialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        if not PreferencesDialog.objectName():
            PreferencesDialog.setObjectName(u"PreferencesDialog")
        PreferencesDialog.resize(744, 507)
        font = QFont()
        font.setPointSize(14)
        PreferencesDialog.setFont(font)
        PreferencesDialog.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.btnBox = QDialogButtonBox(PreferencesDialog)
        self.btnBox.setObjectName(u"btnBox")
        self.btnBox.setGeometry(QRect(460, 430, 241, 32))
        self.btnBox.setOrientation(Qt.Horizontal)
        self.btnBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.grpBox = QGroupBox(PreferencesDialog)
        self.grpBox.setObjectName(u"grpBox")
        self.grpBox.setGeometry(QRect(30, 40, 681, 361))
        self.lblInterfaceLanguage = QLabel(self.grpBox)
        self.lblInterfaceLanguage.setObjectName(u"lblInterfaceLanguage")
        self.lblInterfaceLanguage.setGeometry(QRect(21, 42, 172, 23))
        self.fcmbBoxFontFamily = QFontComboBox(self.grpBox)
        self.fcmbBoxFontFamily.setObjectName(u"fcmbBoxFontFamily")
        self.fcmbBoxFontFamily.setGeometry(QRect(199, 82, 381, 29))
        self.chkBoxRestoreWindowSize = QCheckBox(self.grpBox)
        self.chkBoxRestoreWindowSize.setObjectName(u"chkBoxRestoreWindowSize")
        self.chkBoxRestoreWindowSize.setGeometry(QRect(21, 274, 641, 27))
        self.label = QLabel(self.grpBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(203, 46, 16, 23))
        self.chkBoxEnableLogging = QCheckBox(self.grpBox)
        self.chkBoxEnableLogging.setObjectName(u"chkBoxEnableLogging")
        self.chkBoxEnableLogging.setGeometry(QRect(21, 122, 641, 27))
        self.lblFontAndSize = QLabel(self.grpBox)
        self.lblFontAndSize.setObjectName(u"lblFontAndSize")
        self.lblFontAndSize.setGeometry(QRect(21, 82, 102, 23))
        self.chkBoxEnableJobHistory = QCheckBox(self.grpBox)
        self.chkBoxEnableJobHistory.setObjectName(u"chkBoxEnableJobHistory")
        self.chkBoxEnableJobHistory.setGeometry(QRect(21, 198, 641, 27))
        self.chkBoxEnableLogViewer = QCheckBox(self.grpBox)
        self.chkBoxEnableLogViewer.setObjectName(u"chkBoxEnableLogViewer")
        self.chkBoxEnableLogViewer.setGeometry(QRect(45, 160, 611, 27))
        self.chkBoxEnableLogViewer.setBaseSize(QSize(0, 0))
        self.cmbBoxInterfaceLanguage = QComboBox(self.grpBox)
        self.cmbBoxInterfaceLanguage.setObjectName(u"cmbBoxInterfaceLanguage")
        self.cmbBoxInterfaceLanguage.setGeometry(QRect(199, 42, 461, 29))
        self.spinBoxFontSize = QSpinBox(self.grpBox)
        self.spinBoxFontSize.setObjectName(u"spinBoxFontSize")
        self.spinBoxFontSize.setGeometry(QRect(590, 82, 71, 29))
        self.chkBoxAutoSaveJobHistory = QCheckBox(self.grpBox)
        self.chkBoxAutoSaveJobHistory.setObjectName(u"chkBoxAutoSaveJobHistory")
        self.chkBoxAutoSaveJobHistory.setGeometry(QRect(45, 236, 611, 27))
        self.chkBoxAutoSaveJobHistory.setBaseSize(QSize(0, 0))
        self.frame = QFrame(self.grpBox)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(20, 310, 621, 41))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.lblAlgorithm = QLabel(self.frame)
        self.lblAlgorithm.setObjectName(u"lblAlgorithm")
        self.lblAlgorithm.setGeometry(QRect(10, 0, 121, 41))
        self.rbZero = QRadioButton(self.frame)
        self.rbZero.setObjectName(u"rbZero")
        self.rbZero.setGeometry(QRect(130, 0, 41, 41))
        self.rbOne = QRadioButton(self.frame)
        self.rbOne.setObjectName(u"rbOne")
        self.rbOne.setGeometry(QRect(180, 0, 41, 41))
        self.rbTwo = QRadioButton(self.frame)
        self.rbTwo.setObjectName(u"rbTwo")
        self.rbTwo.setGeometry(QRect(230, 0, 41, 41))
        self.btnRestoreDefaults = QPushButton(PreferencesDialog)
        self.btnRestoreDefaults.setObjectName(u"btnRestoreDefaults")
        self.btnRestoreDefaults.setGeometry(QRect(50, 430, 351, 34))
        QWidget.setTabOrder(self.cmbBoxInterfaceLanguage, self.fcmbBoxFontFamily)
        QWidget.setTabOrder(self.fcmbBoxFontFamily, self.spinBoxFontSize)
        QWidget.setTabOrder(self.spinBoxFontSize, self.chkBoxEnableLogging)
        QWidget.setTabOrder(self.chkBoxEnableLogging, self.chkBoxEnableLogViewer)
        QWidget.setTabOrder(self.chkBoxEnableLogViewer, self.chkBoxEnableJobHistory)
        QWidget.setTabOrder(self.chkBoxEnableJobHistory, self.chkBoxAutoSaveJobHistory)
        QWidget.setTabOrder(self.chkBoxAutoSaveJobHistory, self.chkBoxRestoreWindowSize)
        QWidget.setTabOrder(self.chkBoxRestoreWindowSize, self.rbZero)
        QWidget.setTabOrder(self.rbZero, self.rbOne)
        QWidget.setTabOrder(self.rbOne, self.rbTwo)
        QWidget.setTabOrder(self.rbTwo, self.btnRestoreDefaults)

        self.retranslateUi(PreferencesDialog)
        self.btnBox.accepted.connect(PreferencesDialog.accept)
        self.btnBox.rejected.connect(PreferencesDialog.reject)

        QMetaObject.connectSlotsByName(PreferencesDialog)
    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QCoreApplication.translate("PreferencesDialog", u"Preferences", None))
        self.grpBox.setTitle("")
        self.lblInterfaceLanguage.setText(QCoreApplication.translate("PreferencesDialog", u"Interface Language:", None))
        self.chkBoxRestoreWindowSize.setText(QCoreApplication.translate("PreferencesDialog", u"Restore original window size", None))
        self.label.setText("")
        self.chkBoxEnableLogging.setText(QCoreApplication.translate("PreferencesDialog", u"Enable Logging", None))
        self.lblFontAndSize.setText(QCoreApplication.translate("PreferencesDialog", u"Font & Size:", None))
        self.chkBoxEnableJobHistory.setText(QCoreApplication.translate("PreferencesDialog", u"Enable jobs history", None))
        self.chkBoxEnableLogViewer.setText(QCoreApplication.translate("PreferencesDialog", u"Enable log viewer", None))
        self.chkBoxAutoSaveJobHistory.setText(QCoreApplication.translate("PreferencesDialog", u"Automatically save jobs", None))
        self.lblAlgorithm.setText(QCoreApplication.translate("PreferencesDialog", u"Algorithm:", None))
        self.rbZero.setText(QCoreApplication.translate("PreferencesDialog", u"0", None))
        self.rbOne.setText(QCoreApplication.translate("PreferencesDialog", u"1", None))
        self.rbTwo.setText(QCoreApplication.translate("PreferencesDialog", u"2", None))
        self.btnRestoreDefaults.setText(QCoreApplication.translate("PreferencesDialog", u"Restore Defaults", None))
    # retranslateUi

