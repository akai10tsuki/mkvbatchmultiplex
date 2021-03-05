"""
mkvbatchmultiplex config file
"""
# CF0005

# for app
__VERSION__: tuple = (2, 1, "0b1", "dev5")
__version__: str = ".".join(map(str, __VERSION__))

import logging
import os
import sys

from typing import Callable, ClassVar, Dict, List, Optional
from pathlib import Path

from PySide2.QtGui import QFont
from PySide2.QtWidgets import QApplication

from vsutillib.files import ConfigurationSettings
from vsutillib.log import LogRotateFileHandler
from vsutillib.pyqt import QSignalLogHandler


APPNAME: str = "MKVBatchMultiplex"
VERSION: str = ".".join(map(str, __VERSION__))

AUTHOR: str = "Efrain Vergara"
EMAIL: str = "akai10tsuki@gmail.com"

# for setup.py
COPYRIGHT: str = "2018-2021, Efrain Vergara"
LICENSE: str = "MIT"
DESCRIPTION: str = "A mkv media batch multiplex."
ENTRYPOINTS: Dict[str, List[str]] = {
    "console_scripts": [
        "mkvbatchmultiplex=MKVBatchMultiplex:mainApp",
    ],
}
KEYWORDS: str = "mkv multimedia video mkvtoolnix plex"
NAME: str = APPNAME.lower()
PACKAGES: str = [APPNAME]
URL: str = "https://github.com/akai10tsuki/mkvbatchmultiplex"
PROJECTURLS: Dict[str, str] = {
    "Bug Reports": "https://github.com/akai10tsuki/mkvbatchmultiplex/issues",
    "Source": "https://github.com/akai10tsuki/mkvbatchmultiplex/",
}
PYTHONVERSIONS: str = ">=3.8.1, <4.0"
QT_VERSION: str = "PYSIDE2"
PYSIDE2_VERSION: str = ">=5.15.2"
PYSIDE6_VERSION: str = ">=6.0.0"
REQUIRED: List[str] = [
    "PySide2>=5.15",
    "vsutillib-files>=1.6.5",
    "vsutillib-log>=1.6.0",
    "vsutillib-media>=1.6.5",
    "vsutillib-mkv>=1.6.5",
    "vsutillib-process>=1.6.5",
    "vsutillib-pyqt>=1.6.2",
    "vsutillib-sql>=1.6.5",
]

# REQUIRED = [
#    "vsutillib-macos>=1.6.1", # pulls process
# ]


# label

CONFIGFILE: str = "config.xml"
FILESROOT: str = "." + APPNAME
LOGFILE: str = APPNAME + ".log"
IMAGESFILESPATH: str = "images"
DEFAULTLANGUAGE: str = "en"

if getattr(sys, "frozen", False):
    # Running in pyinstaller bundle
    CWD: Path = Path(os.path.dirname(__file__)).parent
else:
    CWD: Path = Path(os.path.realpath(__file__)).parent
LOCALE: str = CWD.joinpath("locale")

data: Callable[
    [], ConfigurationSettings
] = ConfigurationSettings()  # pylint: disable=invalid-name
logViewer: Callable[
    [], QSignalLogHandler
] = QSignalLogHandler()  # pylint: disable=invalid-name

FORCELOG: bool = True

######################
# Application specific
######################

WORKERTHREADNAME: str = "jobsWorker"
SYSTEMDATABASE: str = "itsue.db"
ALGORITHMDEFAULT: int = 1
DATABASEVERSION: str = "2.1.0"

#######################
#######################


class Action:  # pylint: disable=too-few-public-methods

    Save: ClassVar[str] = "Save"
    Reset: ClassVar[str] = "Reset"
    Restore: ClassVar[str] = "Restore"
    Update: ClassVar[str] = "Update"


