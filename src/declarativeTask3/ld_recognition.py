import sys
import os

import numpy as np
from expyriment import control, stimuli, io, design, misc
from expyriment.misc._timer import get_time
from expyriment.misc import constants

from declarativeTask3.ld_matrix import LdMatrix
from declarativeTask3.ld_utils import setCursor, getPreviousMatrix, newRandomPresentation, readMouse, getPreviousSoundsAllocation
from declarativeTask3.ld_utils import getLanguage, normalize_presentation_order
from declarativeTask3.ld_utils import rename_output_files_to_BIDS
from declarativeTask3.ttl_catch_keyboard import wait_for_ttl_keyboard
from declarativeTask3.config import *
from declarativeTask3.ld_stimuli_names import classNames, ttl_instructions_text, ending_screen_text

from declarativeTask3.ld_sound import create_temp_sound_files, delete_temp_files

if not windowMode:  # Check WindowMode and Resolution
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

arguments = str(''.join(sys.argv[1:])).split(',')  # Get arguments - experiment name and subject
experimentName = arguments[0]
subjectName = arguments[1]

exp = design.Experiment(experimentName)  # Save experiment name

session = experiment_session[experimentName]
session_dir = os.path.normpath(os.path.join('sourcedata', 'sub-' + subjectName, 'ses-' + session))
output_dir = os.path.normpath(os.path.join(session_dir, 'beh'))
if not os.path.isdir(session_dir):
    os.mkdir(session_dir)
io.defaults.datafile_directory = output_dir
io.defaults.eventfile_directory = output_dir

exp.add_experiment_info('Subject: ')  # Save Subject Code
exp.add_experiment_info(subjectName)  # Save Subject Code
language = str(getLanguage(subjectName, 0, 'choose-language'))
exp.add_experiment_info('language: ')

# Save time, Response, correctAnswer, RT
exp.add_data_variable_names(['Time', 'Category', 'Matrix', 'CorrectAnswer', 'RT'])

learning_matrices = []
matrices = []
random_matrices = []
for i, category in enumerate(classPictures):
    learning_matrices.append(getPreviousMatrix(subjectName, 0, 'Encoding', i, category))
    matrices.append(LdMatrix(matrixSize, windowSize))  # Create Matrix
    matrices[i].associateCategory(category)

    exp.add_experiment_info('LearningMatrix_{}_category_{}: '.format(i, category))
    exp.add_experiment_info(str(learning_matrices[i]))
    exp.add_experiment_info('RandomMatrix_{}_category_{}: '.format(i, category))
    random_matrices.append(matrices[i].newRecognitionMatrix(learning_matrices[i], category))
    exp.add_experiment_info(str(random_matrices[i]))

soundsAllocation_index = getPreviousSoundsAllocation(subjectName, 0, 'choose-sound-association')
soundsAllocation = {key: sounds[soundsAllocation_index[key]] for key in soundsAllocation_index.keys()}

exp.add_experiment_info('Image classes order:')
exp.add_experiment_info(str(classPictures))
exp.add_experiment_info('Sounds order:')
exp.add_experiment_info(str(sounds))
exp.add_experiment_info('Image classes to sounds:')
exp.add_experiment_info(str(soundsAllocation))
exp.add_experiment_info('Image classes to sounds (index):')
exp.add_experiment_info(str(soundsAllocation_index))


soundsVolumeAdjustmentIndB = create_temp_sound_files(subjectName, io.defaults.datafile_directory)
exp.add_experiment_info('Sounds Volume adjustment (in dB):')
exp.add_experiment_info(str(soundsVolumeAdjustmentIndB))
if soundsVolumeAdjustmentIndB != [0] * len(sounds):
    volumeAdjusted = True
else:
    volumeAdjusted = False

# TODO: needs to differ from last matrix presentation order
matrices_to_present = np.array(range(len(classPictures)))
matrix_presentation_order = list(np.random.permutation(matrices_to_present))

exp.add_experiment_info(
            'MatrixPresentationOrder_{}'.format(matrix_presentation_order))  # Add sync info

control.initialize(exp)
control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

bids_datafile, bids_eventfile = rename_output_files_to_BIDS(subjectName, session, experimentName,
                                                            io.defaults.datafile_directory,
                                                            io.defaults.eventfile_directory)
exp.data.rename(bids_datafile)
exp.events.rename(bids_eventfile)

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor
setCursor(arrow)
bs = stimuli.BlankScreen(bgColor)  # Create blank screen
instructionRectangle = stimuli.Rectangle(size=(windowSize[0], matrices[0].gap * 2 + cardSize[1]), position=(
    0, -windowSize[1]/float(2) + (2 * matrices[0].gap + cardSize[1])/float(2)), colour=constants.C_DARKGREY)
