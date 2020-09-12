"""
adjustSources try and adjust tracks to account for structure difference
"""

import copy

from vsutillib.media import MediaFileInfo, MediaTrackInfo
from vsutillib.mkv import TracksOrder

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
        savedScore = (-1)
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
            #print(
            #    f"Index {baseIndex} baseTrack   {str(trackBase)}\n"
            #    f"Index {baseIndex} trackSource {str(trackSource)}\n"
            #)
            if trackBase != trackSource:
                if not foundBadTrack:
                    foundBadTrack = True
                print("Adjust called find similar.")
                trackSimilar, score = findSimilarTrack(
                    oBaseFile,
                    sourceFileInfo,
                    trackBase
                )
                print(f"Score = {score}")
                if trackSimilar >= 0:
                    if trackSimilar not in usedTrack:
                        usedTrack.append(trackSimilar)
                        translate[track] = str(trackSimilar)
                        trackSource = sourceFileInfo[trackSimilar]
                        if savedScore > 0:
                            if score < savedScore:
                                savedScore = score
                        else:
                            savedScore = score
                    else:
                        translate = {}
                        break
                else:
                    translate = {}
                    break

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
            rc = True

    if tracksOrderTranslation:
        tracksOrder.translation = tracksOrderTranslation
        oCommand.tracksOrder[index] = tracksOrder.strOrder()

    return rc, confidence
