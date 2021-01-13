"""
 Table headers definition
"""

from ..utils import Text

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
                "Label": " " + _(Text.txt0131) + "  ",
                "Alignment": "right",
                "Width": 80,
                "ToolTip": _(Text.txt0086),
            },
        ],
        [
            "status",
            {
                "Type": "str",
                "CastFunction": str,
                "Label": "  " + _(Text.txt0132) + "  ",
                "Alignment": "center",
                "Width": 80,
                "ToolTip": _(Text.txt0087),
            },
        ],
        [
            "command",
            {
                "Type": "str",
                "CastFunction": str,
                "Label": _(Text.txt0133),
                "Alignment": "center",
                "Width": 4096,
                "ToolTip": _(Text.txt0088),
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
                "Label": " " + _(Text.txt0131) + "  ",
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
                "Label": "  " + _(Text.txt0240) + "  ",
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
                "Label": "  " + _(Text.txt0132) + "  ",
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
                "Label": _(Text.txt0133),
                "Alignment": "center",
                "Width": 4096,
                "ToolTip": "Command generated for MKVMERGE by MKVToolNix",
            },
        ],
    ]

    return data
