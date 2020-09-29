# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ProjectInfoDialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ProjectInfoDialog(object):
    def setupUi(self, projectInfo):
        if not projectInfo.objectName():
            projectInfo.setObjectName(u"projectInfo")
        projectInfo.resize(583, 394)
        font = QFont()
        font.setPointSize(14)
        projectInfo.setFont(font)
        self.buttonBox = QDialogButtonBox(projectInfo)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(190, 350, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.lblName = QLabel(projectInfo)
        self.lblName.setObjectName(u"lblName")
        self.lblName.setGeometry(QRect(31, 41, 511, 27))
        self.teDescription = QTextEdit(projectInfo)
        self.teDescription.setObjectName(u"teDescription")
        self.teDescription.setGeometry(QRect(31, 134, 509, 186))
        self.lblDescription = QLabel(projectInfo)
        self.lblDescription.setObjectName(u"lblDescription")
        self.lblDescription.setGeometry(QRect(31, 105, 511, 27))
        self.leName = QLineEdit(projectInfo)
        self.leName.setObjectName(u"leName")
        self.leName.setGeometry(QRect(31, 70, 511, 29))

        self.retranslateUi(projectInfo)
        self.buttonBox.accepted.connect(projectInfo.accept)
        self.buttonBox.rejected.connect(projectInfo.reject)

        QMetaObject.connectSlotsByName(projectInfo)
    # setupUi

    def retranslateUi(self, projectInfo):
        projectInfo.setWindowTitle(QCoreApplication.translate("ProjectInfoDialog", u"Project Information", None))
        self.lblName.setText(QCoreApplication.translate("ProjectInfoDialog", u"Name", None))
        self.lblDescription.setText(QCoreApplication.translate("ProjectInfoDialog", u"Description", None))
        self.leName.setText("")
    # retranslateUi

