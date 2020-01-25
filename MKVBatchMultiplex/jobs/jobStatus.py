"""
Class JobStatus
"""

class JobStatus:    # pylint: disable=too-few-public-methods
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
