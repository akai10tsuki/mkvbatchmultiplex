# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreferencesDialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        if not PreferencesDialog.objectName():
            PreferencesDialog.setObjectName(u"PreferencesDialog")
        PreferencesDialog.resize(744, 430)
        font = QFont()
        font.setPointSize(14)
        PreferencesDialog.setFont(font)
        PreferencesDialog.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.btnBox = QDialogButtonBox(PreferencesDialog)
        self.btnBox.setObjectName(u"btnBox")
        self.btnBox.setGeometry(QRect(460, 350, 241, 32))
        self.btnBox.setOrientation(Qt.Horizontal)
        self.btnBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.grpBox = QGroupBox(PreferencesDialog)
        self.grpBox.setObjectName(u"grpBox")
        self.grpBox.setGeometry(QRect(30, 40, 681, 281))
        self.lblInterfaceLanguage = QLabel(self.grpBox)
        self.lblInterfaceLanguage.setObjectName(u"lblInterfaceLanguage")
        self.lblInterfaceLanguage.setGeometry(QRect(21, 46, 172, 23))
        self.fcmbBoxFontFamily = QFontComboBox(self.grpBox)
        self.fcmbBoxFontFamily.setObjectName(u"fcmbBoxFontFamily")
        self.fcmbBoxFontFamily.setGeometry(QRect(221, 85, 371, 29))
        self.chkBoxRestoreWindowSize = QCheckBox(self.grpBox)
        self.chkBoxRestoreWindowSize.setObjectName(u"chkBoxRestoreWindowSize")
        self.chkBoxRestoreWindowSize.setGeometry(QRect(21, 235, 631, 27))
        self.label = QLabel(self.grpBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(203, 46, 16, 23))
        self.chkBoxEnableLogging = QCheckBox(self.grpBox)
        self.chkBoxEnableLogging.setObjectName(u"chkBoxEnableLogging")
        self.chkBoxEnableLogging.setGeometry(QRect(21, 124, 631, 27))
        self.lblFontAndSize = QLabel(self.grpBox)
        self.lblFontAndSize.setObjectName(u"lblFontAndSize")
        self.lblFontAndSize.setGeometry(QRect(21, 85, 171, 23))
        self.chkBoxEnableLogViewer = QCheckBox(self.grpBox)
        self.chkBoxEnableLogViewer.setObjectName(u"chkBoxEnableLogViewer")
        self.chkBoxEnableLogViewer.setGeometry(QRect(43, 161, 611, 27))
        self.chkBoxEnableLogViewer.setBaseSize(QSize(0, 0))
        self.cmbBoxInterfaceLanguage = QComboBox(self.grpBox)
        self.cmbBoxInterfaceLanguage.setObjectName(u"cmbBoxInterfaceLanguage")
        self.cmbBoxInterfaceLanguage.setGeometry(QRect(221, 46, 431, 29))
        self.spinBoxFontSize = QSpinBox(self.grpBox)
        self.spinBoxFontSize.setObjectName(u"spinBoxFontSize")
        self.spinBoxFontSize.setGeometry(QRect(599, 85, 51, 29))
        self.btnRestoreDefaults = QPushButton(PreferencesDialog)
        self.btnRestoreDefaults.setObjectName(u"btnRestoreDefaults")
        self.btnRestoreDefaults.setGeometry(QRect(50, 350, 351, 34))

        self.retranslateUi(PreferencesDialog)
        self.btnBox.accepted.connect(PreferencesDialog.accept)
        self.btnBox.rejected.connect(PreferencesDialog.reject)

        QMetaObject.connectSlotsByName(PreferencesDialog)
    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QCoreApplication.translate("PreferencesDialog", u"Preferences", None))
        self.grpBox.setTitle(QCoreApplication.translate("PreferencesDialog", u"Options", None))
        self.lblInterfaceLanguage.setText(QCoreApplication.translate("PreferencesDialog", u"Interface Language:", None))
        self.chkBoxRestoreWindowSize.setText(QCoreApplication.translate("PreferencesDialog", u"Restore original window size", None))
        self.label.setText("")
        self.chkBoxEnableLogging.setText(QCoreApplication.translate("PreferencesDialog", u"Enable Logging", None))
        self.lblFontAndSize.setText(QCoreApplication.translate("PreferencesDialog", u"Font & Size:", None))
        self.chkBoxEnableLogViewer.setText(QCoreApplication.translate("PreferencesDialog", u"Enable Log Viewer", None))
        self.btnRestoreDefaults.setText(QCoreApplication.translate("PreferencesDialog", u"Restore Defaults", None))
    # retranslateUi

