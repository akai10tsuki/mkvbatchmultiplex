"""
Application configuration and version info
"""
# CFG0001

import logging
import os
import sys
from pathlib import Path


from vsutillib.files import ConfigurationSettings
from vsutillib.log import LogRotateFileHandler


__VERSION = (2, 0, "0a1")

VERSION = ".".join(map(str, __VERSION))

AUTHOR = "Efrain Vergara"
EMAIL = "akai10tsuki@gmail.com"

APPNAME = "MKVBatchMultiplex"
VERSION = ".".join(map(str, __VERSION))
URL = "https://github.com/akai10tsuki/" + APPNAME
NAME = APPNAME.lower()

# for setup.py
DESCRIPTION = "An MKV media batch multiplexer."
ENTRYPOINTS = {
    "console_scripts": [NAME + "=" + NAME + ":mainApp",],
}
KEYWORDS = "mkv multimedia video plex"
PACKAGES = [APPNAME]
PROJECTURLS = {
    "Bug Reports": "https://github.com/akai10tsuki/" + NAME + "/issues",
    "Source": "https://github.com/akai10tsuki/" + NAME + "/",
}
PYTHONVERSIONS = ">=3.8, <3.9"
REQUIRED = [
    "PySide2>=5.14",
    "vsutillib.mkv>=1.0.2",
    "vsutillib.media>=1.0.2",
    "vsutillib.macos>=1.0.2",
    "vsutillib.files>=1.0.2",
    "vsutillib.log>=1.0.1",
    "vsutillib.pyqt>=1.0.2",
]

# for app
__version__ = VERSION

FILESROOT = "." + APPNAME
LOGFILE = APPNAME + ".log"
IMAGESFILESPATH = ""
CONFIGFILE = "config.xml"
LOCALE = ""
DEFAULTLANGUAGE = "en"

if getattr(sys, "frozen", False):
    # Running in pyinstaller bundle
    CWD = Path(os.path.dirname(__file__)).parent
else:
    CWD = Path(os.path.realpath(__file__)).parent

LOCALE = CWD.joinpath("locale")

data = ConfigurationSettings()  # pylint: disable=invalid-name


class Action:

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
    """
    Configure log and read saved configuration
    """

    filesPath = Path(Path.home(), FILESROOT)
    filesPath.mkdir(parents=True, exist_ok=True)

    configFile = Path(filesPath, CONFIGFILE)
    data.setConfigFile(configFile)
    data.readFromFile()

    if data.get(ConfigKey.Language) is None:
        data.set(ConfigKey.Language, DEFAULTLANGUAGE)

    logFile = Path(filesPath, LOGFILE)
    logging.getLogger("").setLevel(logging.DEBUG)

    loghandler = LogRotateFileHandler(logFile, backupCount=10, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s %(message)s")

    loghandler.setFormatter(formatter)

    app = APPNAME + "-%s"

    logging.info("CF0001: App Start.")
    logging.info("CF0002: Python: %s", sys.version)
    app = "CF0003: " + app
    logging.info(app, VERSION)


def close():
    """End of activity"""

    data.saveToFile()  # save configuration

    logging.info("CFG0004: App End.")  # end of execution message to log
