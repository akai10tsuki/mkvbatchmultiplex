
***************
Getting Started
***************

Using **MKVToolNix** do any needed operations on the first media file in the
source directory. When done copy the resulting command line to the clipboard:

    *Multiplexer->Show command line*


.. figure:: images/MKVToolNix-copytoclipboard.png
    :align: center

    Copy to clipboard

Open mkvbatchmultiplex and paste command using the **<Paste>**
button:

.. figure:: images/mkvbatchmultiplex-command.png
    :align: center

    Copy from clipboard

Now there are two options **<Add Command>** button will add the job to the Jobs
Table with a 'Waiting' status. The **<Add Queue>** button will add the command
to the job Queue.  When finished adding jobs to the Queue push
**<Start Worker>** to start the Queue worker and run the jobs.  Any job added
with the 'Waiting' status have to be added to the Queue in the Jobs tab in
order to run the job.  If the Queue worker is running jobs added to the Queue
will be processed in the order entered.
