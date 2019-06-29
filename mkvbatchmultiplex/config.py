"""
mkvbatchmultiplex config file
"""
#CF0005

import logging
import sys
from pathlib import Path

from vsutillib.files import ConfigurationSettings
from vsutillib.log import LogRotateFileHandler

data = ConfigurationSettings()  # pylint: disable=invalid-name

__VERSION = (1, 0, '1')

APPNAME = "MKVBatchMultiplex"
VERSION = ".".join(map(str, __VERSION))
URL = "https://github.com/akai10tsuki/mkvbatchmultiplex"
QT_VERSION = "PYSIDE2"

AUTHOR = "Efrain Vergara"
EMAIL = "akai10tsuki@gmail.com"

# for setup.py
DESCRIPTION = 'A mkv media batch multiplex.'
ENTRYPOINTS = {
    'console_scripts': [
        'mkvbatchmultiplex=mkvbatchmultiplex:mainApp',
    ],
}
KEYWORDS = 'mkv multimedia video'
NAME = "mkvbatchmultiplex"
PACKAGES = ['mkvbatchmultiplex']
PROJECTURLS = {
    'Bug Reports': 'https://github.com/akai10tsuki/mkvbatchmultiplex/issues',
    'Source': 'https://github.com/akai10tsuki/mkvbatchmultiplex/',
}
PYTHONVERSIONS = '>=3.5, <3.8'
REQUIRED = [
    'PySide2>=5.12', 'vsutillib.mkv>=1.0.2', 'vsutillib.media>=1.0.2',
    'vsutillib.macos>=1.0.2', 'vsutillib.files>=1.0.2', 'vsutillib.log>=1.0.1',
    'vsutillib.pyqt>=1.0.2'
]

# label
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

    loghandler = LogRotateFileHandler(logFile,
                                      backupCount=10,
                                      encoding='utf-8')

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s %(message)s")

    loghandler.setFormatter(formatter)

    logging.getLogger('').addHandler(loghandler)

    app = APPNAME + "-%s"

    logging.info("CF0001: App Start.")
    logging.info("CF0002: Python: %s", sys.version)
    app = "CF0003: " + app
    logging.info(app, VERSION)


def close():
    """exit accounting"""

    data.saveToFile()

    logging.info("CF0004: App End.")
