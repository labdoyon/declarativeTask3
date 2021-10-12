import ast
import ntpath
from os.path import join
import os
import random

import pandas as pd
import pygame
from datetime import datetime
from time import time
from ast import literal_eval

import numpy as np
from dateutil.parser import parse
from expyriment import misc, stimuli
from expyriment.io import Keyboard
from expyriment.misc._timer import get_time
from expyriment.misc.geometry import coordinates2position

from declarativeTask3.config import linesThickness, cardSize, colorLine, windowSize, bgColor, matrixSize, removeCards
from declarativeTask3.config import classPictures, sounds, ignore_one_learned_matrices, sessions, rawFolder


def checkWindowParameters(iWindowSize):
    result = False

    originalResolution = misc.get_monitor_resolution()

    if iWindowSize[0] <= originalResolution[0] and iWindowSize[1] <= originalResolution[1]:
        result = True

    return result


def drawLines(windowSize, gap, bs):

    linesPositions = np.empty([2,2], object)
    linesPositions[0,0] = (-windowSize[0]/float(2), windowSize[1]/float(2) - 2 * gap - cardSize[0] - linesThickness / float(2))
    linesPositions[0,1] = (windowSize[0]/float(2), windowSize[1]/float(2) - 2 * gap - cardSize[0] - linesThickness / float(2))
    linesPositions[1,0] = (-windowSize[0]/float(2), -windowSize[1]/float(2) + 2 * gap + cardSize[1] + linesThickness / float(2))
    linesPositions[1,1] = (windowSize[0]/float(2), -windowSize[1]/float(2) + 2 * gap + cardSize[1] + linesThickness / float(2))

    lines = np.empty([2], object)
    lines[0] = stimuli.Line(linesPositions[0,0], linesPositions[0,1], linesThickness, colour=colorLine, anti_aliasing=None)
    lines[1] = stimuli.Line(linesPositions[1,0], linesPositions[1,1], linesThickness, colour=colorLine, anti_aliasing=None)

    for line in lines:
        line.plot(bs)

    bs.present()


def plotLine(bs, gap, color=bgColor):
    linePositions = np.empty([2], object)
    linePositions[0] = (-cardSize[0]/float(2), windowSize[1]/float(2) - 2*gap - cardSize[0] - linesThickness/float(2))
    linePositions[1] = (cardSize[0]/float(2), windowSize[1]/float(2) - 2*gap - cardSize[0] - linesThickness/float(2))

    line = stimuli.Line(linePositions[0], linePositions[1], linesThickness, colour=color)
    line.plot(bs)

    return bs


def newRandomPresentation(oldPresentation=None):

    newPresentation = np.array(range(matrixSize[0]*matrixSize[1]))
    if removeCards:
        removeCards.sort(reverse=True)
        for nCard in removeCards:
            newPresentation = np.delete(newPresentation, nCard)

    newPresentation = np.random.permutation(newPresentation)

    if oldPresentation is not None:

        while len(longestSubstringFinder(str(oldPresentation), str(newPresentation)).split()) > 2:
            newPresentation = np.array(range(matrixSize[0]*matrixSize[1]))

            if removeCards:
                removeCards.sort(reverse=True)
                for nCard in removeCards:
                    newPresentation = np.delete(newPresentation, nCard)

            newPresentation = np.random.permutation(newPresentation)

    return newPresentation


def longestSubstringFinder(string1, string2):
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): answer = match
                match = ""
    return answer