class ConfigKey:  # pylint: disable=too-few-public-methods
    """
    Keys for configuration elements all applications
    will have
    """

    DarkMode: ClassVar[str] = "DarkMode"
    DefaultGeometry: ClassVar[str] = "DefaultGeometry"
    Font: ClassVar[str] = "Font"
    Geometry: ClassVar[str] = "Geometry"
    InterfaceLanguages: ClassVar[str] = "InterfaceLanguages"
    Language: ClassVar[str] = "Language"
    Logging: ClassVar[str] = "Logging"
    SimulateRun: ClassVar[str] = "SimulateRun"
    SystemDB: ClassVar[str] = "SystemDB"
    SystemFont: ClassVar[str] = "SystemFont"

    #
    # App Specific
    #

    Algorithm: ClassVar[str] = "Algorithm"
    DbVersion: ClassVar[str] = "DbVersion"
    JobsAutoSave: ClassVar[str] = "JobsAutoSave"
    JobHistory: ClassVar[str] = "JobHistory"
    JobHistoryDisabled: ClassVar[str] = "JobsHistoryDisabled"
    JobID: ClassVar[str] = "JobID"
    JobsTable: ClassVar[str] = "jobs"
    LogViewer: ClassVar[str] = "LogViewer"
    Tab: ClassVar[str] = "Tab"
    TabText: ClassVar[str] = "TabText"
    TextSuffix: ClassVar[str] = "TextSuffix"


class Key:

    RegEx: ClassVar[str] = "RegEx"
    SubString: ClassVar[str] = "SubString"
    MaxRegExCount: ClassVar[str] = "MaxRegExCount"


