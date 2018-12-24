#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Multithreading Class base on QThread"""


from PyQt5.QtCore import QThread


class GenericThread(QThread):
    """
    QThread generic class send function and arguments to start in thread

    :param function: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type function: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """
    def __init__(self, function, *args, **kwargs):
        QThread.__init__(self)

        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        """Override run and start function from argument"""

        self.function(*self.args, **self.kwargs)

        return
