# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ProjectInfoDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QLineEdit, QSizePolicy, QTextEdit,
    QWidget)

class Ui_ProjectInfoDialog(object):
    def setupUi(self, ProjectInfoDialog):
        if not ProjectInfoDialog.objectName():
            ProjectInfoDialog.setObjectName(u"ProjectInfoDialog")
        ProjectInfoDialog.resize(583, 394)
        font = QFont()
        font.setPointSize(14)
        ProjectInfoDialog.setFont(font)
        self.buttonBox = QDialogButtonBox(ProjectInfoDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(190, 350, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.lblName = QLabel(ProjectInfoDialog)
        self.lblName.setObjectName(u"lblName")
        self.lblName.setGeometry(QRect(31, 41, 511, 27))
        self.teDescription = QTextEdit(ProjectInfoDialog)
        self.teDescription.setObjectName(u"teDescription")
        self.teDescription.setGeometry(QRect(31, 134, 509, 186))
        self.lblDescription = QLabel(ProjectInfoDialog)
        self.lblDescription.setObjectName(u"lblDescription")
        self.lblDescription.setGeometry(QRect(31, 105, 511, 27))
        self.leName = QLineEdit(ProjectInfoDialog)
        self.leName.setObjectName(u"leName")
        self.leName.setGeometry(QRect(31, 70, 511, 29))
        QWidget.setTabOrder(self.leName, self.teDescription)

        self.retranslateUi(ProjectInfoDialog)
        self.buttonBox.accepted.connect(ProjectInfoDialog.accept)
        self.buttonBox.rejected.connect(ProjectInfoDialog.reject)

        QMetaObject.connectSlotsByName(ProjectInfoDialog)
    # setupUi

    def retranslateUi(self, ProjectInfoDialog):
        ProjectInfoDialog.setWindowTitle(QCoreApplication.translate("ProjectInfoDialog", u"Project Information", None))
        self.lblName.setText(QCoreApplication.translate("ProjectInfoDialog", u"Name", None))
        self.lblDescription.setText(QCoreApplication.translate("ProjectInfoDialog", u"Description", None))
        self.leName.setText("")
    # retranslateUi