def init(
    filesRoot: Optional[str] = None,
    cfgFile: Optional[str] = None,
    logFile: Optional[str] = None,
    name: Optional[str] = None,
    version: Optional[str] = None,
    app: Optional[str] = None,
):
    """
    configures the system to save application configuration to xml file

    Args:
        **filesRoot** (str, optional): root folder on ~ for files. Defaults to [.vsutillib].

        **configFile** (str, optional): name of configuration file. Defaults to [config.xml].

        **logFile** (str, optional): name of logging file. Defaults to [vsutillib.log].

        **name** (str, optional): name of application. Defaults to [vsutillib].

        **version** (str, optional): appplication version . Defaults to [vsutillib version].
    """

    if filesRoot is None:
        # root path for configuration files
        filesPath = Path(Path.home(), FILESROOT)
    else:
        filesPath = Path(Path.home(), filesRoot)

    filesPath.mkdir(parents=True, exist_ok=True)

    if cfgFile is None:
        # setup main configuration file
        configFile = Path(filesPath, CONFIGFILE)
    else:
        configFile = Path(filesPath, cfgFile)

    data.setConfigFile(configFile)
    data.readFromFile()

    setDefaultFont(app)

    #
    # Setup logging
    #
    if FORCELOG:
        data.set(ConfigKey.Logging, True)

    data.set(ConfigKey.LogViewer, data.get(ConfigKey.LogViewer) or False)

    data.set(ConfigKey.Language, data.get(ConfigKey.Language) or DEFAULTLANGUAGE)

    if logFile is None:
        loggingFile = Path(filesPath, LOGFILE)
    else:
        loggingFile = Path(filesPath, logFile)

    loghandler = LogRotateFileHandler(loggingFile, backupCount=10, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s %(message)s")
    loghandler.setFormatter(formatter)
    logViewer.setFormatter(formatter)
    logging.getLogger("").addHandler(loghandler)
    logging.getLogger("").addHandler(logViewer)
    logging.getLogger("").setLevel(logging.DEBUG)

    appName = name or APPNAME
    appVersion = version or VERSION

    logging.info("CF0001: App Start.")
    logging.info("CF0002: Python: %s", sys.version)
    appName = "CF0003: " + appName
    logging.info("%s-%s", appName, appVersion)

    setInterfaceLanguage()
    setDefaultGeometry()

    db = Path(filesPath, SYSTEMDATABASE)
    data.set(ConfigKey.SystemDB, str(db))

    #
    # App Specific
    #
    setRegEx()

    data.set(ConfigKey.Algorithm, data.get(ConfigKey.Algorithm) or 1)

    data.set(ConfigKey.DbVersion, data.get(ConfigKey.DbVersion) or DATABASEVERSION)

    data.set(ConfigKey.JobsAutoSave, data.get(ConfigKey.JobsAutoSave) or False)

    data.set(ConfigKey.JobHistory, data.get(ConfigKey.JobHistory) or False)

    data.set(
        ConfigKey.JobHistoryDisabled, data.get(ConfigKey.JobHistoryDisabled) or False
    )
    # data.set(ConfigKey.JobHistoryDisabled, False)

    data.set(Key.MaxRegExCount, data.get(Key.MaxRegExCount) or 20)

    data.set(
        ConfigKey.TextSuffix,
        data.get(ConfigKey.TextSuffix)
        or (
            ".srt",
            ".ssa",
            ".ass",
            ".pgs",
            ".idx",
            ".vob",
            ".vtt",
            ".usf",
            ".dvb",
            ".smi",
        ),
    )

    #
    # Temporalily disable uncomment statements
    #
    # data.set(ConfigKey.JobHistoryDisabled, True)
    # data.set(ConfigKey.JobHistory, False)


def setDefaultFont(app: QApplication) -> None:
    """save and set default font point size"""

    strSystemFont = data.get(ConfigKey.SystemFont)
    if strSystemFont is None:
        systemFont = app.font()
        systemFont.setPointSize(14)
        data.set(ConfigKey.SystemFont, systemFont.toString())
    else:
        systemFont = QFont()
        systemFont.fromString(strSystemFont)
    strFont = data.get(ConfigKey.Font)
    if strFont is None:
        font = systemFont
        font.setPointSize(14)
        data.set(ConfigKey.Font, font.toString())


def setDefaultGeometry() -> None:

    data.set(
        ConfigKey.DefaultGeometry,
        data.get(ConfigKey.DefaultGeometry) or (0, 0, 1280, 720),
    )


def setInterfaceLanguage() -> None:

    data.set(
        ConfigKey.InterfaceLanguages,
        data.get(ConfigKey.InterfaceLanguages)
        or {"en": "English (Inglés)", "es": "Español (Spanish)"},
    )


def setRegEx() -> None:
    """Update regex to 2.0.0a2"""

    oldRegEx = [
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+).*",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)(\W*-\W*)(?P<title>.*)",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)"
        r"(\W*-\W*)(?P<title>.*?)((\W*\[.*|\W*\(.*))",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)"
        r"(\w*|)(\W*-\W*)(?P<title>.*?)((\W*\[.*|\W*\(.*))",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)(\w*|)(\W*-|)(?P<title>.*).*",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*)(\d+).*",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+).*",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+)(\W*-\W*|\W*-|\W*|)(.*)",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+)(\W*-\W*|\W*-|\W*|)(.*?)(\W*[([].*)",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*)(?P<episode>\d+).*",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)(?P<episode>\d+).*",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)"
        r"(?P<episode>\d+)(\W*-\W*|\W*-|\W*|)(?P<title>.*)",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)"
        r"(?P<episode>\d+)(\W*-\W*|\W*-|\W*|)(?P<title>.*?)(\W*[([].*)",
    ]

    newRegEx = [
        r"([([].*?[])]\W*|)(.*?)(\W*-\W*)(\d+).*",
        r"([([].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+).*",
        r"([([].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+)(\W*-\W*|\W*-|\W*|)(.*)",
        r"([([].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+)(\W*-\W*|\W*-|\W*|)(.*?)(\W*[([].*)",
        r"([([].*?[])]\W*|)(?P<name>.*?)(\W*-\W*)(?P<episode>\d+).*",
        r"([([].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)(?P<episode>\d+).*",
        r"([([].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)"
        r"(?P<episode>\d+)(\W*-\W*|\W*-|\W*|)(?P<title>.*)",
        r"([([].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)"
        r"(?P<episode>\d+)(\W*-\W*|\W*-|\W*|)(?P<title>.*?)(\W*[([].*)",
    ]

    newSubString = [
        r"\2 - S01E\4",
        r"\2 - S01E\4 - \6",
        r"\g<name> - S01E\g<episode>",
        r"\g<name> - S01E\g<episode> - \g<title>",
    ]

    if data.get(Key.RegEx) is None:
        data.set(Key.RegEx, newRegEx)
    else:
        currentRegEx = data.get(Key.RegEx)
        for e in oldRegEx:
            try:
                currentRegEx.remove(e)
            except:  # pylint: disable=bare-except
                pass
        for e in newRegEx:
            if e not in currentRegEx:
                currentRegEx.append(e)
        data.set(Key.RegEx, currentRegEx)

    if data.get(Key.SubString) is None:
        data.set(Key.SubString, newSubString)
    else:
        currentSubString = data.get(Key.SubString)
        for e in currentSubString:
            if e not in currentSubString:
                currentSubString.append(e)
        data.set(Key.SubString, currentSubString)

    if data.get("MaxCount"):
        data.delete("MaxCount")
    data.set(Key.MaxRegExCount, 20)


def close() -> None:
    """exit accounting"""

    data.saveToFile()
    logging.info("CF0004: App End.")


def logTest(msg: str) -> None:
    print(msg)
