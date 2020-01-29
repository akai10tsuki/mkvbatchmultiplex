"""
Class to process jobs queue
"""
# RJB0001

import logging
import threading
import time

from PySide2.QtCore import QObject

import vsutillib.mkv as mkv

from vsutillib.process import ThreadWorker
from vsutillib.misc import staticVars

from .. import config
from .jobKeys import JobStatus


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class RunJobs(QObject):
    """
    run test run worker thread
    """

    # Class logging state
    __log = False

    def __init__(self, jobsQueue, progressFunc):
        super(RunJobs, self).__init__()

        self.jobsQueue = jobsQueue
        self.progress = progressFunc
        self.jobsWorker = None
        self.__logging = False

    def run(self):
        """
        run summit jobs to worker
        """

        if self.jobsQueue:
            # jobToRun = QthThreadWorker(
            if isinstance(self.jobsWorker, ThreadWorker):
                print(
                    "Create threads total {} ID = {}".format(
                        threading.activeCount(), self.jobsWorker.native_id
                    )
                )
            else:
                print("Check failed.")

            self.jobsWorker = ThreadWorker(
                runJobs,
                self.jobsQueue,
                funcResult=self.result,
                funcProgress=self.progress,
                funcFinished=self.finished,
            )

            print("Before threads total {}".format(threading.activeCount()))
            if not self.jobsWorker.isAlive():
                self.jobsWorker.name = "jobsWorker"
                self.jobsWorker.start()
                print(
                    "After threads total {} ID = {}".format(
                        threading.activeCount(), self.jobsWorker.native_id
                    )
                )
            else:
                print("Worker active.")
                print("Alive threads total {}".format(threading.activeCount()))

        else:

            print("No work to be done Queue empty...")

    def finished(self):
        """
        finished delete Thread object
        """

        print("finished")

    def result(self, funcResult):
        """
        result from jobs queue process

        Args:
            funcResult (str): messages from runJobs
        """

        print(funcResult)


@staticVars(running=False)
def runJobs(jobQueue, funcProgress=None):
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

        i = 0
        j = 0
        t = 0

        # Job(s): {0:3d} Current: {1:3d} File: {2:3d} of {3:3d} Errors: {4:3d}

        totalFiles = 0
        if job.oCommand:
            print("Total files {}".format(len(job.oCommand)))
            totalFiles = len(job.oCommand)

        maxBar = totalFiles * 100
        funcProgress.pbSetMaximum.emit(100, maxBar)

        funcProgress.lblSetValue.emit(0, totalJobs)
        funcProgress.lblSetValue.emit(1, currentJob)
        funcProgress.lblSetValue.emit(3, totalFiles)

        if job.oCommand:
            print("Total files {}".format(len(job.oCommand)))

        # while j < totalFiles:
        #    funcProgress.lblSetValue.emit(2, j + 1)
        #    while i < 100:
        #        i += 0.1
        #        funcProgress.pbSetValues.emit(i, t + i)
        #        time.sleep(0.0001)

        j = 0
        for cmd, basefiles, sourcefiles, _, _ in job.oCommand:

            funcProgress.lblSetValue.emit(2, j + 1)

            ###
            # Execute cmd
            ###

            dummyRunCommand(cmd, job, funcProgress, j, t)

            t += 100
            j += 1
            i = 0

        jobQueue.statusUpdateSignal.emit(job, JobStatus.Done)

    for index in range(4):
        funcProgress.lblSetValue.emit(index, 0)

    funcProgress.pbSetMaximum.emit(100, 100)
    funcProgress.pbSetValues.emit(0, 100)

    runJobs.running = False

    return "Job queue empty."


def dummyRunCommand(command, job, funcProgress, j, t):

    print("\nJob ID: {} \nCommand: {}\n".format(job.job[config.JOBID], command))

    # j current file
    funcProgress.lblSetValue.emit(2, j + 1)
    i = 0
    while i < 100:
        i += 0.1
        funcProgress.pbSetValues.emit(i, t + i)
        time.sleep(0.0001)
