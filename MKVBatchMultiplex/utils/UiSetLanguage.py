
"""

UiSetLanguage

"""

from PySide2.QtCore import (
    QByteArray,
    QCoreApplication,
    QLibraryInfo,
    QLocale,
    QSize,
    QTranslator,
    Slot,
)

from .. import config

class UiSetLanguage:

    def __init__(self, parent):

        self.__errorFound = False

        libPath = QLibraryInfo.location(QLibraryInfo.TranslationsPath)

        #
        # English
        #
        self.enBaseTranslator = QTranslator(parent)
        self.enBaseTranslator.load("qtbase_en", libPath)
        self.enTranslator = QTranslator(parent)
        self.enTranslator.load("ui_en", str(config.LOCALE) + "/en/LC_MESSAGES")

        #
        # Español
        #
        self.esBaseTranslator = QTranslator(parent)
        self.esBaseTranslator.load("qtbase_es", libPath)
        self.esTranslator = QTranslator(parent)
        self.esTranslator.load("ui_es", str(config.LOCALE) + "/es/LC_MESSAGES")

        self.trLast = None
        self.trBaseLast = None
        self.loadedTranslations = []

    def setLanguage(self, language):

        self.__errorFound = False

        #
        # English
        #
        if language == 'en':
            self.removeTranslators()

            if QCoreApplication.installTranslator(self.enBaseTranslator):
                self.loadedTranslations.append(self.enBaseTranslator)
            else:
                self.__errorFound = True

            if QCoreApplication.installTranslator(self.enTranslator):
                self.loadedTranslations.append(self.enTranslator)
            else:
                self.__errorFound = True

        #
        # Español
        #
        if language == 'es':
            self.removeTranslators()

            if QCoreApplication.installTranslator(self.esBaseTranslator):
                self.loadedTranslations.append(self.esBaseTranslator)
            else:
                self.__errorFound = True

            if QCoreApplication.installTranslator(self.esTranslator):
                self.loadedTranslations.append(self.esTranslator)
            else:
                self.__errorFound = True

        return not self.__errorFound

    def removeTranslators(self):

        for translator in self.loadedTranslations:
            QCoreApplication.removeTranslator(translator)

        self.loadedTranslations = []
