"""
set language locale for main window menus
"""

from vsutillib.pyqt import QMenuWidget, QActionWidget

from .. import config
from .text import Text


def setLanguageMenus(parent):
    """
    setLanguageMenus set language locale on menu items

    Args:
        menuActions (QMenu): item to transverse to set labels in correct locale
    """

    for action in parent.menuItems:
        if isinstance(action, QActionWidget):
            action.setText(
                action.textPrefix + _(action.originalText) + action.textSuffix
            )
            if action.statusTip:
                action.setStatusTip(_(action.statusTip))
            if action.toolTip:
                if action.toolTip == Text.txt0020:
                    msg = _(action.toolTip).format(
                        "~/" + config.FILESROOT + "/" + config.LOGFILE
                    )
                    action.setStatusTip(msg)
                else:
                    action.setStatusTip(_(action.toolTip))
        if isinstance(action, QMenuWidget):
            action.setTitle(
                action.titlePrefix + _(action.originalTitle) + action.titleSuffix
            )
