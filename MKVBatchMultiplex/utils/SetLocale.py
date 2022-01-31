"""
class SetLanguage will collect setLanguage Slots
"""

from typing import Callable, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget


class SetLocale(QObject):
    """
    SetLanguage class to save and trigger multiple slots

    Args:
        QObject (QObject): base class in order to work with Signals
    """

    setLanguageSignal = Signal((None, ), (str, ))

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.parent = parent
        self.languageSlots = []

    def addSlot(self, function: Callable[[str | None], None]) -> None:

        self.setLanguageSignal.connect(function)
        self.languageSlots.append(function)

    def emitSignal(self, language: Optional[str] = None) -> None:

        if language is not None:
            self.setLanguageSignal[str].emit(language)
        else:
            self.setLanguageSignal.emit()
