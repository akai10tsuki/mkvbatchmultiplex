"""
Classes representing Keys in job related lists
"""
# pylint: disable=too-few-public-methods

class JobsDBKey:
    """
     keys representing the jobs table fields
    """

    ID = "id"
    addDate = "addDate"
    addTime = "addTime"
    startTime = "startTime"
    endTime = "endTime"
    job = "job"

    IDIndex = 0
    addTimeIndex = 1
    addTimeIndex = 2
    startTimeIndex = 3
    endTimeIndex = 4
    jobIndex = 5

class JobKey:

    ID = 0
    Status = 1
    Command = 2

class JobStatus:
    """Key values for job related work"""

    Abort = "Abort"
    Aborted = "Aborted"
    AbortForced = "AbortForced"
    AbortJob = "AbortJob"
    AbortJobError = "AbortJobError"
    AddToQueue = "AddToQueue"
    Blocked = "Blocked"
    Done = "Done"
    DoneWithError = "DoneWithError"
    Error = "Error"
    Queue = "Queue"
    Running = "Running"
    Skip = "Skip"
    Skipped = "Skipped"
    Stop = "Stop"
    Stopped = "Stopped"
    Waiting = "Waiting"