def getPreviousMatrix(subjectName, daysBefore, experienceName, matrix_index, matrix_category):

    currentDate = datetime.now()

    subject_dir = join(rawFolder, 'sourcedata', 'sub-' + subjectName)
    data_files = []

    for session in sessions:
        session_dir = join(subject_dir, 'ses-' + session, 'beh')
        if os.path.isdir(session_dir):
            data_files = data_files + \
                         [join(session_dir, file) for file in os.listdir(session_dir) if file.endswith('_beh.xpd') and
                          'task-' + experienceName in file]

    data_files.sort(reverse=True)  # latest runs first
    for dataFile in data_files:
        try:
            agg = misc.data_preprocessing.read_datafile(dataFile, only_header_and_variable_names=True)
        except TypeError:
            continue
        previousDate = parse(agg[2]['date'])

        try:
            agg[3].index(experienceName)
        except (ValueError):
            continue

        if daysBefore == 0 or ((currentDate-previousDate).total_seconds() > 72000*daysBefore and (currentDate-previousDate).total_seconds() < 100800*daysBefore):
            header = agg[3].split('\n#e ')

            indexSubjectName = header.index('Subject:') + 1
            if subjectName in header[indexSubjectName]:
                print('File found: ' + dataFile)
                indexPositions = header.index('matrix {}, pictures from class {}:'.format(matrix_index,
                                                                                          matrix_category)) + 1
                previousMatrix = ast.literal_eval(header[indexPositions].split('\n')[0].split('\n')[0])
                return previousMatrix

    return None


def newSoundAllocation():
    # Random permutation to assign sounds to picture classes
    soundToClasses = {}
    soundToClasses_index = {}
    sounds_index = list(range(len(classPictures)))
    for category in classPictures:
        soundToClasses_index[category] = np.random.choice(sounds_index)
        soundToClasses[category] = sounds[soundToClasses_index[category]]
        sounds_index.remove(soundToClasses_index[category])

    return soundToClasses_index, soundToClasses


def getPreviousSoundsAllocation(subjectName, daysBefore, experienceName):
    # Duplicate of get previous matrix but for sounds
    currentDate = datetime.now()

    subject_dir = join(rawFolder, 'sourcedata', 'sub-' + subjectName)
    data_files = []
    for session in sessions:
        session_dir = join(subject_dir, 'ses-' + session, 'beh')
        if os.path.isdir(session_dir):
            data_files = data_files + \
                         [join(session_dir, file) for file in os.listdir(session_dir) if file.endswith('_beh.xpd') and
                          'task-' + experienceName in file]

    data_files.sort(reverse=True)  # latest runs first
    for dataFile in data_files:
        try:
            agg = misc.data_preprocessing.read_datafile(dataFile, only_header_and_variable_names=True)
        except TypeError:
            continue
        previousDate = parse(agg[2]['date'])

        try:
            agg[3].index(experienceName)
        except (ValueError):
            continue

        if daysBefore == 0 or ((currentDate-previousDate).total_seconds() > 72000*daysBefore and (currentDate-previousDate).total_seconds() < 100800*daysBefore):
            header = agg[3].split('\n#e ')

            indexSubjectName = header.index('Subject:') + 1
            if subjectName in header[indexSubjectName]:
                print('File found: ' + dataFile)
                indexPositions = header.index('Image classes to sounds (index):') + 1
                sound_allocation = ast.literal_eval(header[indexPositions].split('\n')[0].split('\n')[0])
                return sound_allocation

    return None


def getPrevious(subjectName, daysBefore, experienceName, target):
    currentDate = datetime.now()

    subject_dir = join(rawFolder, 'sourcedata', 'sub-' + subjectName)
    data_files = []
    for session in sessions:
        session_dir = join(subject_dir, 'ses-' + session, 'beh')
        if os.path.isdir(session_dir):
            data_files = data_files + \
                         [join(session_dir, file) for file in os.listdir(session_dir) if file.endswith('_beh.xpd') and
                          'task-' + experienceName in file]

    data_files.sort(reverse=True)  # latest runs first
    for dataFile in data_files:
        agg = misc.data_preprocessing.read_datafile(dataFile, only_header_and_variable_names=True)
        previousDate = parse(agg[2]['date'])

        try:
            agg[3].index(experienceName)
        except ValueError:
            continue
        if daysBefore == 0 or ((currentDate-previousDate).total_seconds() > 72000*daysBefore and (currentDate-previousDate).total_seconds() < 100800*daysBefore):
            header = agg[3].split('\n#e ')

            indexSubjectName = header.index('Subject:') + 1
            if subjectName in header[indexSubjectName]:
                print('File found: ' + dataFile)
                indexPositions = header.index(target) + 1
                previousTarget = header[indexPositions].split('\n')[0].split('\n')[0]
                try:  # dictionary or list
                    output = literal_eval(previousTarget)
                except (SyntaxError, ValueError):  # string
                    output = previousTarget
                return output

    return None


