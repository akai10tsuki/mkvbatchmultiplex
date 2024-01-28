"""
class SetLanguage will collect setLanguage Slots
"""

from typing import Callable, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget


class Translate(QObject):
    """
    SetLanguage class to save and trigger multiple slots

    Args:
        QObject (QObject): base class in order to work with Signals
    """

    translateSignal = Signal((None, ), (str, ))

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.parent = parent
        self.translateSlots = []

    def addSlot(self, function: Callable[[str | None], None]) -> None:

        self.translateSignal.connect(function)
        self.translateSlots.append(function)

    def emitSignal(self, language: Optional[str] = None) -> None:

        if language is not None:
            self.translateSignal[str].emit(language)
        else:
            self.translateSignal.emit()