instructions_ttl = stimuli.TextLine(ttl_instructions_text[language],
                                    position=(
                                        0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
                                    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                    text_underline=None, text_colour=textColor,
                                    background_colour=bgColor,
                                    max_width=None)
instructionRectangle.plot(bs)
instructions_ttl.plot(bs)
bs.present(False, True)

wait_for_ttl_keyboard()
exp.add_experiment_info(['TTL_RECEIVED_timing_{}'.format(exp.clock.time)])

for i in matrix_presentation_order:
    matrix_i = matrices[i]
    category = matrix_i._category

    presentationMatrixLearningOrder = newRandomPresentation()
    presentationMatrixLearningOrder = np.vstack((presentationMatrixLearningOrder, np.zeros(matrix_i.size[0]*matrix_i.size[1]-len(removeCards))))

    presentationMatrixRandomOrder = newRandomPresentation(presentationMatrixLearningOrder)
    presentationMatrixRandomOrder = np.vstack((presentationMatrixRandomOrder, np.ones(matrix_i.size[0]*matrix_i.size[1]-len(removeCards))))

    presentationOrder = np.hstack((presentationMatrixLearningOrder, presentationMatrixRandomOrder))

    presentationOrder = presentationOrder[:, np.random.permutation(presentationOrder.shape[1])]
    presentationOrder = normalize_presentation_order(presentationOrder,
                                                     learning_matrix=learning_matrices[i],
                                                     random_matrix=random_matrices[i])

    listCards = []
    for nCard in range(presentationOrder.shape[1]):
        if removeCards:
            removeCards.sort()
            removeCards = np.asarray(removeCards)
            tempPosition = presentationOrder[0][nCard]
            index = 0
            try:
                index = int(np.where(removeCards == max(removeCards[removeCards < tempPosition]))[0]) + 1
            except:
                pass

            position = tempPosition - index

        else:
            position = presentationOrder[0][nCard]

        if presentationOrder[1][nCard] == 0:  # Learning Matrix
            listCards.append(learning_matrices[i][int(position)])
        else:
            listCards.append(random_matrices[i][int(position)])

    instructions = stimuli.TextLine(' RECOGNITION ' + classNames[language][category] + ' ',
                                    position=(0, -windowSize[1] / float(2) +
                                              (2 * matrices[0].gap + cardSize[1]) / float(2)),
                                    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                    text_underline=None, text_colour=textColor,
                                    background_colour=bgColor,
                                    max_width=None)
    instructionRectangle.plot(bs)
    instructions.plot(bs)
    bs.present(False, True)

    exp.clock.wait(shortRest, process_control_events=True)
    instructionRectangle.plot(bs)
    bs.present(False, True)

    # LOG and SYNC
    exp.add_experiment_info(
        'Recognition_Test_matrix_{}_category_{}_timing_{}'.format(i, category, exp.clock.time))

    exp.add_experiment_info('matrix_{}_category_{}_Presentation Order: '.format(i, category))  # Save Presentation Order
    exp.add_experiment_info(str(list(presentationOrder)))  # Add listPictures

    matrixA = stimuli.TextLine('  Correct location  ',
                               position=(-windowSize[0]/float(4),
                                         -windowSize[1]/float(2) + (2*matrix_i.gap + cardSize[1])/float(2)),
                               text_size=textSize,
                               text_colour=textColor,
                               background_colour=cardColor)

    matrixARectangle = stimuli.Rectangle(size=matrixA.surface_size, position=matrixA.position,
                                         colour=cardColor)

    matrixNone = stimuli.TextLine('  Wrong location  ',
                                  position=(windowSize[0]/float(4),
                                          -windowSize[1]/float(2) + (2*matrix_i.gap + cardSize[1])/float(2)),
                                  text_size=textSize,
                                  text_colour=textColor,
                                  background_colour=cardColor)

    matrixNoneRectangle = stimuli.Rectangle(size=matrixNone.surface_size, position=matrixNone.position,
                                            colour=cardColor)


    bs = matrix_i.plotDefault(bs)  # Draw default grid
    matrixARectangle.plot(bs)
    matrixA.plot(bs)
    matrixNone.plot(bs)
    for j in range(len(classPictures)):
        matrix_i._cueCard[j].color = bgColor
        bs = matrix_i.plotCueCard(j, False, bs)

    bs.present(False, True)

    for nCard in range(presentationOrder.shape[1]):
        locationCard = int(presentationOrder[0][nCard])

        if bool(presentationOrder[1][nCard] == 0):
            showMatrix = 'MatrixA'
        else:
            showMatrix = 'MatrixRandom'

        matrix_i._matrix.item(locationCard).setPicture(os.path.join(picturesFolderClass[category], listCards[nCard]))
        picture = listCards[nCard].rstrip(".png")

        matrix_i.plotCard(locationCard, True, bs, True)

        exp.add_experiment_info(
            'ShowCard_pos_{}_card_{}_timing_{}_sound_{}'.format(locationCard,
                                                                listCards[nCard],exp.clock.time,
                                                                sounds[soundsAllocation_index[matrix_i._category]]))

        exp.clock.wait(presentationCard, process_control_events=True)
        matrix_i.plotCard(locationCard, False, bs, True)
        exp.add_experiment_info(['HideCard_pos_{}_card_{}_timing_{}'.format(locationCard,
                                                                            listCards[nCard],
                                                                            exp.clock.time)])  # Add sync info

        time_left = responseTime
        valid_response = False
        rt = 0
        while not valid_response and rt is not None:
            mouse.show_cursor(True, True)

            start = get_time()
            rt, position = readMouse(start, mouseButton, time_left)  # time_left instead of response tine

            mouse.hide_cursor(True, True)

            if rt is not None:
                if matrixARectangle.overlapping_with_position(position):
                    valid_response = True
                    exp.data.add([exp.clock.time, category, showMatrix, bool(presentationOrder[1][nCard] == 0), rt])
                    matrixA = stimuli.TextLine('  Correct location  ',
                                               position=(-windowSize[0]/float(4),
                                                         -windowSize[1]/float(2) + (2*matrix_i.gap + cardSize[1])/float(2)),
                                               text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                               text_underline=None, text_colour=textColor,
                                               background_colour=clickColor,
                                               max_width=None)
                    matrixA.plot(bs)
                    bs.present(False, True)
                    exp.clock.wait(clicPeriod, process_control_events=True)
                    matrixA = stimuli.TextLine('  Correct location  ',
                                              position=(-windowSize[0]/float(4),
                                                        -windowSize[1]/float(2) + (2*matrix_i.gap + cardSize[1])/float(2)),
                                              text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                              text_underline=None, text_colour=textColor,
                                              background_colour=cardColor,
                                              max_width=None)
                    matrixA.plot(bs)
                    bs.present(False, True)
                    exp.add_experiment_info(['Response_{}_timing_{}'.format('MatrixA', exp.clock.time)])  # Add sync info

                elif matrixNoneRectangle.overlapping_with_position(position):
                    valid_response = True
                    exp.data.add([exp.clock.time, category, showMatrix, bool(presentationOrder[1][nCard] == 1), rt])
                    matrixNone = stimuli.TextLine('  Wrong location  ',
                                                  position=(windowSize[0]/float(4),
                                                            -windowSize[1]/float(2) + (2*matrix_i.gap + cardSize[1])/float(2)),
                                                  text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                                  text_underline=None, text_colour=textColor,
                                                  background_colour=clickColor,
                                                  max_width=None)
                    matrixNone.plot(bs)
                    bs.present(False, True)
                    exp.clock.wait(clicPeriod, process_control_events=True)
                    matrixNone = stimuli.TextLine('  Wrong location  ',
                                                  position=(windowSize[0]/float(4),
                                                            -windowSize[1]/float(2) + (2*matrix_i.gap + cardSize[1])/float(2)),
                                                  text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                                  text_underline=None, text_colour=textColor,
                                                  background_colour=cardColor,
                                                  max_width=None)
                    matrixNone.plot(bs)
                    bs.present(False, True)
                    exp.add_experiment_info(['Response_{}_timing_{}'.format('None', exp.clock.time)])  # Add sync info

                else:
                    exp.data.add([exp.clock.time, category, showMatrix, False, rt])
                    exp.add_experiment_info(['Response_{}_timing_{}'.format('NoRT', exp.clock.time)])  # Add sync info
            else:
                exp.data.add([exp.clock.time, category, showMatrix, False, rt])
            if rt is not None:
                if rt < time_left - clicPeriod:
                    time_left = time_left - clicPeriod - rt
                else:
                    break

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI, process_control_events=True)

instructions = stimuli.TextLine(
    ending_screen_text[language],
    position=(0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
    text_underline=None, text_colour=textColor, background_colour=bgColor,
    max_width=None)

instructions.plot(bs)
bs.present(False, True)
exp.clock.wait(thankYouRest, process_control_events=True)
instructionRectangle.plot(bs)
bs.present(False, True)

delete_temp_files()
