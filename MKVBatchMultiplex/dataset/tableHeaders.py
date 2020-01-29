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
                "Label": "       " + "Status" + "       ",
                "Alignment": "center",
                "Width": 220,
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
