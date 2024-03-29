
"""
UiSetLocale set the language to use in designer generated code
TODO: Maybe add to resource file
"""


from PySide6.QtCore import (
    QCoreApplication,
    QLibraryInfo,
    QTranslator,
)
from PySide6.QtWidgets import QWidget

from .. import config


class UiSetMessagesCatalog:
    """
    class to set the language for PySide2 ui dialogs
    """

    def __init__(self, parent: QWidget) -> None:

        self.__errorFound = False

        libPath = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)

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

    def setMessagesCatalog(self, language: str) -> bool:
        """
        setLanguage set the language locale

        Args:
            language (str): desired language for now ("en", "es")

        Returns:
            bool: True if everything is ok, False otherwise.
        """

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

    def removeTranslators(self) -> None:

        for translator in self.loadedTranslations:
            QCoreApplication.removeTranslator(translator)

        self.loadedTranslations = []
