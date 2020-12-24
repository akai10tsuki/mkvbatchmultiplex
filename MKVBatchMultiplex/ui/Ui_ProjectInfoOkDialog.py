# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ProjectInfoOkDialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ProjectInfoOkDialog(object):
    def setupUi(self, ProjectInfoOkDialog):
        if not ProjectInfoOkDialog.objectName():
            ProjectInfoOkDialog.setObjectName(u"ProjectInfoOkDialog")
        ProjectInfoOkDialog.resize(583, 394)
        font = QFont()
        font.setPointSize(14)
        ProjectInfoOkDialog.setFont(font)
        self.buttonBox = QDialogButtonBox(ProjectInfoOkDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(190, 350, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        self.lblName = QLabel(ProjectInfoOkDialog)
        self.lblName.setObjectName(u"lblName")
        self.lblName.setGeometry(QRect(31, 41, 511, 27))
        self.teDescription = QTextEdit(ProjectInfoOkDialog)
        self.teDescription.setObjectName(u"teDescription")
        self.teDescription.setGeometry(QRect(31, 134, 509, 186))
        self.lblDescription = QLabel(ProjectInfoOkDialog)
        self.lblDescription.setObjectName(u"lblDescription")
        self.lblDescription.setGeometry(QRect(31, 105, 511, 27))
        self.leName = QLineEdit(ProjectInfoOkDialog)
        self.leName.setObjectName(u"leName")
        self.leName.setGeometry(QRect(31, 70, 511, 29))
        QWidget.setTabOrder(self.leName, self.teDescription)

        self.retranslateUi(ProjectInfoOkDialog)
        self.buttonBox.accepted.connect(ProjectInfoOkDialog.accept)
        self.buttonBox.rejected.connect(ProjectInfoOkDialog.reject)

        QMetaObject.connectSlotsByName(ProjectInfoOkDialog)
    # setupUi

    def retranslateUi(self, ProjectInfoOkDialog):
        ProjectInfoOkDialog.setWindowTitle(QCoreApplication.translate("ProjectInfoOkDialog", u"Project Information", None))
        self.lblName.setText(QCoreApplication.translate("ProjectInfoOkDialog", u"Name", None))
        self.lblDescription.setText(QCoreApplication.translate("ProjectInfoOkDialog", u"Description", None))
        self.leName.setText("")
    # retranslateUi

