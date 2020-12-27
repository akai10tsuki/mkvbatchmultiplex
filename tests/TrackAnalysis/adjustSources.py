"""
adjustSources try and adjust tracks to account for structure difference
"""

import copy

from pathlib import PurePath

from vsutillib.media import MediaFileInfo, MediaTrackInfo
from vsutillib.mkv import TracksOrder

from findSimilarTrack import findSimilarTrack


def adjustSources(oCommand, index, algorithm=1):
    """
    adjustSources scan tracks and adjust for structure difference:

        - Algorithm = 0 should not call this.
        - Algorithm = 1 will try to find out of order tracks and if the tracks are
        found the order will be as in the base files.  Tracks have to be of same
        type and codec unless there is only one tracks of the required type. For
        example there is one audio in english and one file is aac and the other
        ac3 the the match will succeed.
        - Algorithm = 2 will always generate a file without regards of missing
        tracks. The results can be unplayable.

    Args:
        oCommand (MKVCommandParser): current commands for job
        index (int): command index

    Returns:
        bool: True if conflict resolved.  False otherwise.
    """

    rc = False

    tracksOrder = TracksOrder(oCommand.cliTracksOrder)
    tracksOrderTranslation = {}
    sourceFiles = oCommand.oSourceFiles[index]
    dummyTrack = MediaTrackInfo()
    confidence = "None"

    foundBadTrack = False
    unsolvedMismatch = False
    average = ScoreAverage()

    translationList = [None] * 3

    for baseIndex, oBaseFile in enumerate(oCommand.oBaseFiles):
        baseFileInfo = oBaseFile.mediaFileInfo
        sourceFileInfo = MediaFileInfo(sourceFiles[baseIndex])
        trackOptions = oBaseFile.trackOptions
        translate = {}
        usedTracks = []
        savedScore = -1

        for track in oBaseFile.trackOptions.tracks:
            i = int(track)
            if len(baseFileInfo) <= 0:
                # source file with no tracks
                suffix = PurePath(baseFileInfo.fileName).suffix  # pathlib.Path or str
                if suffix in (
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
                ):
                    # Hope this are the supported subs move to config.
                    continue
                else:
                    return False, "Low"
            trackBase = baseFileInfo[i]
            if i < len(sourceFileInfo):
                # source less tracks than base
                trackSource = sourceFileInfo[i]
            else:
                trackSource = dummyTrack
            # Testing
            if trackBase != trackSource:
                if not foundBadTrack:
                    foundBadTrack = True
                trackSimilar, score = findSimilarTrack(
                    oBaseFile, sourceFileInfo, trackBase, usedTracks, algorithm
                )
                if trackSimilar >= 0:
                    average.addUnits(1)
                    average.addPoints(score)
                    if trackSimilar not in usedTracks:
                        usedTracks.append(trackSimilar)
                        translate[track] = str(trackSimilar)
                        if savedScore > 0:
                            if score < savedScore:
                                savedScore = score
                        else:
                            savedScore = score
                    else:
                        print("Not suppose to show..")
                        if algorithm == 2:
                            translate[track] = str(
                                200 + i
                            )  # mkvmerge will ignore track
                        else:
                            translate = {}
                            break
                else:
                    if algorithm == 2:
                        translate[track] = str(200 + i)  # mkvmerge will ignore track
                    else:
                        if not unsolvedMismatch:
                            unsolvedMismatch = True
                        translate = {}
                        break
            else:
                if track not in usedTracks:
                    usedTracks.append(i)

        if translate:
            translationList[baseIndex] = copy.deepcopy(translate)
            if not rc:
                rc = True
            template = oCommand.commandTemplates[index]
            trackOpts = copy.deepcopy(trackOptions)
            trackOpts.translation = translate
            newTemplate = template.replace(trackOpts.options, trackOpts.strOptions(), 1)
            oCommand.commandTemplates[index] = newTemplate
            tracksOrderTranslation.update(trackOpts.orderTranslation)
            confidence = "High"
            if average.average() < 5:
                confidence = "Low"
            elif average.average() < 8:
                confidence = "Medium"


    # Save translations
    oCommand.translations[index] = translationList

    if not foundBadTrack:
        # No needed tracks failed match.
        # Nothing to do go ahead with command.
        confidence = "High - Needed track(s) matched."
        rc = True

    if tracksOrderTranslation and oCommand.cliTracksOrder:
        # update track order on oCommand for given index
        tracksOrder.translation = tracksOrderTranslation
        oCommand.tracksOrder[index] = tracksOrder.strOrder()

    return rc, confidence, average.average()


class ScoreAverage:
    """
    Avarage of units and points
    """

    def __init__(self):

        self.score = 0
        self.units = 0

    def addUnits(self, value):
        if isinstance(value, int):
            self.units += value

    def addPoints(self, value):
        if isinstance(value, int):
            self.score += value

    def average(self):
        if self.units > 0:
            return self.score / self.units
        else:
            return None
