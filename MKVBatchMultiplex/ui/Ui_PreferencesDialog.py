# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreferencesDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QFontComboBox, QFrame,
    QGroupBox, QLabel, QPushButton, QRadioButton,
    QSizePolicy, QSpinBox, QWidget)

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        if not PreferencesDialog.objectName():
            PreferencesDialog.setObjectName(u"PreferencesDialog")
        PreferencesDialog.resize(744, 510)
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
        self.chkBoxRestoreWindowSize.setGeometry(QRect(20, 288, 641, 27))
        self.label = QLabel(self.grpBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(203, 46, 16, 23))
        self.chkBoxEnableLogging = QCheckBox(self.grpBox)
        self.chkBoxEnableLogging.setObjectName(u"chkBoxEnableLogging")
        self.chkBoxEnableLogging.setGeometry(QRect(21, 122, 641, 27))
        self.lblFontAndSize = QLabel(self.grpBox)
        self.lblFontAndSize.setObjectName(u"lblFontAndSize")
        self.lblFontAndSize.setGeometry(QRect(21, 82, 102, 23))
        self.cmbBoxInterfaceLanguage = QComboBox(self.grpBox)
        self.cmbBoxInterfaceLanguage.setObjectName(u"cmbBoxInterfaceLanguage")
        self.cmbBoxInterfaceLanguage.setGeometry(QRect(199, 42, 461, 29))
        self.spinBoxFontSize = QSpinBox(self.grpBox)
        self.spinBoxFontSize.setObjectName(u"spinBoxFontSize")
        self.spinBoxFontSize.setGeometry(QRect(590, 82, 71, 29))
        self.frame = QFrame(self.grpBox)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(10, 236, 621, 41))
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
        self.chkBoxComputeCRC = QCheckBox(self.grpBox)
        self.chkBoxComputeCRC.setObjectName(u"chkBoxComputeCRC")
        self.chkBoxComputeCRC.setGeometry(QRect(21, 198, 641, 27))
        self.chkBoxEnableLogViewer = QCheckBox(self.grpBox)
        self.chkBoxEnableLogViewer.setObjectName(u"chkBoxEnableLogViewer")
        self.chkBoxEnableLogViewer.setGeometry(QRect(45, 160, 611, 27))
        self.btnRestoreDefaults = QPushButton(PreferencesDialog)
        self.btnRestoreDefaults.setObjectName(u"btnRestoreDefaults")
        self.btnRestoreDefaults.setGeometry(QRect(30, 430, 351, 34))
        QWidget.setTabOrder(self.cmbBoxInterfaceLanguage, self.fcmbBoxFontFamily)
        QWidget.setTabOrder(self.fcmbBoxFontFamily, self.spinBoxFontSize)
        QWidget.setTabOrder(self.spinBoxFontSize, self.chkBoxEnableLogging)
        QWidget.setTabOrder(self.chkBoxEnableLogging, self.chkBoxRestoreWindowSize)
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
        self.lblAlgorithm.setText(QCoreApplication.translate("PreferencesDialog", u"Algorithm:", None))
        self.rbZero.setText(QCoreApplication.translate("PreferencesDialog", u"0", None))
        self.rbOne.setText(QCoreApplication.translate("PreferencesDialog", u"1", None))
        self.rbTwo.setText(QCoreApplication.translate("PreferencesDialog", u"2", None))
        self.chkBoxComputeCRC.setText(QCoreApplication.translate("PreferencesDialog", u"Append CRC to file name", None))
        self.chkBoxEnableLogViewer.setText(QCoreApplication.translate("PreferencesDialog", u"Enable log viewer", None))
        self.btnRestoreDefaults.setText(QCoreApplication.translate("PreferencesDialog", u"Restore Defaults", None))
    # retranslateUi

