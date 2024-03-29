"""
Class to process jobs queue
"""
# 11

import logging

from PySide6.QtCore import QObject, Signal


from vsutillib.process import ThreadWorker, isThreadRunning
from vsutillib.pyside6 import SvgColor

from .. import config
from ..models import TableProxyModel

#from .jobsWorker import jobsWorker
from .jobsWorker import jobsWorker

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class RunJobs(QObject):
    """
    RunJobs - class instantiated and called by JobQueue.run() it will start the
    Jobs Worker in a new thread to proccess the Jobs queue.

    Args:
        **parent** (QWidget): parent widget

        **jobsQueue** (deque, optional): Queue with Jobs to execute. Defaults to
        None.

        **progressFunc** (function, optional): Function that updates progress bar.
        Defaults to None.

        **proxyModel** (TableProxyModel, optional): Proxy model for model/view.
        Defaults to None.

        **controlQueue** (deque, optional): Queue to control Jobs execution.
        Some status conditions are routed through here to Stop, Skip or Abort Jobs.
        Defaults to None.

        **log** (bool, optional): Logging can be cotrolled using this parameter.
        Defaults to None.
    """

    finishedSignal = Signal()
    startSignal = Signal()
    resultSignal = Signal(object)

    # Class logging state
    __log = False

    @classmethod
    def classLog(cls, setLogging=None):
        """
        get/set logging at class level
        every class instance will log
        unless overwritten

        Args:
            setLogging (bool):
                - True class will log
                - False turn off logging
                - None returns current Value

        Returns:
            bool:

            returns the current value set
        """

        if setLogging is not None:
            if isinstance(setLogging, bool):
                cls.__log = setLogging

        return cls.__log

    def __init__(
        self,
        parent,
        jobsQueue=None,
        progressFunc=None,
        proxyModel=None,
        controlQueue=None,
        log=None,
    ):
        super(RunJobs, self).__init__()

        self.__jobsQueue = None
        self.__logging = False
        self.__output = None
        self.__process = None
        self.__progress = None
        self.__proxyModel = None
        self.__model = None

        self.parent = parent
        self.jobsqueue = jobsQueue
        self.progress = progressFunc
        self.proxyModel = proxyModel
        self.controlQueue = controlQueue
        self.mainWindow = self.parent.parent
        self.worker = None
        self.log = log

    @property
    def log(self):
        """
        class property can be used to override the class global
        logging setting

            bool:

            True if logging is enable False otherwise
        """
        if self.__log is not None:
            return self.__log

        return RunJobs.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    @property
    def running(self):
        """
        running read only property

        Returns:
            bool: True if jobs worker is running. False otherwise.
        """
        return isThreadRunning(config.WORKERTHREADNAME)

    @property
    def jobsqueue(self):
        """
        jobsqueue jobs queue read write

        Returns:
            deque: jobs queue
        """
        return self.__jobsQueue

    @jobsqueue.setter
    def jobsqueue(self, value):
        self.__jobsQueue = value

    @property
    def model(self):
        """
        model used in model/view read only

        Returns:
            JobsTableModel: model used in model/view
        """
        return self.__model

    @property
    def proxyModel(self):
        """
        proxyModel of model used in model/view read write

        Returns:
            TableProxyModel: Filtered model of source model used in model/view
        """
        return self.__proxyModel

    @proxyModel.setter
    def proxyModel(self, value):
        if isinstance(value, TableProxyModel):
            self.__proxyModel = value
            self.__model = value.sourceModel()

    @property
    def output(self):
        """
        output permit access to output windows read write

        Returns:
            OutputWindows: provides access to command, job, and error tabs
        """
        return self.__output

    @output.setter
    def output(self, value):
        self.__output = value

    @property
    def process(self):
        """
        process function to proccess jobs output from subprocess pipe read write

        Returns:
            function: function to process jobs output
        """
        return self.__process

    @process.setter
    def process(self, value):
        self.__process = value

    @property
    def progress(self):
        """
        progress function to update progress bar read write

        Returns:
            DualProgressBar: progress bar of main window
        """
        return self.__progress

    @progress.setter
    def progress(self, value):
        self.__progress = value

    def run(self):
        """
        run summit jobs queue to jobs worker in new thread. While running any
        new job added to the queue will be proccessed.
        """

        if self.jobsqueue and not self.running:
            self.worker = ThreadWorker(
                jobsWorker,
                self.jobsqueue,
                self.output,
                self.proxyModel,
                self.progress,
                self.controlQueue,
                self.parent.parent.trayIconMessageSignal,
                log=self.log,
                funcStart=self.start,
                funcResult=self.result,
                funcFinished=self.finished,
            )
            self.worker.name = config.WORKERTHREADNAME
            self.worker.start()

            return True

        if not self.jobsqueue:
            msg = "Jobs Queue empty"
            self.output.error.emit(msg, {"color": SvgColor.yellow})

            if self.log:
                MODULELOG.error("RJB0001: Error: %s", msg)

        if self.running:
            msg = "Jobs running"
            self.output.error.emit(msg, {"color": SvgColor.yellow})

            if self.log:
                MODULELOG.error("RJB0002: Error: %s", msg)

        return False

    def start(self):
        """
        start generate signal for start of run
        """

        self.startSignal.emit()

        if self.log:
            MODULELOG.debug("RJB0003: Jobs started.")

    def finished(self):
        """
        finished generate signal for finished run
        """

        self.finishedSignal.emit()

        if self.log:
            MODULELOG.debug("RJB0004: Jobs finished.")

    def result(self, funcResult):
        """
        result from jobs queue process

        Args:
            funcResult (str): messages from jobsWorker
        """

        self.resultSignal.emit(funcResult)
