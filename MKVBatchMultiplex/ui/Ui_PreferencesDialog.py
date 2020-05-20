# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreferencesDialog.ui'
##
## Created by: Qt User Interface Compiler version 5.14.2
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
        PreferencesDialog.resize(674, 395)
        font = QFont()
        font.setPointSize(14)
        PreferencesDialog.setFont(font)
        PreferencesDialog.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.btnBox = QDialogButtonBox(PreferencesDialog)
        self.btnBox.setObjectName(u"btnBox")
        self.btnBox.setGeometry(QRect(60, 320, 531, 32))
        self.btnBox.setOrientation(Qt.Horizontal)
        self.btnBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok|QDialogButtonBox.RestoreDefaults)
        self.grpBox = QGroupBox(PreferencesDialog)
        self.grpBox.setObjectName(u"grpBox")
        self.grpBox.setGeometry(QRect(30, 40, 611, 241))
        self.layoutWidget = QWidget(self.grpBox)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(20, 42, 571, 165))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.lblInterfaceLanguage = QLabel(self.layoutWidget)
        self.lblInterfaceLanguage.setObjectName(u"lblInterfaceLanguage")

        self.gridLayout.addWidget(self.lblInterfaceLanguage, 0, 0, 1, 1)

        self.cmbBoxInterfaceLanguage = QComboBox(self.layoutWidget)
        self.cmbBoxInterfaceLanguage.setObjectName(u"cmbBoxInterfaceLanguage")

        self.gridLayout.addWidget(self.cmbBoxInterfaceLanguage, 0, 1, 1, 2)

        self.lblFontAndSize = QLabel(self.layoutWidget)
        self.lblFontAndSize.setObjectName(u"lblFontAndSize")

        self.gridLayout.addWidget(self.lblFontAndSize, 1, 0, 1, 1)

        self.fcmbBoxFontFamily = QFontComboBox(self.layoutWidget)
        self.fcmbBoxFontFamily.setObjectName(u"fcmbBoxFontFamily")

        self.gridLayout.addWidget(self.fcmbBoxFontFamily, 1, 1, 1, 1)

        self.spinBoxFontSize = QSpinBox(self.layoutWidget)
        self.spinBoxFontSize.setObjectName(u"spinBoxFontSize")

        self.gridLayout.addWidget(self.spinBoxFontSize, 1, 2, 1, 1)

        self.chkBoxEnableLogging = QCheckBox(self.layoutWidget)
        self.chkBoxEnableLogging.setObjectName(u"chkBoxEnableLogging")

        self.gridLayout.addWidget(self.chkBoxEnableLogging, 2, 0, 1, 1)

        self.chkBoxEnableJobHistory = QCheckBox(self.layoutWidget)
        self.chkBoxEnableJobHistory.setObjectName(u"chkBoxEnableJobHistory")

        self.gridLayout.addWidget(self.chkBoxEnableJobHistory, 3, 0, 1, 2)

        self.chkBoxRestoreWindowSize = QCheckBox(self.layoutWidget)
        self.chkBoxRestoreWindowSize.setObjectName(u"chkBoxRestoreWindowSize")

        self.gridLayout.addWidget(self.chkBoxRestoreWindowSize, 4, 0, 1, 2)


        self.retranslateUi(PreferencesDialog)
        self.btnBox.accepted.connect(PreferencesDialog.accept)
        self.btnBox.rejected.connect(PreferencesDialog.reject)

        QMetaObject.connectSlotsByName(PreferencesDialog)
    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QCoreApplication.translate("PreferencesDialog", u"Preferences", None))
        self.grpBox.setTitle(QCoreApplication.translate("PreferencesDialog", u"Options", None))
        self.lblInterfaceLanguage.setText(QCoreApplication.translate("PreferencesDialog", u"Interface Language:", None))
        self.lblFontAndSize.setText(QCoreApplication.translate("PreferencesDialog", u"Font & Size:", None))
        self.chkBoxEnableLogging.setText(QCoreApplication.translate("PreferencesDialog", u"Enable Logging", None))
        self.chkBoxEnableJobHistory.setText(QCoreApplication.translate("PreferencesDialog", u"Enable jobs history", None))
        self.chkBoxRestoreWindowSize.setText(QCoreApplication.translate("PreferencesDialog", u"Restore original window size", None))
    # retranslateUi

