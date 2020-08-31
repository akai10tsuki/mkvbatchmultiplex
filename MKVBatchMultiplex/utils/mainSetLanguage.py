"""
set language locale for main window menus
"""

from PySide2.QtWidgets import QAction

from vsutillib.pyqt import QMenuWidget, QActionWidget

from .. import config
from .text import Text

def setLanguageMenus(menuActions):
    """
    setLanguageMenus set language locale on menu items

    Args:
        menuActions (QMenu): item to transverse to set labels in correct locale
    """
    for m in menuActions:
        # menus on menu bar
        t = m.menu()

        if isinstance(t, QMenuWidget):
            t.setTitle(t.titlePrefix + _(t.originaltitle) + t.titleSuffix)

        for a in t.actions():
            if a.isSeparator():
                continue

            if isinstance(a, QActionWidget):
                if a.shortcut is not None:
                    a.setShortcut(_(a.shortcut))

                if a.tooltip is not None:
                    if a.tooltip == Text.txt0020:
                        msg = _(a.tooltip).format(
                            "~/" + config.FILESROOT + "/" + config.LOGFILE
                        )
                        a.setStatusTip(msg)
                    else:
                        a.setStatusTip(_(a.tooltip))

                if a.text is not None:
                    a.setText(a.textPrefix + _(a.originaltext) + a.textSuffix)

            elif isinstance(a, QMenuWidget):
                a.setTitle(_(a.originaltitle))

            elif isinstance(a, QAction):
                i = a.menu()

                if isinstance(t, QMenuWidget):
                    i.setTitle(_(i.originaltitle))
