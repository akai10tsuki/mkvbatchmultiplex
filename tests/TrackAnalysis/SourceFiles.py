"""

  SourceFile and SourceFiles classes

Raises:
    StopIteration: [description]
    IndexError: [description]
    StopIteration: [description]
    TypeError: [description]

Returns:
    [type]: [description]

"""

import re

from pathlib import Path

from natsort import natsorted, ns

#from vsutillib.media import MediaFileInfo
from vsutillib.mkv import unQuote

from MediaFileInfo import MediaFileInfo
from TrackOptions import TrackOptions


class SourceFile:
    """
     Tracks and file names
    """

    def __init__(self, fullMatchString=None, fileOrder=None):

        self.__fullMatchString = None
        self.__errorFound = False
        self.__fileOrder = None
        self.options = None
        self.filesInDir = []
        self.fileName = None
        self.mediaFileInfo = None
        self.matchString = None
        self.trackOptions = TrackOptions()

        # for iterator
        self.__index = 0

        self.fullMatchString = (fullMatchString, fileOrder)

    def __contains__(self, item):
        return item in self.filesInDir

    def __getitem__(self, index):
        return self.filesInDir[index]

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.filesInDir)

    def __next__(self):
        if self.__index >= len(self.filesInDir):
            self.__index = 0
            raise StopIteration
        else:
            self.__index += 1
            return self.__getitem__(self.__index - 1)

    def _parse(self):

        reTrackEx = re.compile(r"(?=--language )(.*?) (?=--language|'\(')")
        reOptionsEx = re.compile(
            (
                r"(?=--audio-tracks "
                r"|--video-tracks "
                r"|--subtitle-tracks "
                r"|--button-tracks "
                r"|--track-tags  "
                r"|--attachments "
                r"|--no-audio "
                r"|--no-video "
                r"|--no-subtitles "
                r"|--no-buttons "
                r"|--no-track-tags "
                r"|--no-chapters "
                r"|--no-attachments"
                r"|--no-global-tags "
                r"|--chapter-charset "
                r"|--chapter-language "
                r"|--language "
                r")(.*?) (?='\(')"
            )
        )
        # reTrackIDEx = re.compile(r"--language (\d+):(.*?)\W*")
        # reTrackNameEx = re.compile(r"--track-name (.*)( --|'|)")
        reSourcesEx = re.compile(r"'\('\s(.*?)\s'\)'")
        self.fileName = None

        if self.__fullMatchString:
            if match := reOptionsEx.search(self.__fullMatchString):
                self.options = match.group(1)
                self.trackOptions.options = self.options
                self.trackOptions.fileOrder = self.fileOrder
            else:
                self.__errorFound = True
            if match := reSourcesEx.search(self.__fullMatchString):
                f = unQuote(match.group(1))
                p = Path(f)

                try:
                    test = p.is_file()
                except OSError:
                    self.__errorFound = True
                else:
                    if test:
                        self.fileName = p
                        self.mediaFileInfo = MediaFileInfo(p)
                        self.matchString = match.group(0)
                        d = p.parent
                        fid = [x for x in d.glob("*" + p.suffix) if x.is_file()]
                        fid = natsorted(fid, alg=ns.PATH)
                        self.filesInDir.extend(fid)
                    else:
                        self.__errorFound = True
            else:
                self.__errorFound = True

    def __bool__(self):
        return not self.__errorFound

    @property
    def baseFile(self):
        return self.fileName

    @property
    def directory(self):
        return self.fileName.parent

    @property
    def fileOrder(self):
        return self.__fileOrder

    @property
    def fullMatchString(self):
        return self.__fullMatchString

    @fullMatchString.setter
    def fullMatchString(self, value):
        if isinstance(value, tuple):
            self.__fullMatchString = value[0]
            self.__fileOrder = value[1]
            self._parse()

class SourceFiles:
    """
     One sequence of SourceFile class elements
    """

    def __init__(self):

        self.__sourceFiles = []

        # for iterator
        self.__index = 0

    def __bool__(self):
        return bool(self.__sourceFiles)

    def __contains__(self, item):
        return item in self.__sourceFiles

    def __getitem__(self, index):
        """ __getitem__ from SourceFile is finally called"""

        if isinstance(index, (int, slice)):
            tmp = []
            for e in self.__sourceFiles:
                tmp.append(e[index])
            return tmp

        #if isinstance(index, tuple):
        #    print("Tuple " + str(index[0]))
        #    return self.__sourceFiles[index[0]]

        raise IndexError("Index " + str(index) + " invalid")

    def __iter__(self):
        return self

    def __len__(self):
        if self.__sourceFiles:
            return len(self.__sourceFiles[0]) # files read for first source
        return len(self.__sourceFiles)

    def __next__(self):
        if self.__index >= len(self.__sourceFiles[0]):
            self.__index = 0
            raise StopIteration
        else:
            self.__index += 1
            return self.__getitem__(self.__index - 1)

    def append(self, value):

        if isinstance(value, SourceFile):
            self.__sourceFiles.append(value)
        else:
            raise TypeError

    @property
    def sourceFiles(self):
        return self.__sourceFiles
