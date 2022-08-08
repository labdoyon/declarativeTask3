# declarative task 3
Current developer and curator: thibault.vlieghe@mcgill.ca
Original author: arnaud.bore@gmail.com

# Description
this experiment is made of 8 phases
1. Example
2. StimuliPresentation
3. PreLearning
(Optional) soundVolumeAdjustment
4. Learning
5. TestMatrixA
6. ConsolidationMatrixA
7. Recognition
8. Association

#
Please mind the 265 characters path limit size in Windows

# Documentation
this task was built using Expyriment 0.10.0, a python library for neuroimaging experiments. More details on this library can be found at: https://docs.expyriment.org/

# DEBUGGING
if the program crashes, the information on the error can be found in the .xpe file in sourcedata/sub-<subject-id>/ses-<ses-id>/<task-filename>.xpe

You can also debug faster via command line as follows:
go to ld_runExperimentDayOne.py
take a menu element (say Example, `CommandItem(text='Example'`
e.g. for example in the HBHL task:
py .\src\declarativeTask3\ld_example.py "Example,<subject_id>>"
take the 'command' and 'arguments' element of the menu element
e.g.
command=python + " " + os.path.join("src", "declarativeTask3", "ld_example.py"),
    arguments='ses-ExpD1_task-Example,' + sys.argv[1]

You may now run the following in the command line, to run this step of the experiment without the menu provided in ld_runExperimentDayOne.py
py src\declarativeTask3\ld_example.py 'ses-ExpD1_task-Example,<subject_id>'
You will see any error the program generates much faster

A phase typically has one associated script
e.g. example phase: src/ld_example.py

A subject must go through all phases for the experiment to be complete

# Installation
Preferably use python3.8.1, though the program should work with all python>3.6
sys.version_info(major=3, minor=8, micro=1, releaselevel='final', serial=0)
install requirements with pip: <pip install -r requirements.txt>
Install the task with: <pip install -r requirements.txt>