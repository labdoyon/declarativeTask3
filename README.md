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

A phase typically has one associated script
e.g. example phase: src/ld_example.py

A subject must go through all phases for the experiment to be complete

# Installation
Preferably use python3.8.1, though the program should work with all python>3.6
sys.version_info(major=3, minor=8, micro=1, releaselevel='final', serial=0)
and <3.8.13
Install requirements with pip: <pip install -r requirements.txt>
Install the task with <pip install -e .> (from the task main directory)