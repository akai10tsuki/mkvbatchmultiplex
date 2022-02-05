"""
Module that defines the table data use in the model/view
"""

# pylint: disable=too-few-public-methods

import itertools
from typing import Any, ClassVar, List, Optional, TypedDict, Union


class HeadersDict(TypedDict):
    Alignment: str
    CastFunction: object
    Label: str
    ToolTip: str
    Type: str
    Width: int


class DataItem:
    """
    Data item information:
        - cell (object) = value of cell in table cast to a type depending on
          attribute in header
        - toolTip (str) = toolTip to show when mouse hovers over it
        - obj (object) = python object
    """

    cell: ClassVar[object] = None
    toolTip: ClassVar[str] = None
    obj: ClassVar[object] = None


class DataKey:
    """
    DataItem index names for when the DataItem is represented in a list.
    """

    Cell: ClassVar[int] = 0
    ToolTip: ClassVar[int] = 1
    Obj: ClassVar[int] = 2


class HeaderAttributeKey:
    """
    Header Attribute dictionary keys.
    """

    Alignment: ClassVar[str] = "Alignment"
    CastFunction: ClassVar[str] = "CastFunction"
    Label: ClassVar[str] = "Label"
    ToolTip: ClassVar[str] = "ToolTip"
    Type: ClassVar[str] = "Type"
    Width: ClassVar[str] = "Width"


class HeaderInfo:
    """
    Header information for a column

        - header (str) - column name
        - attribute (dict) - for the attributes to apply to the cell data
        - toolTip (str) - toolTip to show
    """

    header: ClassVar[str] = None
    attribute: ClassVar[dict] = None
    toolTip: ClassVar[str] = None


class Index:
    """
    Dummy QModelIndex to ease data manupulations.

    Returns:
        Index: Dummy QModelIndex
    """

    def __init__(self, row: int, column: int):

        self._row = row
        self._column = column

    def column(self):
        """
        column of cell

        Returns:
            int: column of cell in table
        """
        return self._column

    def isValid(self):  # pylint: disable=no-self-use
        """
        isValid dummy check for Index validity

        Returns:
            bool: allways returns true
        """
        return True

    def row(self):
        """
        row of cell

        Returns:
            int: row of cell in table
        """

        return self._row


