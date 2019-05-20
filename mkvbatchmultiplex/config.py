"""
mkvbatchmultiplex config file
"""


import logging
import sys
from pathlib import Path

from vsutillib import ConfigurationSettings, LogRotateHandler

data = ConfigurationSettings() # pylint: disable=invalid-name

__VERSION = (0, 9, '1b1', 'dev1')

VERSION = ".".join(map(str, __VERSION))
AUTHOR = "Efrain Vergara"
EMAIL = "akai10tsuki@gmail.com"
URL = "https://github.com/akai10tsuki/mkvbatchmultiplex"
APPNAME = "MKVBatchMultiplex"
QT_VERSION = "PYSIDE2"

TOTALJOBS, CURRENTJOB, CURRENTFILE, TOTALFILES, TOTALERRORS = range(5)

# Files are relative to home directory
CONFIGFILE = "config.xml"
FILESROOT = ".MKVBatchMultiplex"
IMAGEFILESPATH = "images"
LOGFILE = "MKVBatchMultiplex.log"


def init():
    """Configure logging and configuration file"""

    filesPath = Path(Path.home(), FILESROOT)
    filesPath.mkdir(parents=True, exist_ok=True)

    configFile = Path(filesPath, CONFIGFILE)
    data.setConfigFile(configFile)
    data.readFromFile()

    logFile = Path(filesPath, LOGFILE)
    logging.getLogger('').setLevel(logging.DEBUG)

    loghandler = LogRotateHandler(logFile, backupCount=10)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s %(message)s"
    )

    loghandler.setFormatter(formatter)

    logging.getLogger('').addHandler(loghandler)

    app = APPNAME + "-%s"

    logging.info("App Start.")
    logging.info("Python: %s", sys.version)
    logging.info(app, VERSION)


def close():
    """exit accounting"""

    data.saveToFile()

    logging.info("App End.")
