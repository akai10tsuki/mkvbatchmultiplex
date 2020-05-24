# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SearchTextDialog.ui'
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


class Ui_SearchTextDialog(object):
    def setupUi(self, SearchTextDialog):
        if not SearchTextDialog.objectName():
            SearchTextDialog.setObjectName(u"SearchTextDialog")
        SearchTextDialog.resize(566, 283)
        font = QFont()
        font.setPointSize(14)
        SearchTextDialog.setFont(font)
        self.btnBox = QDialogButtonBox(SearchTextDialog)
        self.btnBox.setObjectName(u"btnBox")
        self.btnBox.setGeometry(QRect(330, 200, 181, 32))
        self.btnBox.setOrientation(Qt.Horizontal)
        self.btnBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.groupBox = QGroupBox(SearchTextDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(50, 50, 471, 131))
        self.widget = QWidget(self.groupBox)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(11, 41, 451, 64))
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.leSearchText = QLineEdit(self.widget)
        self.leSearchText.setObjectName(u"leSearchText")

        self.gridLayout.addWidget(self.leSearchText, 0, 1, 1, 1)

        self.lblResult = QLabel(self.widget)
        self.lblResult.setObjectName(u"lblResult")

        self.gridLayout.addWidget(self.lblResult, 1, 0, 1, 2)

        self.btnSearchText = QPushButton(SearchTextDialog)
        self.btnSearchText.setObjectName(u"btnSearchText")
        self.btnSearchText.setGeometry(QRect(60, 200, 81, 31))

        self.retranslateUi(SearchTextDialog)
        self.btnBox.accepted.connect(SearchTextDialog.accept)
        self.btnBox.rejected.connect(SearchTextDialog.reject)

        QMetaObject.connectSlotsByName(SearchTextDialog)
    # setupUi

    def retranslateUi(self, SearchTextDialog):
        SearchTextDialog.setWindowTitle(QCoreApplication.translate("SearchTextDialog", u"Search Text", None))
        self.groupBox.setTitle(QCoreApplication.translate("SearchTextDialog", u"Search", None))
        self.label.setText(QCoreApplication.translate("SearchTextDialog", u"Text to search:", None))
        self.lblResult.setText("")
        self.btnSearchText.setText(QCoreApplication.translate("SearchTextDialog", u"Search", None))
    # retranslateUi

