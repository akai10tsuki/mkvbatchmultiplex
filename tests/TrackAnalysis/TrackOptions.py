"""
Track Options - get the tracks options as set in cli
"""

import re
import shlex

from MergeOptions import MergeOptions


class TrackOptions:
    """
     TrackOptions
    """

    def __init__(self, options=None):

        if options is not None:
            self.options = options

    def _initVars(self):

        self.__options = None
        self.__saOptions = []
        self.__sOptions = []
        self.__sdOptions = {}
        self.__sdTrackNames = {}
        self.__sTracks = []
        self.__translation = {}

    @property
    def sOptions(self):
        return self.__sOptions

    @property
    def saOptions(self):
        return self.__saOptions

    @property
    def options(self):
        return self.__options

    @options.setter
    def options(self, value):
        if isinstance(value, str):
            self._initVars()
            self.__options = value
            self._shlexSeparation()
            self._parse()

    @property
    def trackNames(self):
        return self.__sdTrackNames

    @property
    def tracks(self):
        return self.__sTracks

    @property
    def translation(self):
        return self.__translation

    @translation.setter
    def translation(self, value):
        self.__translation = value

    def optionsByTrack(self, track):

        strTmp = self.__sdOptions.get(track, None)
        return strTmp

    def strOptionsByTrack(self, track):
        """
        strOptionsByTrack recreate options with lookup in track substitution dictionary

        Args:
            track (str): track id

        Returns:
            str: option for track id
        """

        strTmp = ""
        aTmp = self.__sdOptions.get(track, None)
        for index, tTmp in enumerate(aTmp):
            track = self.translation.get(tTmp[1], tTmp[1])
            if index == len(aTmp) - 1:
                strTmp += tTmp[0] + " " + track + ":" + tTmp[2]
            else:
                strTmp += tTmp[0] + " " + track + ":" + tTmp[2] + " "

        return strTmp

    def strOptions(self):
        """
        strOptions track options reconstructed to take into account any substitution

        Returns:
            str: full options found on command line
        """

        strTmp = self._strOptions()
        for index, track in enumerate(self.tracks):
            if index == len(self.tracks) - 1:
                strTmp += self.strOptionsByTrack(track)
            else:
                strTmp += self.strOptionsByTrack(track) + " "

        return strTmp

    def _strOptions(self):

        mOptions = MergeOptions()

        strTmp = ""

        for tOption in self.__saOptions:
            opt = tOption[0]
            if opt in ("--video-tracks", "--audio-tracks", "--subtitle-tracks"):
                tracks = tOption[1].split(",")
                newTrks = []
                for trk in tracks:
                    trans = self.__translation.get(trk, trk)
                    newTrks.append(trans)
                newStr = ""
                for trk in newTrks:
                    if not newStr:
                        newStr += trk
                    else:
                        newStr += "," + trk
                if not strTmp:
                    strTmp += opt + " " + newStr
                else:
                    strTmp += " " + opt + " " + newStr

        if strTmp:
            strTmp += " "

        return strTmp

    def _shlexSeparation(self):

        shellOptions = shlex.split(self.__options)
        mOptions = MergeOptions()

        trackOptions = []

        for index, option in enumerate(shellOptions):
            if mOptions.isTrackOption(option):
                parameter = (
                    None
                    if not mOptions.hasParameter(option)
                    else shellOptions[index + 1]
                )
                trackOptions.append([option, index, parameter])

        currentTrack = ""

        reTrackID = re.compile(r"(\d+):(.*?)$")

        index = -1

        for opt in trackOptions:

            if mOptions.hasTrackID(opt[0]):
                if match := reTrackID.match(opt[2]):
                    if currentTrack != match.group(1):
                        currentTrack = match.group(1)
                        index += 1
                        self.__sOptions.append("")
                        self.__sOptions[index] += opt[0] + " " + opt[2]
                    else:
                        self.__sOptions[index] += " " + opt[0] + " " + opt[2]
            else:
                index += 1
                self.__sOptions.append("")
                if mOptions.hasParameter(opt[0]):
                    self.__sOptions[index] += opt[0] + " " + opt[2]
                else:
                    self.__sOptions[index] += opt[0]

    def _parse(self):

        mOptions = MergeOptions()

        for option in self.__sOptions:
            opt = option.split(" ")[0]
            if mOptions.hasTrackID(opt):
                reTrackOptionsEx = re.compile(r"(.*?) (\d+):(.*?) ")
                if match := reTrackOptionsEx.findall(option + " "):
                    for m in match:
                        self.__saOptions.append(m)
                        track = m[1]
                        if m[0] == "--track-name":
                            self.__sdTrackNames[track] = m[2]
                        if not track in self.__sdOptions.keys():
                            self.__sdOptions[track] = []
                            self.__sTracks.append(track)
                        self.__sdOptions[track].append(m)
            elif mOptions.hasParameter(opt):
                sOpt = option.split(" ")
                self.__saOptions.append((sOpt[0], sOpt[1], ""))
            else:
                self.__saOptions.append((sOpt[0], "", ""))
