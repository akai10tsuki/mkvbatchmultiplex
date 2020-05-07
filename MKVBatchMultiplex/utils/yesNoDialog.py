"""
QMessageBox Yes/No dialog.
"""

from PySide2.QtWidgets import QMessageBox

from .text import Text


def yesNoDialog(parent, msg, title):
    """
    Convenience function to display a Yes/No dialog

    Returns:
        bool: return True if yes button press. No otherwise
    """

    m = QMessageBox(parent)
    m.setText(msg)
    m.setIcon(QMessageBox.Question)
    yesButton = m.addButton(_(Text.txt0082), QMessageBox.ButtonRole.YesRole)
    noButton = m.addButton(" No ", QMessageBox.ButtonRole.NoRole)
    m.setDefaultButton(noButton)
    m.setFont(parent.font())
    m.setWindowTitle(title)
    m.exec_()

    if m.clickedButton() == yesButton:
        return True

    return False
