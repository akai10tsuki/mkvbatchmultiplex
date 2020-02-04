"""
mkvbatchmultiplex config file
"""
# CF0005

import logging
import os
import sys
from pathlib import Path

from vsutillib.files import ConfigurationSettings
from vsutillib.log import LogRotateFileHandler

__VERSION = (2, 0, "0a1")

APPNAME = "MKVBatchMultiplex"
VERSION = ".".join(map(str, __VERSION))
URL = "https://github.com/akai10tsuki/mkvbatchmultiplex"
QT_VERSION = "PYSIDE2"

AUTHOR = "Efrain Vergara"
EMAIL = "akai10tsuki@gmail.com"

# for setup.py
DESCRIPTION = "A mkv media batch multiplex."
ENTRYPOINTS = {
    "console_scripts": ["mkvbatchmultiplex=mkvbatchmultiplex:mainApp",],
}
KEYWORDS = "mkv multimedia video"
NAME = APPNAME.lower()
PACKAGES = ["mkvbatchmultiplex"]
PROJECTURLS = {
    "Bug Reports": "https://github.com/akai10tsuki/mkvbatchmultiplex/issues",
    "Source": "https://github.com/akai10tsuki/mkvbatchmultiplex/",
}
PYTHONVERSIONS = ">=3.8, <3.9"
REQUIRED = [
    "PySide2>=5.12",
    "vsutillib.mkv>=1.0.2",
    "vsutillib.media>=1.0.2",
    "vsutillib.macos>=1.0.2",
    "vsutillib.files>=1.0.2",
    "vsutillib.log>=1.0.1",
    "vsutillib.pyqt>=1.0.2",
]

# for app
__version__ = VERSION

# label
#TOTALJOBS, CURRENTJOB, CURRENTFILE, TOTALFILES, TOTALERRORS = range(5)

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

JOBID, JOBSTATUS, JOBCOMMAND = range(3)

BTNADDCOMMAND = 0

BTNPASTE = 0
BTNADDQUEUE = 1
BTNSTARTQUEUE = 2

BTNANALYSIS = 4
BTNSHOWCOMMANDS = 5
BTNCHECKFILES = 6

BTNCLEAR = 8
BTNRESET = 9

WORKERTHREADNAME = "jobsWorker"

JTVBTNCLEARQUEUE = 3
JTVBTNSTARTQUEUE = 4

SIMULATERUN = True

#######################
#######################

class Action: # pylint: disable=too-few-public-methods

    Save = "Save"
    Reset = "Reset"
    Restore = "Restore"
    Update = "Update"


class ConfigKey:  # pylint: disable=too-few-public-methods
    """
    Keys for configuration elements all applications
    will have
    """

    Language = "Language"
    Font = "Font"
    Logging = "Logging"
    Geometry = "Geometry"


def init():
    """Configure logging and configuration file"""

    filesPath = Path(Path.home(), FILESROOT)
    filesPath.mkdir(parents=True, exist_ok=True)

    configFile = Path(filesPath, CONFIGFILE)
    data.setConfigFile(configFile)
    data.readFromFile()

    if FORCELOG:
        data.set(ConfigKey.Logging, True)

    if data.get(ConfigKey.Language) is None:
        data.set(ConfigKey.Language, DEFAULTLANGUAGE)

    logFile = Path(filesPath, LOGFILE)
    logging.getLogger("").setLevel(logging.DEBUG)

    loghandler = LogRotateFileHandler(logFile, backupCount=10, encoding="utf-8")

    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s %(message)s")

    loghandler.setFormatter(formatter)

    logging.getLogger("").addHandler(loghandler)

    app = APPNAME + "-%s"

    logging.info("CF0001: App Start.")
    logging.info("CF0002: Python: %s", sys.version)
    app = "CF0003: " + app
    logging.info(app, VERSION)


def close():
    """exit accounting"""

    data.saveToFile()

    logging.info("CF0004: App End.")
