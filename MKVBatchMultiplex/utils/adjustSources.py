"""
adjustSources try and adjust tracks to account for structure difference
"""

import copy

from vsutillib.media import MediaFileInfo, MediaTrackInfo
from vsutillib.mkv import TracksOrder

from .. import config
from .findSimilarTrack import findSimilarTrack


def adjustSources(oCommand, index):
    """
    adjustSources scan tracks and adjust for structure difference

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

    for baseIndex, oBaseFile in enumerate(oCommand.oBaseFiles):
        baseFileInfo = oBaseFile.mediaFileInfo
        sourceFileInfo = MediaFileInfo(sourceFiles[baseIndex])
        trackOptions = oBaseFile.trackOptions
        translate = {}
        usedTrack = []
        savedScore = -1
        foundBadTrack = False

        for track in oBaseFile.trackOptions.tracks:
            i = int(track)
            if len(baseFileInfo) <= 0:
                # source file with no tracks
                return False
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
                #print(
                #    f"Index {baseIndex} baseTrack   {str(trackBase)}\n"
                #    f"Index {baseIndex} trackSource {str(trackSource)}\n"
                #)
                trackSimilar, score = findSimilarTrack(
                    oBaseFile, sourceFileInfo, trackBase, usedTrack
                )
                if trackSimilar >= 0:
                    #print(f"Score = {score}")
                    #print(
                    #    f"Index {baseIndex} baseTrack   {str(trackBase)}\n"
                    #    f"Index {baseIndex} trackSource {str(sourceFileInfo[trackSimilar])}\n"
                    #)
                    #print(f"Found track {trackSimilar} used tracks {usedTrack}")
                    if trackSimilar not in usedTrack:
                        usedTrack.append(trackSimilar)
                        translate[track] = str(trackSimilar)
                        #trackSource = sourceFileInfo[trackSimilar]
                        if savedScore > 0:
                            if score < savedScore:
                                savedScore = score
                        else:
                            savedScore = score
                    else:
                        print("Not suppose to show..")
                        if config.data.get(config.ConfigKey.Algorithm) == 2:
                            translate[track] = str(200 + i) # mkvmerge will ignore track
                        else:
                            translate = {}
                            break
                else:
                    if config.data.get(config.ConfigKey.Algorithm) == 2:
                        translate[track] = str(200 + i) # mkvmerge will ignore track
                    else:
                        translate = {}
                        break
            else:
                if track not in usedTrack:
                    usedTrack.append(i)

        if translate:
            if not rc:
                rc = True
            template = oCommand.commandTemplates[index]
            trackOpts = copy.deepcopy(trackOptions)
            trackOpts.translation = translate
            newTemplate = template.replace(trackOpts.options, trackOpts.strOptions(), 1)
            oCommand.commandTemplates[index] = newTemplate
            tracksOrderTranslation.update(trackOpts.orderTranslation)
            confidence = "High"
            if savedScore < 5:
                confidence = "Low"
            elif savedScore < 8:
                confidence = "Medium"

        if not foundBadTrack:
            # No needed tracks failed match.
            # Nothing to do go ahead with command.
            confidence = "High - Needed track(s) matched."
            rc = True

    if tracksOrderTranslation and oCommand.cliTracksOrder:
        tracksOrder.translation = tracksOrderTranslation
        oCommand.tracksOrder[index] = tracksOrder.strOrder()

    return rc, confidence
