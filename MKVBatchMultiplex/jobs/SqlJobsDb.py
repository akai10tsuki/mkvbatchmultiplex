"""
 Jobs database
"""

from vsutillib.sql import SqlDb


class SqlJobsDB(SqlDb):
    """
    SqlJobsDB sqlite database for jobs history

    Args:
        SqlDb (class): class for managing sqlite connections
    """

    def __init__(self, dbFile=None):
        super().__init__(dbFile)

    def _initHelper(self):

        # Create jobs table
        if self.connection is not None:
            sqlJobsTable = """ CREATE TABLE IF NOT EXISTS jobs (
                                id integer PRIMARY KEY,
                                addDate text,
                                addTime REAL,
                                startTime REAL,
                                endTime REAL,
                                job BLOB
                                ) """
            self.sqlExecute(sqlJobsTable)

    def connect(self, database, autoCommit=False):
        super().connect(database, autoCommit)

        self._initHelper()

    def delete(self, jobID):
        """
        delete job from database

        Args:
            jobID (int): job id to delete

        Returns:
            sqlite3.cursor: cursor to the database aftter operation
        """

        cursor = None
        if isinstance(jobID, int):
            sqlDeleteJob = "DELETE FROM jobs WHERE id=?"
            cursor = self.sqlExecute(sqlDeleteJob, jobID)
            if cursor is not None:
                self.connection.commit()

        return cursor

    def insert(self, *args):
        """
        insert job into database

        Args:
            jobID (int): job id to insert

        Returns:
            sqlite3.cursor: cursor to the database after operation
        """

        sqlJob = """ INSERT INTO
                     jobs(id, addDate, addTime, startTime, endTime, job)
                     VALUES(?, ?, ?, ?, ?, ?) """
        cursor = self.sqlExecute(sqlJob, *args)
        if cursor is not None:
            self.connection.commit()

        return cursor

    def fetchJob(self, jobID, *args, fetchAll=False, whereClause=None):
        """
        fetchJob fetch information from database by job id

        Args:
            jobID (int): job identification number
            fields (tuple, optional): tuple with fields. Defaults to None.
            fetchAll (bool, optional): fetch all records in query. Defaults to False.

        Returns:
            sqlite3.cursor: cursor to the operation results
        """

        fetchFields = ""
        wClause = ""
        values = ""
        if isinstance(jobID, dict):
            strTmp = ""
            wClause = "WHERE "
            totalFields = len(jobID)
            values = []
            for i, (f, v) in enumerate(jobID.items()):
                strTmp += f + " = ?"
                if i < (totalFields - 1):
                    strTmp += " AND "
                values.append(v)
            wClause += strTmp
            if args:
                strTmp = ""
                totalFields = len(args)
                for i, f in enumerate(args):
                    fetchFields += f
                    if i < (totalFields - 1):
                        fetchFields += ", "
            else:
                fetchFields = "*"
        elif isinstance(jobID, int):
            if jobID <= 0:
                fetchFields = "*"
                wClause = ""
            else:
                fetchFields = "*"
                wClause = "WHERE id = ?"
                values = [jobID]

        cursor = None
        if whereClause is not None:
            wClause = whereClause

        sqlFetchID = (
            "SELECT " + fetchFields + " FROM jobs" + (""
            if wClause == ""
            else " " + wClause)
        )

        if values:
            cursor = self.sqlExecute(sqlFetchID, *values)
        else:
            cursor = self.sqlExecute(sqlFetchID)

        if fetchAll:
            cursor.fetchall()

        return cursor

    def update(self, jobID, fields, *args):
        """
        update job information on database

        fields = (id, addDate, addTime, startTime, endTime, job)

        Args:
            jobID (int): job id to update
            fields (tuple): fields to update
            args (tuple): values to update
        """

        sqlUpdateJob = "UPDATE jobs SET "
        values = []
        totalFields = len(fields)
        strTmp = ""

        for i, f in enumerate(fields):
            strTmp += f + " = ?"
            if i < (totalFields - 1):
                strTmp += ", "

        sqlUpdateJob += strTmp + " WHERE id = ?"

        for v in args:
            values.append(v)

        values.append(jobID)

        cursor = None

        if isinstance(jobID, int) and isinstance(fields, tuple):

            cursor = self.sqlExecute(sqlUpdateJob, *values)
            if cursor is not None:
                self.connection.commit()

        return cursor
