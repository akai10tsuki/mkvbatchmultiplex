"""
 Table headers definition
"""

def tableHeaders():
    """
    tableHeaders table model headers

    Returns:
        list: header definitions
    """

    data = [
        [
            "jobID",
            {
                "Type": "int",
                "CastFunction": int,
                "Label": " " + "ID" + "  ",
                "Alignment": "right",
                "Width": 80,
                "ToolTip": "Job identification number",
            },
        ],
        [
            "status",
            {
                "Type": "str",
                "CastFunction": str,
                "Label": "  " + "Status" + "  ",
                "Alignment": "center",
                "Width": 80,
                "ToolTip": "Application code for the job status",
            },
        ],
        [
            "command",
            {
                "Type": "str",
                "CastFunction": str,
                "Label": "Command",
                "Alignment": "center",
                "Width": 4096,
                "ToolTip": "Command generated for MKVMERGE by MKVToolNix",
            },
        ],
    ]

    return data

def tableHistoryHeaders():
    """
    tableHeaders table model headers

    Returns:
        list: header definitions
    """

    data = [
        [
            "jobID",
            {
                "Type": "int",
                "CastFunction": int,
                "Label": " " + "ID" + "  ",
                "Alignment": "right",
                "Width": 80,
                "ToolTip": "Job identification number",
            },
        ],
        [
            "date",
            {
                "Type": "str",
                "CastFunction": str,
                "Label": "  " + "Date" + "  ",
                "Alignment": "center",
                "Width": 80,
                "ToolTip": "Date of execution",
            },
        ],
        [
            "status",
            {
                "Type": "str",
                "CastFunction": str,
                "Label": "  " + "Status" + "  ",
                "Alignment": "center",
                "Width": 80,
                "ToolTip": "Application code for the job status",
            },
        ],
        [
            "command",
            {
                "Type": "str",
                "CastFunction": str,
                "Label": "Command",
                "Alignment": "center",
                "Width": 4096,
                "ToolTip": "Command generated for MKVMERGE by MKVToolNix",
            },
        ],
    ]

    return data
