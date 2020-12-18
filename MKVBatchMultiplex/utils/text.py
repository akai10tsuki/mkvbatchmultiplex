"""
Text strings used in the application
"""

# 90001 - Overflow


class Text:  # pylint: disable=too-few-public-methods
    """
    Text strings used in the application
    """

    S_ = lambda s: s

    n = 0

    txt0001 = S_("MKVMERGE: Batch Multiplex")
    txt0002 = S_("Author")
    txt0003 = S_("email")
    txt0004 = S_("Python Version")

    # 20
    txt0020 = S_("&File")
    txt0021 = S_("&Exit")
    txt0022 = S_("Ctrl+E")
    txt0023 = S_("Exit Application")
    txt0024 = S_("Abort")
    txt0025 = S_("Force exit")


    # 40
    txt0040 = S_("&Settings")
    txt0041 = S_("Enable logging")
    txt0042 = S_("Enable session logging in {}")
    txt0043 = S_("Font && size")
    txt0044 = S_("Select font & size")

    txt0045 = S_("&Interface language")

    txt0046 = S_("Restore defaults")
    txt0047 = S_("Restore settings for font, window size and position")

    #50
    txt0050 = S_("&Preferences")
    txt0051 = S_("Setup program options")


    # 60
    txt0060 = S_("&Help")
    txt0061 = S_("Contents")
    txt0062 = S_("Using")
    txt0063 = S_("About")
    txt0064 = S_("About QT")

    # Dialogs & others
    # 80
    txt0080 = S_("Close App")
    txt0081 = S_("Are you sure you want to exit")
    txt0082 = S_("Yes")

    txt0083 = S_("Confirm restore ...")
    txt0084 = S_("Restore default settings")

    txt0085 = S_("Jobs: {0:3d} - Current: {1:3d} - File: {2:3d} of {3:3d} - Errors: {4:3d}")
    txt0086 = S_("Job identification number")
    txt0087 = S_("Application code for the job status")
    txt0088 = S_("Command generated for MKVMERGE by MKVToolNix")
    txt0089 = S_("Jobs are still running")
    txt0090 = S_("Exit")
    txt0091 = S_("Progress")

    # JobTableWidgets
    # 120
    txt0120 = S_("Populate")
    txt0121 = S_("Add test jobs to table")
    txt0122 = S_("Queue Waiting Jobs")
    txt0123 = S_("Add all Waiting jobs to the Queue")
    txt0124 = S_("Clear Queue")
    txt0125 = S_("Remove jobs from Queue")
    txt0126 = S_("Start Worker")
    txt0127 = S_("Start processing jobs on Queue")
    txt0128 = S_("Debug")
    txt0129 = S_("Print current dataset to console")
    txt0130 = S_("Jobs Table")
    txt0131 = S_("ID")
    txt0132 = S_("Status")
    txt0133 = S_("Command")
    txt0134 = S_("Abort Running Job")
    txt0135 = S_("Abort running job and continue with next in Queue")
    txt0136 = S_("Abort Jobs")
    txt0137 = S_("Abort running job and put jobs in Queue in Waiting status")
    txt0138 = S_("Remove Job")
    txt0139 = S_("Remove job from list")
    txt9000 = S_("Remove selected jobs")
    txt9001 = S_("Copy")
    txt9002 = S_("Remove")
    txt9003 = S_("Delete")
    txt9004 = S_("Save")

    # TabsWidget
    # 140
    txt0140 = S_("Jobs")
    txt0141 = S_("Jobs Output")
    txt0142 = S_("Jobs Errors")
    txt0143 = S_("Rename Files")

    txt0144 = S_("Jobs table to manipulate job status and Queue")
    txt0145 = S_("Output generated by jobs and job handling",)
    txt0146 = S_("Errors generated by processing or running of jobs")
    txt0147 = S_("Rename the output files ej. Series Name - S01E01.mkv, ...")
    txt0148 = S_("Enter generated command and see any test output")

    txt0149 = S_("Log Viewer")
    txt0150 = S_("Display log entries")
    txt0151 = S_("Messages registered in current running log")

    # CommandWidget
    # 160
    txt0160 = S_("Add Command")
    txt0161 = S_("Add command to jobs table with Waiting status")
    txt0162 = S_("Clear Output")
    txt0163 = S_("Erase text in output window")
    txt0164 = S_("Paste")
    txt0165 = S_("Paste Clipboard contents in command line")
    txt0166 = S_("Add Queue")
    txt0167 = S_("Add command to jobs table and put on Queue")
    # txt0168 = S_()
    txt0169 = S_("Start processing jobs on Queue")
    txt0170 = S_("Analysis")
    txt0171 = S_("Print analysis of command line")
    txt0172 = S_("Commands")
    txt0173 = S_("Commands to be applied")
    txt0174 = S_("Check Files")
    txt0175 = S_("Check files for consistency")
    txt0176 = S_("Clear Output")
    txt0177 = S_("Erase text in output window")
    txt0178 = S_("Reset")
    txt0179 = S_("Reset state completely to work with another batch")
    txt0180 = S_("Clear output")
    txt0181 = S_("Clear output window")
    txt0182 = S_("Rename")
    txt0183 = S_("Rename output files")

    # RenameWidget
    # 200
    txt0200 = S_("Regular Expression")
    txt0201 = S_("Enter regular expression")
    txt0202 = S_("Substitution String")
    txt0203 = S_("Enter substitution string")
    txt0204 = S_("Original names")
    txt0205 = S_("Name generated base on parsed command")
    txt0206 = S_("Rename to")
    txt0207 = S_("Names that will be used for commands")
    txt0208 = S_("Apply Rename")
    txt0209 = S_("Replace the original names with the operation result")

    txt0210 = S_("Undo")
    txt0211 = S_("Undo rename operation")
    txt0212 = S_("Clear")
    txt0213 = S_("Clear names start over")
    txt0214 = S_("Invalid regex")


    # JobHistoryWidget
    # 240
    txt0240 = S_("Date")
    txt0241 = S_("Saved Jobs")
    txt0242 = S_("Fetch Jobs")
    txt0249 = S_("Jobs History")
    txt0250 = S_("Fetch History")
    txt0243 = S_("Search")
    txt0244 = S_("Show Output")
    txt0245 = S_("Show Errors")
    txt0246 = S_("Print")
    txt0247 = S_("Select All")
    txt0248 = S_("Clear Selection")


    """
    txt0169 = S_()
    txt0169 = S_()
    txt0169 = S_()
    txt0169 = S_()
    txt0169 = S_()
    txt0169 = S_()
    txt0169 = S_()
    txt0169 = S_()
    txt0169 = S_()
    txt0169 = S_()
    txt0169 = S_()
    txt0169 = S_()
    """
