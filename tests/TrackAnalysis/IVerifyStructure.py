"""
IVerifyStructure
"""

from vsutillib.mkv import VerifyStructure

class IVerifyStructure(VerifyStructure):
    """
    IVerifyStructure VerifyStructure sub class do verification by index on
    MKVCommandParser object

    Args:
        oCommand (object): MKVCommandParser object
        index (int): index to verify
    """

    def __init__(self, oCommand=None, index=None):
        super().__init__()

        if oCommand is not None:
            if index is not None:
                self.verifyStructure(oCommand, index)

    # Kind of fake overload
    def verifyStructure(self, oCommand, index): # pylint: disable=arguments-differ
        baseFiles = oCommand.baseFiles
        sourceFiles = oCommand.oSourceFiles[index]

        super().verifyStructure(baseFiles, sourceFiles)
