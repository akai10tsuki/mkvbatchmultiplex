"""
mkvbatchmultiplex config file
"""
# CF0005

import logging
import os
import sys
from pathlib import Path

from PySide2.QtGui import QFont

from vsutillib.files import ConfigurationSettings
from vsutillib.log import LogRotateFileHandler
from vsutillib.pyqt import QSignalLogHandler

__VERSION = (2, 0, "1")

APPNAME = "MKVBatchMultiplex"
VERSION = ".".join(map(str, __VERSION))

AUTHOR = "Efrain Vergara"
EMAIL = "akai10tsuki@gmail.com"

# for setup.py
COPYRIGHT = "2018-2020, Efrain Vergara"
LICENSE = "MIT"
DESCRIPTION = "A mkv media batch multiplex."
ENTRYPOINTS = {
    "console_scripts": ["mkvbatchmultiplex=MKVBatchMultiplex:mainApp",],
}
KEYWORDS = "mkv multimedia video mkvtoolnix plex"
NAME = APPNAME.lower()
PACKAGES = [APPNAME]
URL = "https://github.com/akai10tsuki/mkvbatchmultiplex"
PROJECTURLS = {
    "Bug Reports": "https://github.com/akai10tsuki/mkvbatchmultiplex/issues",
    "Source": "https://github.com/akai10tsuki/mkvbatchmultiplex/",
}
PYTHONVERSIONS = ">=3.8.1, <3.9"
QT_VERSION = "PYSIDE2"
REQUIRED = [
    "PySide2>=5.14",
    "vsutillib-files>=1.6.0",
    "vsutillib-log>=1.6.0",
    "vsutillib-macos>=1.6.1",
    "vsutillib-media>=1.6.1",
    "vsutillib-mkv>=1.6.1",
    "vsutillib-process>=1.6.0",
    "vsutillib-pyqt>=1.6.1",
    "vsutillib-sql>=1.6.0",
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
logViewer = QSignalLogHandler()  # pylint: disable=invalid-name

FORCELOG = True

######################
# Application specific
######################

WORKERTHREADNAME = "jobsWorker"
SYSTEMDATABASE = "itsue.db"

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
    DefaultGeometry = "DefaultGeometry"
    Font = "Font"
    Geometry = "Geometry"
    InterfaceLanguages = "InterfaceLanguages"
    Language = "Language"
    Logging = "Logging"
    SimulateRun = "SimulateRun"
    SystemDB = "SystemDB"
    SystemFont = "SystemFont"

    #
    # App Specific
    #

    JobHistory = "JobHistory"
    JobsTable = "jobs"
    JobID = "JobID"
    LogViewer = "LogViewer"
    Tab = "Tab"
    TabText = "TabText"


class Key:

    RegEx = "RegEx"
    SubString = "SubString"
    MaxRegExCount = "MaxRegExCount"


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

    if data.get(ConfigKey.LogViewer) is None:
        data.set(ConfigKey.LogViewer, False)

    if data.get(ConfigKey.Language) is None:
        data.set(ConfigKey.Language, DEFAULTLANGUAGE)

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

    setInterfaceLanguage()
    setDefaultGeometry()

    db = Path(filesPath, SYSTEMDATABASE)
    data.set(ConfigKey.SystemDB, str(db))

    #
    # App Specific
    #
    setRegEx()

    if data.get(Key.MaxRegExCount) is None:
        data.set(Key.MaxRegExCount, 20)

    # Don't Release for now manually activated
    # <ConfigSetting id="JobHistory" type="bool">True</ConfigSetting>
    #if data.get(ConfigKey.JobHistory) is None:
    #    data.set(ConfigKey.JobHistory, False)
    #for key in data.configDictionary:
    #    print(f"Key {key}")


def setDefaultFont(app):
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


def setDefaultGeometry():

    if data.get(ConfigKey.DefaultGeometry) is None:
        data.set(ConfigKey.DefaultGeometry, (0, 0, 1280, 720))


def setInterfaceLanguage():

    if data.get(ConfigKey.InterfaceLanguages) is None:
        data.set(
            ConfigKey.InterfaceLanguages,
            {"en": "English (Inglés)", "es": "Español (Spanish)"},
        )


def setRegEx():
    """Update regex to 2.0.0a2"""

    oldRegEx = [
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+).*",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)(\W*-\W*)(?P<title>.*)",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)(\W*-\W*)(?P<title>.*?)((\W*\[.*|\W*\(.*))",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)(\w*|)(\W*-\W*)(?P<title>.*?)((\W*\[.*|\W*\(.*))",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)(\w*|)(\W*-|)(?P<title>.*).*",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*)(\d+).*",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+).*",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+)(\W*-\W*|\W*-|\W*|)(.*)",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+)(\W*-\W*|\W*-|\W*|)(.*?)(\W*[([].*)",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*)(?P<episode>\d+).*",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)(?P<episode>\d+).*",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)(?P<episode>\d+)(\W*-\W*|\W*-|\W*|)(?P<title>.*)",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)(?P<episode>\d+)(\W*-\W*|\W*-|\W*|)(?P<title>.*?)(\W*[([].*)",
    ]

    newRegEx = [
        r"([([].*?[])]\W*|)(.*?)(\W*-\W*)(\d+).*",
        r"([([].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+).*",
        r"([([].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+)(\W*-\W*|\W*-|\W*|)(.*)",
        r"([([].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+)(\W*-\W*|\W*-|\W*|)(.*?)(\W*[([].*)",
        r"([([].*?[])]\W*|)(?P<name>.*?)(\W*-\W*)(?P<episode>\d+).*",
        r"([([].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)(?P<episode>\d+).*",
        r"([([].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)(?P<episode>\d+)(\W*-\W*|\W*-|\W*|)(?P<title>.*)",
        r"([([].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)(?P<episode>\d+)(\W*-\W*|\W*-|\W*|)(?P<title>.*?)(\W*[([].*)",
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


def close():
    """exit accounting"""

    data.saveToFile()

    logging.info("CF0004: App End.")


def logTest(msg):
    print(msg)
