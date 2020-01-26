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
"""

# pylint: disable=too-few-public-methods


class HeaderAttributeKey:

    Alignment = "Alignment"
    CastFunction = "CastFunction"
    Label = "Label"
    Type = "Type"
    Width = "Width"

class DataKey:

    Data = 0
    ToolTip = 1

class HeaderInfo:
    """
    Header information
    """

    header = None
    attribute = None
    headerList = None
    toolTip = None

class DataItem:
    """
    Data item information
    """

    data = None
    toolTip = None

class Index:
    """
     Dummy QModelIndex

    Returns:
        Index: Dummy QModelIndex
    """

    def __init__(self, row, column):

        self._row = row
        self._column = column

    def row(self):

        return self._row

    def column(self):

        return self._column

    def isValid(self):

        return True

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
                "Alignment": "center",
                "CastFunction": str,
                "Label": "Column Label",
                "ToolTip": "Tool Tip string"
                "Type": "str",
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
            if len(dataList) == 1:
                self.insertRow(0, dataList)
            else:
                for position, data in enumerate(dataList):
                    self.insertRow(position, data)

    def __getitem__(self, index):

        if isinstance(index, (int, slice)):
            if (index < 0) or (index > len(self.headers) - 1):
                raise IndexError("list index [{}] out of range".format(index))

            return self.headers[index].attribute['Label']

        if isinstance(index, tuple):

            col = None

            if len(index) == 1:
                row = index[0]
            elif len(index) == 2:
                row, col = index
            else:
                raise IndexError("Bad index format: {}".format(index))

            if col is None:

                returnRow = []
                currentRow = self.data[row]
                for r in currentRow:
                    returnRow.append(r.data)

                return returnRow

            return self.data[row][col].data

        raise TypeError("Invalid index type")

    def __setitem__(self, index, value):

        if isinstance(index, int):
            self.headers[index].attribute['Label'] = value

        elif isinstance(index, tuple):
            # Only update members of the data table no headers

            print("Bad Bad")

            if len(index) == 2:

                row, col = index
            else:
                raise IndexError("Bad index format: {}".format(index))

            index = Index(row, col) # Simulate index

            self.setData(index, value)

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

    def setData(self, index, value):
        """
        Insert row at the end of the data table

        Keyword Arguments:
            dataItem {list} -- list containing a data row (default: {None})
        """

        if (value is not None) and index.isValid():
            # Use self.insertRow() so only one method add data
            # better for logging purposes
            row = index.row()
            column = index.column()
            if isinstance(value, DataItem):
                self.data[row][column].data = value.data
                self.data[row][column].toolTip = value.toolTip
            else:
                self.data[row][column].data = value
            return True

        return False

    def setToolTip(self, index, value):
        """
        Insert row at the end of the data table

        Keyword Arguments:
            dataItem {list} -- list containing a data row (default: {None})
        """

        if (value is not None) and index.isValid():
            # Use self.insertRow() so only one method add data
            # better for logging purposes
            row = index.row()
            column = index.column()
            self.data[row][column].toolTip = value
            return True

        return False

    def insertRow(self, position, row):
        """
        Insert a data row

        Arguments:
            index {int} -- row number where to insert the data
            row {list} -- list with row data
        """
        emptyRow = [DataItem(), DataItem(), DataItem()]

        self.data.insert(position, emptyRow)

        for column, value in enumerate(row):
            if isinstance(value, list):
                newItem = DataItem()
                newItem.data = value[DataKey.Data]
                newItem.toolTip = value[DataKey.ToolTip]
                index = Index(position, column)
                self.setData(index, newItem)
            else:
                if value is not None:
                    raise ValueError('Item at index {} is invalid'.format(column))

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
