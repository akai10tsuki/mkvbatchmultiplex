"""
class SetLanguage will collect setLanguage Slots
"""

from PySide2.QtCore import QObject, Signal

class SetLanguage(QObject):
    """
    SetLanguage class to save and trigger multiple slots

    Args:
        QObject (QObject): base class in order to work with Signals
    """

    setLanguageSignal = Signal()

    def __init__(self, parent=None):
        super(SetLanguage, self).__init__(parent)

        self.parent = parent
        self.languageSlots = []

    def addSlot(self, function):

        self.setLanguageSignal.connect(function)
        self.languageSlots.append(function)

    def emitSignal(self):

        self.setLanguageSignal.emit()
