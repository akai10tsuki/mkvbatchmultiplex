"""
mkvbatchmultiplex config file
"""
# CF0005

import logging
import os
import platform
import sys
from pathlib import Path

from PySide2.QtGui import QFont

from vsutillib.files import ConfigurationSettings
from vsutillib.log import LogRotateFileHandler

__VERSION = (2, 0, "0a1")

APPNAME = "MKVBatchMultiplex"
VERSION = ".".join(map(str, __VERSION))

AUTHOR = "Efrain Vergara"
EMAIL = "akai10tsuki@gmail.com"

# for setup.py
COPYRIGHT = "2018-2020, Efrain Vergara"
LICENSE = "MIT"
DESCRIPTION = "A mkv media batch multiplex."
ENTRYPOINTS = {
    "console_scripts": ["mkvbatchmultiplex=mkvbatchmultiplex:mainApp",],
}
KEYWORDS = "mkv multimedia video mkvtoolnix plex"
NAME = APPNAME.lower()
PACKAGES = [NAME]
URL = "https://github.com/akai10tsuki/mkvbatchmultiplex"
PROJECTURLS = {
    "Bug Reports": "https://github.com/akai10tsuki/mkvbatchmultiplex/issues",
    "Source": "https://github.com/akai10tsuki/mkvbatchmultiplex/",
}
PYTHONVERSIONS = ">=3.8.1, <3.9"
QT_VERSION = "PYSIDE2"
REQUIRED = [
    "PySide2>=5.14",
    "vsutillib.files>=1.5.0",
    "vsutillib.log>=1.5.0",
    "vsutillib.macos>=1.5.0",
    "vsutillib.media>=1.5.0",
    "vsutillib.misc>=1.5.0",
    "vsutillib.mkv>=1.5.0",
    "vsutillib.process>=1.5.0",
    "vsutillib.pyqt>=1.5.0",
]

# for app
__version__ = VERSION

# label

CONFIGFILE = "config.xml"
FILESROOT = "." + APPNAME
LOGFILE = APPNAME + ".log"
IMAGESFILESPATH = "images"
DEFAULTLANGUAGE = "en"

if getattr(sys, "frozen", False):
    # Running in pyinstaller bundle
    CWD = Path(os.path.dirname(__file__)).parent
else:
    CWD = Path(os.path.realpath(__file__)).parent
LOCALE = CWD.joinpath("locale")

data = ConfigurationSettings()  # pylint: disable=invalid-name
FORCELOG = True

######################
# Application specific
######################

WORKERTHREADNAME = "jobsWorker"

#######################
#######################


class Action:  # pylint: disable=too-few-public-methods

    Save = "Save"
    Reset = "Reset"
    Restore = "Restore"
    Update = "Update"


class ConfigKey:  # pylint: disable=too-few-public-methods
    """
    Keys for configuration elements all applications
    will have
    """

    DarkMode = "DarkMode"
    Font = "Font"
    Geometry = "Geometry"
    Language = "Language"
    Logging = "Logging"
    SimulateRun = "SimulateRun"
    SystemFont = "SystemFont"

    #
    # App Specific
    #

    Tab = "Tab"
    TabText = "TabText"


class Key:

    RegEx = "RegEx"
    SubString = "SubString"
    MaxCount = "MaxCount"


def init(filesRoot=None, cfgFile=None, logFile=None, name=None, version=None, app=None):
    """
    configures the system to save application configuration to xml file

    Args:
        filesRoot (str, optional): root folder on ~ for files. Defaults to [.vsutillib].
        configFile (str, optional): name of configuration file. Defaults to [config.xml].
        logFile (str, optional): name of logging file. Defaults to [vsutillib.log].
        name (str, optional): name of application. Defaults to [vsutillib].
        version (str, optional): appplication version . Defaults to [vsutillib version].
    """

    if filesRoot is None:
        filesPath = Path(Path.home(), FILESROOT)
    else:
        filesPath = Path(Path.home(), filesRoot)

    filesPath.mkdir(parents=True, exist_ok=True)

    if cfgFile is None:
        configFile = Path(filesPath, CONFIGFILE)
    else:
        configFile = Path(filesPath, configFile)

    data.setConfigFile(configFile)
    data.readFromFile()

    setDefaultFont(app)

    if FORCELOG:
        data.set(ConfigKey.Logging, True)

    if data.get(ConfigKey.Language) is None:
        data.set(ConfigKey.Language, DEFAULTLANGUAGE)

    if logFile is None:
        loggingFile = Path(filesPath, LOGFILE)
    else:
        loggingFile = Path(filesPath, logFile)

    loghandler = LogRotateFileHandler(loggingFile, backupCount=10, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s %(message)s")
    loghandler.setFormatter(formatter)
    logging.getLogger("").setLevel(logging.DEBUG)
    logging.getLogger("").addHandler(loghandler)

    if name is None:
        appName = APPNAME
    else:
        appName = name

    if version is None:
        appVersion = VERSION
    else:
        appVersion = version

    logging.info("CF0001: App Start.")
    logging.info("CF0002: Python: %s", sys.version)
    appName = "CF0003: " + appName
    logging.info("%s-%s", appName, appVersion)

    #
    # App Specific
    #
    if data.get(Key.RegEx) is None:
        data.set(
            Key.RegEx,
            [
                r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+).*",
                r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)(\W*-\W*)(?P<title>.*)",
                r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)(\W*-\W*)(?P<title>.*?)((\W*\[.*|\W*\(.*))",
            ],
        )

    if data.get(Key.SubString) is None:
        data.set(
            Key.SubString,
            [r"\g<name> - S01E\g<episode>", r"\g<name> - S01E\g<episode> - \g<title>",],
        )

    if data.get(Key.MaxCount) is None:
        data.set(Key.MaxCount, 10)

def setDefaultFont(app):
    """save and set default font point size"""

    strSystemFont = data.get(ConfigKey.SystemFont)
    if strSystemFont is None:
        systemFont = app.font()
        data.set(ConfigKey.SystemFont, systemFont.toString())
    else:
        systemFont = QFont()
        systemFont.fromString(strSystemFont)
    strFont = data.get(ConfigKey.Font)
    if strFont is None:
        font = systemFont
        font.setPointSize(14)
        data.set(ConfigKey.Font, font.toString())

def close():
    """exit accounting"""

    data.saveToFile()

    logging.info("CF0004: App End.")
