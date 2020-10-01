"""
Jobs Views Helpers
"""

from .. import config
from ..utils import Text, yesNoDialog

##
# BUG #7
#
# Jobs still execute after been removed from list
##
def removeJob(self, jobID):
    """
    removeJob confirm job remove filtering

    Args:
        jobID (int|None): if int is the job ID if None multi-selection

    Returns:
        bool: True remove selection. Do nothing if False
    """

    language = config.data.get(config.ConfigKey.Language)
    leadQuestionMark = "¿" if language == "es" else ""
    bAnswer = False
    if jobID is not None:
        title = _(Text.txt0138) + ": " + str(jobID)
        msg = leadQuestionMark + _(Text.txt0139) + "?"
    else:
        title = _(Text.txt0138)
        msg = leadQuestionMark + _(Text.txt9000) + "?"
    bAnswer = yesNoDialog(self, msg, title)

    return bAnswer