def getLanguage(subjectName, daysBefore, experienceName):
    currentDate = datetime.now()

    subject_dir = join(rawFolder, 'sourcedata', 'sub-' + subjectName)
    data_files = []
    for session in sessions:
        session_dir = join(subject_dir, 'ses-' + session, 'beh')
        if os.path.isdir(session_dir):
            data_files = data_files + \
                         [join(session_dir, file) for file in os.listdir(session_dir) if file.endswith('_beh.xpd') and
                          'task-' + experienceName in file]

    data_files.sort(reverse=True)  # latest runs first
    for dataFile in data_files:
        try:
            agg = misc.data_preprocessing.read_datafile(dataFile, only_header_and_variable_names=True)
        except TypeError:
            continue
        previousDate = parse(agg[2]['date'])

        try:
            agg[3].index(experienceName)
        except ValueError:
            continue
        if daysBefore == 0 or ((currentDate-previousDate).total_seconds() > 72000*daysBefore and (currentDate-previousDate).total_seconds() < 100800*daysBefore):
            header = agg[3].split('\n#e ')

            indexSubjectName = header.index('Subject:') + 1
            if subjectName in header[indexSubjectName]:
                print('File found: ' + dataFile)
                indexPositions = header.index('language:') + 1
                language = header[indexPositions].split('\n')[0].split('\n')[0]
                return language

    return None


def normalize_presentation_order(presentation_order, learning_matrix, random_matrix):
    positions = [int(i) for i in presentation_order[0]]
    matrix_a_or_rec = [int(i) for i in presentation_order[1]]
    images = [random_matrix[position] if matrix_a_or_rec[index] else learning_matrix[position]
              for index, position in enumerate(positions)]

    while any([positions[i] == positions[i+1] for i in range(len(positions)-1)]) or \
            any([images[i] == images[i+1] for i in range(len(positions)-1)]):
        zipped_lists = list(zip(positions, matrix_a_or_rec, images))
        random.shuffle(zipped_lists)

        positions, matrix_a_or_rec, images = zip(*zipped_lists)
        positions, matrix_a_or_rec, images = list(positions), list(matrix_a_or_rec), list(images)

    new_presentation_order = np.array([np.array(positions), np.array(matrix_a_or_rec)])

    return new_presentation_order


def normalize_test_presentation_order(trials_order, pictures_allocation):
    positions = []
    for card in trials_order:
        category = card[0]
        matrix_index = classPictures.index(category)
        positions.append(pictures_allocation[matrix_index].index(card))

    trial_category = {}
    trial_category_longest_sequence = {element: 3 for element in classPictures}

    while any([positions[i] == positions[i + 1] for i in range(len(positions) - 1)]) or \
            any(value > 2 for value in trial_category_longest_sequence.values()):
        zipped_lists = list(zip(positions, trials_order))
        random.shuffle(zipped_lists)

        positions, trials_order = zip(*zipped_lists)
        positions, trials_order = list(positions), list(trials_order)

        for category_j in classPictures:
            # counting longest uninterrupted sequence of trials of the same category
            trial_category[category_j] = pd.Series([trial[0] == category_j for trial in trials_order], dtype=bool)
            trial_category_longest_sequence[category_j] = (~trial_category[category_j]).cumsum()[
                trial_category[category_j]].value_counts().max()

    return trials_order


def subfinder(mylist, pattern):
    answers = []
    for i in range(len(mylist) - len(pattern)+1):
        if np.all(mylist[i:i+len(pattern)] == pattern):
            answers.append(True)
        else:
            answers.append(False)

    try:
        answers.index(True)
    except ValueError:
        return False

    return True


