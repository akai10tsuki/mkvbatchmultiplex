"""
set language locale for main window menus
"""

from vsutillib.pyqt import QMenuWidget, QActionWidget


def setLanguageMenus(parent):
    """
    setLanguageMenus set language locale on menu items

    Args:
        menuActions (QMenu): item to transverse to set labels in correct locale
    """

    for action in parent.menuItems:
        if isinstance(action, (QActionWidget, QMenuWidget)):
            action.setLanguage()
