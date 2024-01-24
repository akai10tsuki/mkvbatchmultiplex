"""
Configure language for localee
"""

import gettext

from typing import Optional

from PySide6.QtWidgets import QMainWindow

from .. import config

def configMessagesCatalog(app: QMainWindow, language: Optional[str] = None) -> None:
    """
    Set application language the scheme permits runtime changes
    """

    if language is None:
        language = config.data.get(config.ConfigKey.Language)

    lang = gettext.translation(
        config.NAME, localedir=str(config.LOCALE), languages=[language]
    )
    if app.uiTranslateInterface.setMessagesCatalog(language):
        pass
    lang.install(names=("ngettext",))
    config.data.set(config.ConfigKey.Language, language)
