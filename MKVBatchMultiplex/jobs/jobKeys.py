"""
Classes representing Keys in job related lists
"""
# pylint: disable=too-few-public-methods

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
    Queue = "Queue"
    Error = "Error"
    Running = "Running"
    Skip = "Skip"
    Stop = "Stop"
    Waiting = "Waiting"
