"""
jobsDB
"""

try:
    import cPickle as pickle
except:  # pylint: disable=bare-except
    import pickle
import sys
import zlib

from .. import config

from .jobKeys import JobKey, JobsTableKey

def addToDb(database, job, update=False):
    """
    addToDb add the job to the history database

    Args:
        database (SqlJobsTable): history database
        job (JobInfo): running job information
        update (bool, optional): update is true if record should exits.
            Defaults to False.

    Returns:
        int: rowid if insert successful. 0 otherwise.
    """

    # Compress job information:
    # compressed = zlib.compress(cPickle.dumps(obj))

    # Get it back:
    # obj = cPickle.loads(zlib.decompress(compressed))

    # Key ID, startTime
    #

    bSimulateRun = config.data.get(config.ConfigKey.SimulateRun)
    rc = 0

    if not bSimulateRun:
        cmpJob = zlib.compress(pickle.dumps(job))
        if not update:
            rowid = database.insert(
                job.jobRow[JobKey.ID],
                job.date.isoformat(),
                job.addTime,
                job.startTime,
                job.endTime,
                cmpJob,
                job.oCommand.command,
                "AutoSaved",
                "AutoSaved",
                0,
                0,
            )
            rc = rowid

            if rowid > 0:
                sqlSearchUpdate = """
                    INSERT INTO jobsSearch(rowidKey, id, startTime, command)
                        VALUES(?, ?, ?, ?); """
                database.sqlExecute(
                    sqlSearchUpdate,
                    rowid,
                    job.jobRow[JobKey.ID],
                    job.startTime,
                    job.oCommand.command,
                )
            if rowid == 0:
                print("error", database.error)
                sys.exit()
        else:
            # jobsDB.update(449, (JobsTableKey.startTime, ), 80)
            database.update(
                job.jobRow[JobKey.ID],
                (JobsTableKey.startTime, JobsTableKey.endTime, JobsTableKey.job),
                job.startTime,
                job.endTime,
                cmpJob,
            )

    return rc

def removeFromDb(database, recordID, jobID, update=False):
    """
    addToDb add the job to the history database

    Args:
        database (SqlJobsTable): history database
        job (JobInfo): running job information
        update (bool, optional): update is true if record should exits.
            Defaults to False.

    Returns:
        int: rowid if insert successful. 0 otherwise.
    """

    # Compress job information:
    # compressed = zlib.compress(cPickle.dumps(obj))

    # Get it back:
    # obj = cPickle.loads(zlib.decompress(compressed))

    # Key ID, startTime
    #

    bSimulateRun = config.data.get(config.ConfigKey.SimulateRun)
    rc = 0

    if not bSimulateRun:
        if not update:
            rowid = database.delete(
                jobID,
            )
            rc = rowid

    return rc
