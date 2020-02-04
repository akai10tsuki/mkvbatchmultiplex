"""
Class to process jobs queue
"""
# RJB0011

import logging
import re

# import threading
import time

from PySide2.QtCore import QObject, Qt, Signal

import vsutillib.mkv as mkv

from vsutillib.process import ThreadWorker, RunCommand, isThreadRunning
from vsutillib.misc import staticVars

from .. import config
from .jobKeys import JobStatus


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class RunJobs(QObject):
    """
    run test run worker thread
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

    def __init__(self, parent, jobsQueue=None, progressFunc=None, log=None):
        super(RunJobs, self).__init__()

        self.__jobsQueue = None
        self.__output = None
        self.__process = None
        self.__progress = None

        self.parent = parent
        self.jobsqueue = jobsQueue
        self.progress = progressFunc

        self.mainWindow = self.parent.parent
        self.jobsWorker = None
        self.__logging = False
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
        return isThreadRunning(config.WORKERTHREADNAME)

    @property
    def jobsqueue(self):
        return self.__jobsQueue

    @jobsqueue.setter
    def jobsqueue(self, value):
        self.__jobsQueue = value

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self, value):
        self.__output = value

    @property
    def process(self):
        return self.__process

    @process.setter
    def process(self, value):
        self.__process = value

    @property
    def progress(self):
        return self.__progress

    @progress.setter
    def progress(self, value):
        self.__progress = value

    def run(self):
        """
        run summit jobs to worker
        """

        if self.jobsqueue and not self.running:

            self.jobsWorker = ThreadWorker(
                runJobs,
                self.jobsqueue,
                self.output,
                log=self.log,
                funcStart=self.start,
                funcResult=self.result,
                funcProgress=self.progress,
                funcFinished=self.finished,
            )

            self.jobsWorker.name = config.WORKERTHREADNAME
            self.jobsWorker.start()

            return True

        if not self.jobsqueue:

            msg = "Jobs Queue empty"
            self.output.error.emit(msg, {"color": Qt.yellow})

            if self.log:
                MODULELOG.error("RJB0001: Error: %s", msg)

        if self.running:

            msg = "Jobs running"
            self.output.error.emit(msg, {"color": Qt.yellow})

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
            MODULELOG.debug("RJB0004 Jobs finished.")

    def result(self, funcResult):
        """
        result from jobs queue process

        Args:
            funcResult (str): messages from runJobs
        """

        self.resultSignal.emit(funcResult)


@staticVars(newJob=False)
def displayRunJobs(line, job, output, indexTotal, funcProgress=None):
    """
    Convenience function used by runJobs
    to display lines of the mkvmerge
    execution

    Args:
        line (str): line to display
    """
    regEx = re.compile(r"(\d+)")

    funcProgress.lblSetValue.emit(2, indexTotal[0] + 1)
    n = 0

    if line.find("Progress:") >= 0:

        if m := regEx.search(line):
            n = int(m.group(1))

        if n > 0:
            output.job.emit(line[:-1], {"replaceLine": True})
            funcProgress.pbSetValues.emit(n, indexTotal[1] + n)

    else:

        output.job.emit(line[:-1], {"appendLine": True})

    if (line.find("writing.") > 0) or (line.find("Multiplexing took") == 0):
        output.job.emit("\n", {})


@staticVars(running=False)
def runJobs(jobQueue, output, funcProgress=None, log=False):
    """
    runJobs execute jobs on queue

    Args:
        jobQueue (JobQueue): Job queue has all related information for the job
        funcProgress (func, optional): function to call to report job progress. Defaults to None.

    Returns:
        str: Dummy  return value
    """

    if runJobs.running:
        # Block direct calls while working there should be none
        return "Working..."

    runJobs.running = True

    totalJobs = len(jobQueue)
    remainingJobs = totalJobs - 1
    currentJob = 0
    indexTotal = [0, 0]

    verify = mkv.VerifyStructure(log=log)

    while job := jobQueue.popLeft():

        actualRemaining = len(jobQueue)
        if actualRemaining == remainingJobs:
            remainingJobs -= 1
        else:
            totalJobs = totalJobs + actualRemaining - remainingJobs
            remainingJobs = actualRemaining - 1

        jobQueue.statusUpdateSignal.emit(job, JobStatus.Running)
        currentJob += 1

        indexTotal[0] = 0  # file index
        indexTotal[1] = 0  # current max progress bar

        totalFiles = 0
        if job.oCommand:
            totalFiles = len(job.oCommand)

        maxBar = totalFiles * 100
        funcProgress.pbSetMaximum.emit(100, maxBar)

        funcProgress.lblSetValue.emit(0, totalJobs)
        funcProgress.lblSetValue.emit(1, currentJob)
        funcProgress.lblSetValue.emit(3, totalFiles)

        indexTotal[0] = 0

        cli = RunCommand(
            processLine=displayRunJobs,
            processArgs=[job, output, indexTotal],
            processKWArgs={"funcProgress": funcProgress},
            commandShlex=True,
            universalNewLines=True,
            log=log,
        )

        if job.oCommand:

            if log:
                MODULELOG.debug("RJB0005: Job ID: %s started.", job.job[config.JOBID])

            for cmd, baseFiles, sourceFiles, destinationFiles, _ in job.oCommand:

                funcProgress.lblSetValue.emit(2, indexTotal[0] + 1)

                verify.verifyStructure(baseFiles, sourceFiles)

                if log:

                    msg = (
                        "Command: {}  Base Files: {} "
                        "Source Files: {} Destination Files: {}"
                    )
                    msg = msg.format(cmd, baseFiles, sourceFiles, destinationFiles)

                    MODULELOG.debug('RJB0006: %s', msg)


                if verify:

                    ###
                    # Execute cmd
                    ###
                    msg = (
                        "\nCommand: {}\nBase Files: {}\n"
                        "Source Files: {}\nDestination Files: {}\n\n"
                    )
                    msg = msg.format(cmd, baseFiles, sourceFiles, destinationFiles)
                    output.job.emit(msg, {})

                    if log:
                        MODULELOG.debug('RJB0007: Structure checks ok')


                    if config.SIMULATERUN:
                        dummyRunCommand(funcProgress, indexTotal)
                    else:
                        cli.command = cmd
                        cli.run()

                else:
                    msg = "\nDestination Files: {}\n".format(destinationFiles)
                    output.job.emit(msg, {})
                    for m in verify.analysis:
                        output.job.emit(m, {})

                    if log:
                        MODULELOG.error('RJB0008: Structure check failed')

                indexTotal[1] += 100
                indexTotal[0] += 1

            jobQueue.statusUpdateSignal.emit(job, JobStatus.Done)

            if log:
                MODULELOG.debug("RJB0009: Job ID: %s finished.", job.job[config.JOBID])

        else:

            msg = "Job ID: {} cannot execute command.\n\n{}\n"
            msg = msg.format(job.job[config.JOBID], job.oCommand.command)
            output.error.emit(msg, {"color": Qt.red})

            jobQueue.statusUpdateSignal.emit(job, JobStatus.Error)

            if log:
                MODULELOG.debug(
                    "RJB0010: Job ID: %s cannot execute command: %s.",
                    job.job[config.JOBID],
                    job.oCommand.command,
                )

    for index in range(4):
        funcProgress.lblSetValue.emit(index, 0)

    funcProgress.pbSetMaximum.emit(100, 100)
    funcProgress.pbSetValues.emit(0, 100)

    runJobs.running = False

    return "Job queue empty."


def dummyRunCommand(funcProgress, indexTotal):
    """
    dummyRunCommand dummy run job function
    """

    funcProgress.lblSetValue.emit(2, indexTotal[0] + 1)
    i = 0
    while i < 100:
        i += 0.5
        funcProgress.pbSetValues.emit(i, indexTotal[1] + i)
        time.sleep(0.0001)
