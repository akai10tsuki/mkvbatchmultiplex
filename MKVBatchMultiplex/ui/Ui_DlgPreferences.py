# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DlgPreferences.ui'
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


class Ui_DlgPreferences(object):
    def setupUi(self, DlgPreferences):
        if not DlgPreferences.objectName():
            DlgPreferences.setObjectName(u"DlgPreferences")
        DlgPreferences.resize(654, 347)
        font = QFont()
        font.setPointSize(14)
        DlgPreferences.setFont(font)
        DlgPreferences.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.btnBox = QDialogButtonBox(DlgPreferences)
        self.btnBox.setObjectName(u"btnBox")
        self.btnBox.setGeometry(QRect(230, 280, 381, 32))
        self.btnBox.setOrientation(Qt.Horizontal)
        self.btnBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok|QDialogButtonBox.RestoreDefaults)
        self.grpBox = QGroupBox(DlgPreferences)
        self.grpBox.setObjectName(u"grpBox")
        self.grpBox.setGeometry(QRect(30, 40, 591, 201))
        self.widget = QWidget(self.grpBox)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(20, 41, 543, 132))
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.lblInterfaceLanguage = QLabel(self.widget)
        self.lblInterfaceLanguage.setObjectName(u"lblInterfaceLanguage")

        self.gridLayout.addWidget(self.lblInterfaceLanguage, 0, 0, 1, 1)

        self.cmbBoxInterfaceLanguage = QComboBox(self.widget)
        self.cmbBoxInterfaceLanguage.setObjectName(u"cmbBoxInterfaceLanguage")

        self.gridLayout.addWidget(self.cmbBoxInterfaceLanguage, 0, 1, 1, 2)

        self.lblFontAndSize = QLabel(self.widget)
        self.lblFontAndSize.setObjectName(u"lblFontAndSize")

        self.gridLayout.addWidget(self.lblFontAndSize, 1, 0, 1, 1)

        self.fcmbBoxFontFamily = QFontComboBox(self.widget)
        self.fcmbBoxFontFamily.setObjectName(u"fcmbBoxFontFamily")

        self.gridLayout.addWidget(self.fcmbBoxFontFamily, 1, 1, 1, 1)

        self.spinBoxFontSize = QSpinBox(self.widget)
        self.spinBoxFontSize.setObjectName(u"spinBoxFontSize")

        self.gridLayout.addWidget(self.spinBoxFontSize, 1, 2, 1, 1)

        self.chkBoxEnableLoging = QCheckBox(self.widget)
        self.chkBoxEnableLoging.setObjectName(u"chkBoxEnableLoging")

        self.gridLayout.addWidget(self.chkBoxEnableLoging, 2, 0, 1, 1)

        self.chkBoxRestoreWindowSize = QCheckBox(self.widget)
        self.chkBoxRestoreWindowSize.setObjectName(u"chkBoxRestoreWindowSize")

        self.gridLayout.addWidget(self.chkBoxRestoreWindowSize, 3, 0, 1, 2)


        self.retranslateUi(DlgPreferences)
        self.btnBox.accepted.connect(DlgPreferences.accept)
        self.btnBox.rejected.connect(DlgPreferences.reject)

        QMetaObject.connectSlotsByName(DlgPreferences)
    # setupUi

    def retranslateUi(self, DlgPreferences):
        DlgPreferences.setWindowTitle(QCoreApplication.translate("DlgPreferences", u"Preferences", None))
        self.grpBox.setTitle(QCoreApplication.translate("DlgPreferences", u"Options", None))
        self.lblInterfaceLanguage.setText(QCoreApplication.translate("DlgPreferences", u"Interface Language:", None))
        self.lblFontAndSize.setText(QCoreApplication.translate("DlgPreferences", u"Font & Size", None))
        self.chkBoxEnableLoging.setText(QCoreApplication.translate("DlgPreferences", u"Enable Logging", None))
        self.chkBoxRestoreWindowSize.setText(QCoreApplication.translate("DlgPreferences", u"Restore original window size", None))
    # retranslateUi

