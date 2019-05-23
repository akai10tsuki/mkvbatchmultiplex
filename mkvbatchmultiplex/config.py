"""
mkvbatchmultiplex config file
"""
#CF0005

import logging
import sys
from pathlib import Path


from vsutillib import ConfigurationSettings, LogRotateHandler


data = ConfigurationSettings() # pylint: disable=invalid-name

__VERSION = (0, 9, '1b1', 'dev1')

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
PYTHONVERSIONS = '>=3.5, <4'
REQUIRED = [
    'pymediainfo>=4.0',
    'PySide2>=5.12'
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

    loghandler = LogRotateHandler(logFile, backupCount=10)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s %(message)s"
    )

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
