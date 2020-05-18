"""
 Jobs database
"""

from vsutillib.sql import SqlDb


class SqlJobsTable(SqlDb):
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
            self._createJobsTable()

    def _createJobsTable(self):
        # Create jobs table
        if self.connection is not None:
            sqlJobsTable = """ CREATE TABLE IF NOT EXISTS jobs (
                                id INTEGER,
                                addDate TEXT,
                                addTime REAL,
                                startTime REAL,
                                endTime REAL,
                                job BLOB,
                                projectName TEXT,
                                projectInfo TEXT,
                                saved INTEGER,
                                delete INTEGER
                                ) """
            sqlDbInfoTable = """ CREATE TABLE IF NOT EXISTS dbInfo (
                                dbTable TEXT NOT NULL UNIQUE,
                                version TEXT NOT NULL
                                ) """
            self.sqlExecute(sqlJobsTable)
            self.sqlExecute(sqlDbInfoTable)
            if self.version("jobs") is None:
                updateTablesFromNone(self)
                self.setVersion("jobs", "2.0.0a1")

    def setVersion(self, *args):
        """
        set table version

        Args:
            dbTable (str): sql table
            version (str): table version
        """

        sqlSetVersion = """
            INSERT INTO
                dbInfo(dbTable, version)
                VALUES(?, ?)
        """

        self.sqlExecute(sqlSetVersion, *args)
        self.connection.commit()

    def version(self, dbTable):
        """
        version get table version

        Args:
            dbTable (str): sql table

        Returns:
            str: version of table
        """

        sqlVersion = "SELECT version FROM dbInfo WHERE dbTable = ?"

        cursor = self.sqlExecute(sqlVersion, dbTable)

        if cursor:
            row = cursor.fetchone()
            if row:
                return row[0]

        return None

    def connect(self, database, autoCommit=False):
        """override connect to create tables"""

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

    def fetchJob(self, jobID, *args, fetchAll=False, whereClause=None, orderClause=None):
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

def updateTablesFromNone(database):
    """
    update jobs table form no version to version 2.0.0a1
    """

    sqlScript = """
        -- disable foreign key constraint check
        PRAGMA foreign_keys=off;

        -- start a transaction
        BEGIN TRANSACTION;

        -- Here you can drop column or rename column
        CREATE TABLE IF NOT EXISTS new_jobs_table(
            id INTEGER,
            addDate TEXT,
            addTime REAL,
            startTime REAL,
            endTime REAL,
            job BLOB,
            projectName TEXT,
            projectInfo TEXT,
            saved INTEGER,
            toDelete INTEGER
        );
        -- copy data from the table to the new_table
        INSERT INTO new_jobs_table(id, addDate, addTime, startTime, endTime, job)
        SELECT id, addDate, addTime, startTime, endTime, job
        FROM jobs;

        -- drop the table
        DROP TABLE jobs;

        -- rename the new_table to the table
        ALTER TABLE new_jobs_table RENAME TO jobs;

        -- set new fields with default values
        UPDATE jobs SET
          projectName = "AutoSaved",
          projectInfo = "AutoSaved",
          saved = 0,
          toDelete = 0;

        -- commit the transaction
        COMMIT;

        -- enable foreign key constraint check
        PRAGMA foreign_keys=on; """

    cursor = database.connection.cursor()
    cursor.executescript(sqlScript)
