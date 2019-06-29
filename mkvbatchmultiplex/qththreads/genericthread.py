"""
Multithreading Class base on QThread
"""


import logging


from PySide2.QtCore import QThread


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class QthThread(QThread):
    """
    QThread generic class send function and arguments to start in thread

    :param function: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type function: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    log = False

    def __init__(self, function, *args, **kwargs):
        super().__init__(self)

        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        """Override run and start function from argument"""

        self.function(*self.args, **self.kwargs)

        return