class TableData:
    """
    Class to represent data in a table with columns headers

    data[row][column] = DataItem


    Args:
        **headerList** (list, optional): List with header information.
        Defaults to None.

            A headerList is a list of the form:

                [str, dict]

                (str) - string representing the column name

                (dict) - dictionary representing different attributes

                    - "Alignment": alignment for column header label
                    - "CastFunction": function to cast cell to element type
                    - "Label": label header for the column
                    - "ToolTip": text to show for tool tip
                    - "Type": type of element in cell
                    - "Width": width for the column header

                ::

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

        **dataList** (list, optional): list with initialization data.
        Defaults to None.

            dataList is a list that represent a table with m rows and n columns
            in the form:

            .. code:: python

                dataList = [ row1, row2 , ...]

                row = [
                    [cell value, toolTip value, obj value],
                    [cell value, toolTip value, obj value],
                    ...
                ]

                rows have n columns

                dataList = [
                    [
                        [cell value, toolTip value, obj value],
                        [cell value, toolTip value, obj value],
                        ...
                    ],
                    [
                        [cell value, toolTip value, obj value],
                        [cell value, toolTip value, obj value],
                        ...
                    ],
                    ...
                ]

                dataList has m rows

            Every row should have the same number of columns.

        Raises:
        ::
            IndexError: index is out of range
            TypeError: invalid index type

    Returns:
        If an instance of the class is accessed using list notation the class returns:

            If **data** is a TableData instance.

                data[row] - column header

                data[row,] - table row at index

                tableData[row, col] - element at position row, col on table
    """

    def __init__(
            self,
            headerList: Optional[List[Union[str, HeadersDict]]] = None,
            dataList: Optional[List[Union[object, str]]] = None):

        self.data = []  # 2 dimensional dataset of DataItem
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
                    # data is expected to be 3 element list
                    self.insertRow(position, data)

    def __getitem__(self, index: int):

        if isinstance(index, (int, slice)):
            # to access the elements in full dataset.data[row][column] for DataItem
            #  or dataset.data[row][col].member for DataIem.member
            # dataset[index] returns columns labels
            if (index < 0) or (index > len(self.headers) - 1):
                raise IndexError("list index [{}] out of range".format(index))

            return self.headers[index].attribute[HeaderAttributeKey.Label]

        if isinstance(index, tuple):
            # dataset[row,] returns the [row] list
            # dataset[row, col] returns DataIem.cell value
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
                    returnRow.append(r.cell)

                return returnRow

            return self.data[row][col].cell

        raise TypeError("Invalid index type")

    def __setitem__(self, index: Union[int, tuple], value: Any):

        if isinstance(index, int):
            self.headers[index].attribute["Label"] = value

        elif isinstance(index, tuple):
            # Only update members of the data table no headers
            if len(index) == 2:
                row, col = index
            else:
                raise IndexError(f"Bad index format: {index}")

            index = Index(row, col)  # Simulate index
            self.setData(index, value)
        else:
            raise TypeError("Invalid index type")

    def __len__(self):
        return len(self.data)

    def addHeader(
            self,
            header: Optional[List[Union[str, HeadersDict]]] = None) -> None:
        """
        Add header information. header has the form = [str, dict]

        Keyword Arguments:
            **header** (list) -- list containing the a header (default: {None})
        """

        if header is not None:
            oHeader = HeaderInfo()
            oHeader.header = header[0]
            oHeader.attribute = header[1]
            self.headerName.append(header[0])
            self.headers.append(oHeader)

    def deleteColumn(self, index: int) -> Any:
        """
        Delete a column from the table

        Arguments:
            **index** (int) -- column to delete

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

    def insertColumn(
            self,
            position: Optional[int] = 0,
            columnHeader: Optional[str] = None,
            columnData: Optional[Union[str, Any]] = None) -> None:
        """
        Insert a data column

        Arguments:
            **position** (int) -- column number where to insert the data

            **columnHeader** (str) -- header for column to be inserted

            **columnData** (list) -- data to insert in column cells
        """

        if columnHeader is None:
            self.headers.insert(position, HeaderInfo())
            self.headerName.insert(position, "")
        else:
            if isinstance(columnHeader, list):
                oHeader = HeaderInfo()
                oHeader.header = columnHeader[0]
                oHeader.attribute = columnHeader[1]
                self.headers.insert(position, oHeader)
                self.headerName.insert(position, oHeader.header)
            elif isinstance(columnHeader, HeaderInfo):
                self.headers.insert(position, columnHeader)
                self.headers.insert(position, columnHeader.header)
            else:
                raise TypeError("Invalid column header type.")

        if columnData is None:
            for r in self.data:
                r.insert(position, DataItem())
        else:
            for _, r in enumerate(self.data):
                element = DataItem()
                element.cell = columnData[0]
                r.insert(position, columnData[1])

    def insertRow(
            self,
            position: int,
            row: Optional[List[Union[str, Any]]] = None) -> None:
        """
        Insert a data row

        Arguments:
            **position** (int) -- row number where to insert the data

            **row** (list) -- list with row data. Defaults to {None}
        """

        if row is not None:
            totalColumns = len(self.headerName)
            emptyRow = []
            for _ in itertools.repeat(None, totalColumns):
                rowItem = DataItem()
                emptyRow.append(rowItem)

            self.data.insert(position, emptyRow)

            for column, value in enumerate(row):
                if isinstance(value, list):
                    newItem = DataItem()
                    newItem.cell = value[DataKey.Cell]
                    newItem.toolTip = value[DataKey.ToolTip]
                    newItem.obj = value[DataKey.Obj]
                    index = Index(position, column)
                    self.setData(index, newItem)
                else:
                    if value is not None:
                        raise ValueError(
                            "Item at index {} is invalid".format(column))
        else:
            totalColumns = len(self.headerName)
            emptyRow = []
            for _ in itertools.repeat(None, totalColumns):
                emptyRow.append("")
            self.data.insert(position, emptyRow)

    def removeRow(self, index: int) -> List[Union[str, Any]]:
        """
        Delete a data row

        Arguments:
            **index** (int) -- row number to delete 0 based

        Returns:
            list -- row deleted
        """
        element = self.data.pop(index)

        return element

    def setData(self, index: int, value: List[Union[str, Any]]) -> bool:
        """
        Insert row at the end of the data table

        Keyword Arguments:
            **dataItem** (list) -- list containing a data row (default: {None})
        """

        if (value is not None) and index.isValid():
            # Use self.insertRow() so only one method add data
            # better for logging purposes
            row = index.row()
            column = index.column()

            if isinstance(value, DataItem):
                self.data[row][column].cell = value.cell
                self.data[row][column].toolTip = value.toolTip
                self.data[row][column].obj = value.obj
            else:
                self.data[row][column].cell = value

            return True

        return False

    def setToolTip(self, index: Index, value: str) -> bool:
        """
        Insert row at the end of the data table

        Keyword Arguments:
            **dataItem** (list) -- list containing a data row (default: {None})
        """

        if (value is not None) and index.isValid():
            # Use self.insertRow() so only one method add data
            # better for logging purposes
            row = index.row()
            column = index.column()
            self.data[row][column].toolTip = value

            return True

        return False
