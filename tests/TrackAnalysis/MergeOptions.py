"""Identify mkvmerge options"""


class MergeOptions:
    """
     mkvmerge supported global and track options
    """

    globalOptions = {
        "--verbose": [False, False],
        "--quiet": [False, False],
        "--output": [True, False],
        "--webm": [False, False],
        "--title": [True, False],
        "--default-language": [True, False],
    }

    tackOptions = {
        "--no-audio": [False, False],
        "--no-video": [False, False],
        "--no-subtitles": [False, False],
        "--no-buttons": [False, False],
        "--no-track-tags": [False, False],
        "--no-chapters": [False, False],
        "--no-attachments": [False, False],
        "--no-global-tags": [False, False],
        "--audio-tracks": [True, False],
        "--video-tracks": [True, False],
        "--subtitle-tracks": [True, False],
        "--button-tracks": [True, False],
        "--track-tags": [True, False],
        "--attachments": [True, False],
        "--chapter-charset": [True, False],
        "--chapter-language": [True, False],
        "--sync": [True, True],
        "--cues": [True, True],
        "--default-track": [True, True],
        "--force-track": [True, True],
        "--blockadd": [True, True],
        "--track-name": [True, True],
        "--language": [True, True],
        "--tags": [True, True],
        "--aac-is-sbr": [True, True],
        "--reduce-to-core": [True, True],
        "--remove-dialog-normalization-gain": [True, True],
        "--timestamps": [True, True],
        "--default-duration": [True, True],
        "--fix-bitstream-timing-information": [True, True],
        "--nalu-size-length": [True, True],
        "--compression": [True, True],
        "--fourcc": [True, True],
        "--display-dimensions": [True, True],
        "--aspect-ratio": [True, True],
        "--aspect-ratio-factor": [True, True],
        "--cropping": [True, True],
        "--color-matrix": [True, True],
        "--colour-bits-per-channel": [True, True],
        "--chroma-subsample": [True, True],
        "--cb-subsample": [True, True],
        "--chroma-siting": [True, True],
        "--colour-range": [True, True],
        "--colour-transfer-characteristics": [True, True],
        "--max-content-light": [True, True],
        "--max-frame-light": [True, True],
        "--chromaticity-coordinates": [True, True],
        "--white-colour-coordinates": [True, True],
        "--max-luminance": [True, True],
        "--min-luminance": [True, True],
        "--projection-type": [True, True],
        "--projection-private": [True, True],
        "--projection-pose-yaw": [True, True],
        "--projection-pose-pitch": [True, True],
        "--projection-pose-roll": [True, True],
        "--field-order": [True, True],
        "--stereo-mode": [True, True],
        "--sub-charset": [True, True],
    }

    def __init__(self):

        pass

    @staticmethod
    def hasParameter(option):
        """
        hasParameter determines if mkvmerge option has a parameter

        Args:
            option (str): mkvmerge option

        Returns:
            bool|None: returns True if option has parameter False if no.  Returns
                None if option not supported
        """

        rc = MergeOptions.globalOptions.get(option)

        if rc:
            return rc[0]

        rc = MergeOptions.tackOptions.get(option)

        if rc:
            return rc[0]

        return None

    @staticmethod
    def hasTrackID(option):
        """
        hasTrackID determines if mkvmerge option has a track ID in parameter

        Args:
            option (str): mkvmerge option

        Returns:
            bool|None: returns True if option has track False if no.  Returns
                None if option not supported
        """

        rc = MergeOptions.globalOptions.get(option)

        if rc:
            return rc[1]

        rc = MergeOptions.tackOptions.get(option)

        if rc:
            return rc[1]

        return None

    @staticmethod
    def isTrackOption(option):
        """
        isTrackOptions determines if mkvmerge option is used for tracks

        Args:
            option (str): mkvmerge option

        Returns:
            bool|None: returns True if option is used for tracks False if no.
                Returns None if option not supported
        """

        rc = MergeOptions.tackOptions.get(option)

        if rc:
            return True

        return False