def setCursor(arrow):
    hotspot = (0, 0)
    s2 = []
    for line in arrow:
        s2.append(line.replace('x', 'X').replace(',', '.').replace('O', 'o'))
    cursor, mask = pygame.cursors.compile(s2, 'X', '.', 'o')
    size = len(arrow[0]), len(arrow)
    pygame.mouse.set_cursor(size, hotspot, cursor, mask)


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def readMouse(startTime, button, duration=None):
    iKeyboard = Keyboard()
    if duration is not None:
        while int((get_time() - startTime) * 1000) <= duration:
            alle = pygame.event.get()
            rt = int((get_time() - startTime)*1000)
            for e in alle:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == button:
                    return rt, coordinates2position(e.pos)

            if iKeyboard.process_control_keys():
                break

        return None, None

    else:
        while True:
            alle = pygame.event.get()
            rt = int((get_time() - startTime)*1000)
            for e in alle:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == button:
                    return rt, coordinates2position(e.pos)

            if iKeyboard.process_control_keys():
                break
    #
    # if nBlock < 0:  # if nBlock == 0:
    #
    #     ''' Presentation all locations + memorization'''
    #
    #     list = np.random.permutation(m.size[0] * m.size[1])
    #     list = list.tolist()
    #     list.remove((m.size[0]*m.size[1])/2)
    #
    #     for nCard in list:
    #         isLearned = False
    #
    #         while not isLearned:
    #             mouse.hide_cursor(True, True)
    #             bs = m.plotCard(nCard,True,bs)  # Show Location for ( 2s )
    #             bs.present(False, True)
    #             exp.clock.wait(presentationCard)
    #
    #             bs = m.plotCard(nCard, False, bs)  # Hide Location
    #             m._cueCard.setPicture(m._matrix.item(nCard).stimuli[0].filename)
    #             bs = m.plotCueCard(True, bs)  # Show Cue
    #             bs.present(False, True)  # Update Screen
    #
    #             exp.clock.wait(presentationCard)  # Wait
    #
    #             bs = m.plotCueCard(False, bs)  # Hide Cue
    #             bs.present(False, True)  # Update Screen
    #             mouse.show_cursor(True, True)  # Show cursor
    #
    #             position = None
    #             [event_id, position, rt] = mouse.wait_press(buttons=None, duration=responseTime, wait_for_buttonup=True)
    #
    #             if position is not None:
    #                 if m.checkPosition(position) == nCard:
    #                     mouse.hide_cursor(True, True)
    #                     isLearned = True
    #
    #             ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    #             exp.clock.wait(ISI)


def newSoundAllocation():
    # Random permutation to assign sounds to picture classes
    soundToClasses = {}
    soundToClasses_index = {}
    sounds_index = list(range(len(classPictures)))
    for category in classPictures:
        soundToClasses_index[category] = np.random.choice(sounds_index)
        soundToClasses[category] = sounds[soundToClasses_index[category]]
        sounds_index.remove(soundToClasses_index[category])

    return soundToClasses_index, soundToClasses


def absoluteTime(firstTime):
    return int((time()*1000))-firstTime


def generate_bids_filename(subject_id, session, task, filename_suffix='_beh', filename_extension='.xpd',
                           run=None):
    if run is None:
        return 'sub-' + subject_id + '_ses-' + session + '_task-' + task + filename_suffix + filename_extension
    else:
        return 'sub-' + subject_id + '_ses-' + session + '_task-' + task +\
               '_run-' + str(run) +\
               filename_suffix + filename_extension


def rename_output_files_to_BIDS(subject_name, session, experiment_name,
                                datafile_dir, eventfile_dir):
    i = 1
    wouldbe_datafile = generate_bids_filename(
        subject_name, session, experiment_name, filename_suffix='_beh', filename_extension='.xpd')
    wouldbe_eventfile = generate_bids_filename(
        subject_name, session, experiment_name, filename_suffix='_events', filename_extension='.xpe')

    while os.path.isfile(join(datafile_dir, wouldbe_datafile)) or \
            os.path.isfile(join(eventfile_dir, wouldbe_eventfile)):
        i += 1
        i_string = '0' * (2 - len(str(i))) + str(i)  # 0 padding, assuming 2-digits number
        wouldbe_datafile = generate_bids_filename(subject_name, session, experiment_name, filename_suffix='_beh',
                                                  filename_extension='.xpd', run=i_string)
        wouldbe_eventfile = generate_bids_filename(subject_name, session, experiment_name, filename_suffix='_events',
                                                   filename_extension='.xpe', run=i_string)

    return wouldbe_datafile, wouldbe_eventfile
