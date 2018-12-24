#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper classes for QThreadPool"""


import traceback
import sys

from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exectype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param function: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type function: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''

    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        # pylint: disable-msg=W0702
        # have to capture all exceptions using sys.exc_info()
        # to sort out what is happening
        try:
            result = self.function(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            excepttype, value = sys.exc_info()[:2]
            self.signals.error.emit((excepttype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
