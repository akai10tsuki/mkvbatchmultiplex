"""
set language locale for main window menus
"""

from typing import List

from PySide6.QtWidgets import QWidget

from vsutillib.pyside6 import QMenuWidget, QActionWidget


def setLocale(widgets: List[QWidget]):
    """
    setLocale set language locale on menu items QActionWidget and
    QMenuItemWidget

    Args:
        widgets (QWidget): widgets items must have a setLanguage method
    """

    for action in widgets:
        if isinstance(action, (QActionWidget, QMenuWidget)):
            setLanguage = getattr(action, "setLanguage", None)
            if callable(setLanguage):
                action.setLanguage()
