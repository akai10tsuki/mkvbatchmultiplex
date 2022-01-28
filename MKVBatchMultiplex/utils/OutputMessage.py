"""
    OutputMessage
"""

class OutputMessage:
    """
    Message to display out output windows QOutputTextWidget

    Args:
        message (str): property for message to display read write
        arguments (dict): property arguments for the displaying of the message
        read write
    """

    def __init__(self, message, arguments):
        self.__msg = None
        self.__args = None

        self.message = message
        self.arguments = arguments

    def setMessage(self, message=None, arguments=None):

        self.message = message
        self.arguments = arguments

    @property
    def message(self):
        """message property"""
        return self.__msg

    @message.setter
    def message(self, value):
        if isinstance(value, str):
            self.__msg = value

    @property
    def arguments(self):
        """arguments property"""
        return self.__args

    @arguments.setter
    def arguments(self, value):
        if isinstance(value, str):
            self.__arguments = value
