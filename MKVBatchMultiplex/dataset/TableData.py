"""
Class to represent data in a table with headers

Header:
    header {str} - header ID
    attribute {dict}  -
        "Type": type of element in cell
        "CastFunction": function to cast cell to element type
        "Label": label header for the column
        "Alignment": alignment for column header label
        "Width": width for the column header

        [
            "jobID",
            {
                "Type": "int",
                "CastFunction": int,
                "Label": "Job ID",
                "Alignment": "right",
                "Width": 80,
            },
        ],

TODO: Add capacity to remove rows and columns
"""


class HeaderInfo:
    """
    Header information
    """

    header = None
    attribute = None
    headerList = None


class TableData:
    """
    Class to represent data in a table with columns headers

    A header is a list of the form:
        [str, dict]
        str = string representing the column name
        dict = dictionary representing different attributes
        [
            "Column Name",
            {
                "Type": "str",
                "CastFunction": str,
                "Label": "Column Label",
                "Alignment": "center",
                "Width": 220,
            },
        ]

    Raises:
        IndexError: index is out of range
        TypeError: invalid index type

    Returns:
        str -- tableData[index] column header
        list - tableData[index,] data row
        object - tableData[row, col] element at position row,col on table
    """

    def __init__(self, headerList=None, dataList=None):

        self.data = []  # 2 dimensional dataset
        self.headers = []  # list of HeaderInfo objects
        self.headerName = []  # list of header/columns names HeaderInfo.header

        if headerList is not None:
            for h in headerList:
                self.addHeader(h)

            if dataList is not None:
                for d in dataList:
                    self.addData(d)

    def __getitem__(self, index):

        if isinstance(index, (int, slice)):
            if (index < 0) or (index > len(self.headers) - 1):
                raise IndexError("list index [{}] out of range".format(index))
            return self.headers[index]

        if isinstance(index, tuple):

            col = None

            if len(index) == 1:
                row = index[0]
            elif len(index) == 2:
                row, col = index
            else:
                raise IndexError("Bad index format: {}".format(index))

            if col is None:
                return self.data[row]

            return self.data[row][col]

        raise TypeError("Invalid index type")

    def __setitem__(self, index, value):

        if isinstance(index, tuple):
            # Only update members of the data table no headers
            if len(index) == 2:
                row, col = index
            else:
                raise IndexError("Bad index format: {}".format(index))

            self.data[row][col] = value

        else:
            raise TypeError("Invalid index type")

    def __len__(self):
        return len(self.data)

    def addHeader(self, header=None):
        """
        Add header information

        Keyword Arguments:
            header {list} -- list containing the a header (default: {None})
        """

        if header is not None:

            self.headerName.append(header[0])

            oHeader = HeaderInfo()
            oHeader.header = header[0]
            oHeader.attribute = header[1]
            oHeader.headerList = header

            self.headers.append(oHeader)

    def addData(self, dataItem=None):
        """
        Insert row at the end of the data table

        Keyword Arguments:
            dataItem {list} -- list containing a data row (default: {None})
        """

        if dataItem is not None:
            # Use self.insertRow() so only one method add data
            # better for logging purposes

            index = len(self) + 1
            self.insertRow(index, dataItem)

    def insertRow(self, index, row):
        """
        Insert a data row

        Arguments:
            index {int} -- row number where to insert the data
            row {list} -- list with row data
        """
        self.data.insert(index, row)

    def deleteRow(self, index):
        """
        Delete a data row

        Arguments:
            index {int} -- row number to delete 0 based

        Returns:
            list -- row deleted
        """
        element = self.data.pop(index)

        return element

    def insertColumn(self, index=0, columnHeader=None, columnData=None):
        """
        Insert a data column

        Arguments:
            index {int} -- row number where to insert the data
            row {list} -- list with row data
        """

        if columnHeader is None:
            self.headers.insert(index, HeaderInfo())
            self.headerName.insert(index, "")

        else:

            if isinstance(columnHeader, list):

                oHeader = HeaderInfo()
                oHeader.header = columnHeader[0]
                oHeader.attribute = columnHeader[1]
                oHeader.headerList = columnHeader

                self.headers.insert(index, oHeader)
                self.headerName.insert(index, oHeader.header)

            elif isinstance(columnHeader, HeaderInfo):

                self.headers.insert(index, columnHeader)
                self.headers.insert(index, columnHeader.header)

            else:

                raise TypeError("Invalid column header type.")

        if columnData is None:
            for r in self.data:
                r.insert(index, "")
        else:
            for i, r in enumerate(self.data):
                r.insert(index, columnData[i])

    def deleteColumn(self, index):
        """
        Delete a column from the table

        Arguments:
            index {int} -- column to delete

        Returns:
            list -- list containing the header ID, header attributes and data rows deleted
        """

        deletedInfo = []
        deletedRows = []
        deletedInfo.append(self.headers.pop(index))
        deletedInfo.append(self.headerName.pop(index))

        for row in self.data:
            deletedRows.append(row.pop(index))

        deletedInfo.append(deletedRows)

        return deletedInfo
