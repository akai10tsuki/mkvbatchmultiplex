"""
Class to process jobs queue
"""
# RJB0001

import logging
import re

# import threading
import time

from PySide2.QtCore import QObject, Signal

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

    # Class logging state
    __log = False

    def __init__(self, parent, jobsQueue=None, progressFunc=None):
        super(RunJobs, self).__init__()

        self.__jobsQueue = None
        self.__process = None
        self.__progress = None

        self.parent = parent
        self.jobsqueue = jobsQueue
        self.progress = progressFunc

        self.mainWindow = self.parent.parent
        self.jobsWorker = None
        self.__logging = False
        self.__running = False

    @property
    def running(self):
        return self.__running

    @property
    def jobsqueue(self):
        return self.__jobsQueue

    @jobsqueue.setter
    def jobsqueue(self, value):
        self.__jobsQueue = value

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

        if self.jobsqueue and not isThreadRunning(config.WORKERTHREADNAME):

            self.jobsWorker = ThreadWorker(
                runJobs,
                self.jobsqueue,
                self.mainWindow,
                funcStart=self.start,
                funcResult=self.result,
                funcProgress=self.progress,
                funcFinished=self.finished,
            )

            self.jobsWorker.name = config.WORKERTHREADNAME
            self.jobsWorker.start()
            self.__running = True

    def start(self):
        """
        start generate signal for start of run
        """
        self.__running = True
        self.startSignal.emit()

    def finished(self):
        """
        finished generate signal for finished run
        """
        self.__running = False
        self.finishedSignal.emit()

    def result(self, funcResult):
        """
        result from jobs queue process

        Args:
            funcResult (str): messages from runJobs
        """

        print(funcResult)


@staticVars(newJob=False)
def displayRunJobs(line, job, mainWindow, indexTotal, funcProgress=None):
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
        print("\r" + line[:-1], end="")

        if m := regEx.search(line):
            n = int(m.group(1))

        if n > 0:
            mainWindow.jobsOutputSignal.emit(line[:-1], {"replaceLine": True})
            funcProgress.pbSetValues.emit(n, indexTotal[1] + n)

    else:

        print(line, end="")
        mainWindow.jobsOutputSignal.emit(line[:-1], {"appendLine": True})

    if (line.find("writing.") > 0) or (line.find("Multiplexing took") == 0):
        mainWindow.jobsOutputSignal.emit("\n", {})


@staticVars(running=False)
def runJobs(jobQueue, mainWindow, funcProgress=None):
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

    verify = mkv.VerifyStructure()

    while job := jobQueue.popLeft():

        actualRemaining = len(jobQueue)
        if actualRemaining == remainingJobs:
            remainingJobs -= 1
        else:
            totalJobs = totalJobs + actualRemaining - remainingJobs
            remainingJobs = actualRemaining - 1

        jobQueue.statusUpdateSignal.emit(job, JobStatus.Running)
        currentJob += 1

        print(
            "At position ({}, {}) ID = {} Running.. ".format(
                job.statusIndex.row(), job.statusIndex.column(), job.job[config.JOBID],
            )
        )

        # Test

        indexTotal[0] = 0  # file index
        indexTotal[1] = 0  # current max progress bar

        # Job(s): {0:3d} Current: {1:3d} File: {2:3d} of {3:3d} Errors: {4:3d}

        totalFiles = 0
        if job.oCommand:
            # print("Total files {}".format(len(job.oCommand)))
            totalFiles = len(job.oCommand)

        maxBar = totalFiles * 100
        funcProgress.pbSetMaximum.emit(100, maxBar)

        funcProgress.lblSetValue.emit(0, totalJobs)
        funcProgress.lblSetValue.emit(1, currentJob)
        funcProgress.lblSetValue.emit(3, totalFiles)

        indexTotal[0] = 0

        cli = RunCommand(
            processLine=displayRunJobs,
            processArgs=[job, mainWindow, indexTotal],
            processKWArgs={"funcProgress": funcProgress},
            commandShlex=True,
            universalNewLines=True,
        )

        for cmd, baseFiles, sourceFiles, destinationFiles, _ in job.oCommand:

            funcProgress.lblSetValue.emit(2, indexTotal[0] + 1)

            verify.verifyStructure(baseFiles, sourceFiles)

            if verify:
                ###
                # Execute cmd
                ###
                msg = "\nCommand: {}\nBase Files: {}\nSource Files: {}\nDestination Files: {}\n\n"
                msg = msg.format(cmd, baseFiles, sourceFiles, destinationFiles)
                mainWindow.jobsOutputSignal.emit(msg, {})

                cli.command = cmd
                #cli.run()

                dummyRunCommand(cmd, job, funcProgress, indexTotal)

            else:

                msg = "\nDestination Files: {}\n".format(destinationFiles)
                mainWindow.jobsOutputSignal.emit(msg, {})
                for m in verify.analysis:
                    mainWindow.jobsOutputSignal.emit(m, {})

            indexTotal[1] += 100
            indexTotal[0] += 1

        jobQueue.statusUpdateSignal.emit(job, JobStatus.Done)

    for index in range(4):
        funcProgress.lblSetValue.emit(index, 0)

    funcProgress.pbSetMaximum.emit(100, 100)
    funcProgress.pbSetValues.emit(0, 100)

    runJobs.running = False

    return "Job queue empty."


def dummyRunCommand(command, job, funcProgress, indexTotal):
    """
    dummyRunCommand dummy run job function
    """
    print("\nJob ID: {} \nCommand: {}\n".format(job.job[config.JOBID], command))

    # j current file
    funcProgress.lblSetValue.emit(2, indexTotal[0] + 1)
    i = 0
    while i < 100:
        i += 0.1
        funcProgress.pbSetValues.emit(i, indexTotal[1] + i)
        time.sleep(0.0001)
