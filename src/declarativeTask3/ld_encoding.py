import sys
import random
import os
import pickle
import subprocess

import numpy as np
import pandas as pd
from expyriment import control, stimuli, io, design, misc
from expyriment.misc import constants
from expyriment.misc._timer import get_time

from declarativeTask3.ld_matrix import LdMatrix
from declarativeTask3.ld_utils import getPreviousSoundsAllocation, normalize_test_presentation_order
from declarativeTask3.ld_utils import setCursor, newRandomPresentation, getPreviousMatrix, getLanguage, path_leaf, readMouse
from declarativeTask3.ld_utils import rename_output_files_to_BIDS, generate_bids_filename
from declarativeTask3.ld_sound import create_temp_sound_files, delete_temp_files
from declarativeTask3.config import *
from declarativeTask3.ttl_catch_keyboard import wait_for_ttl_keyboard
from declarativeTask3.ld_stimuli_names import classNames, ttl_instructions_text, presentation_screen_text, rest_screen_text, \
    ending_screen_text, choose_image_text, choose_position_text, feedback_message

if not windowMode:  # Check WindowMode and Resolution
    control.defaults.window_mode = windowMode
    control.defaults.window_size = misc.get_monitor_resolution()
    windowSize = control.defaults.window_size
else:
    control.defaults.window_mode = windowMode
    control.defaults.window_size = windowSize

if debug:
    control.set_develop_mode(on=True, intensive_logging=False, skip_wait_methods=False)

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

exp.add_experiment_info('Subject: ')
exp.add_experiment_info(subjectName)
language = str(getLanguage(subjectName, 0, 'choose-language'))
exp.add_experiment_info('language: ')
exp.add_experiment_info(language)  # Save Subject Code

# Save time, nblocks, position, correctAnswer, RT
exp.add_data_variable_names(['Time', 'NBlock', 'Picture', 'Answers', 'RT'])

keepMatrix = True
if experimentName == 'Encoding':
    no_feedback = False
    cuecard_response_logging_text = 'CorrectCueCardResponse'
elif experimentName == 'Test-Encoding':
    nbBlocksMax = 1
    no_feedback = True
    cuecard_response_logging_text = 'CueCardResponse'
elif experimentName == 'ReTest-Encoding':
    nbBlocksMax = 1
    no_feedback = True
    cuecard_response_logging_text = 'CueCardResponse'

exp.add_experiment_info('Image categories (original order; src/config.py order): ')
exp.add_experiment_info(str(classPictures))

matrices = []
pictures_allocation = []
if ignore_one_learned_matrices:
    index_matrix_not_to_present_again = None
for i, category in enumerate(classPictures):
    previousMatrix = getPreviousMatrix(subjectName, 0, 'Encoding', i, category)
    # previousMatrix will be <None> if there is no previous matrix, the findMatrix function will generate a new matrix
    # if it is fed <None> as previousMatrix
    matrices.append(LdMatrix(matrixSize, windowSize))  # Create matrices
    pictures_allocation.append(matrices[i].findMatrix(category, previousMatrix=previousMatrix, keep=True))
    # Find pictures_allocation
    matrices[i].associateCategory(category)

# generating trials for test-encoding and retest-encoding
if experimentName == 'Encoding':
    with open(os.path.join(io.defaults.datafile_directory, 'matrices.pkl'), 'wb') as f:
        pickle.dump(pictures_allocation, f)
    subprocess.Popen(
        [sys.executable, os.path.join(rawFolder, "src", "declarativeTask3", "generate_test_retest_trials_order.py"),
         subjectName])

control.initialize(exp)

for i, category in enumerate(classPictures):
    matrices[i].associatePictures(pictures_allocation[i])  # Associate Pictures to cards
    exp.add_experiment_info('matrix {}, pictures from class {}:'.format(i, category))
    exp.add_experiment_info(str(matrices[i].listPictures))  # Add listPictures

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

control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)

bids_datafile, bids_eventfile = rename_output_files_to_BIDS(subjectName, session, experimentName,
                                                            io.defaults.datafile_directory,
                                                            io.defaults.eventfile_directory)
exp.data.rename(bids_datafile)
exp.events.rename(bids_eventfile)

exp.add_experiment_info(['StartExp: {}'.format(exp.clock.time)])  # Add sync info

mouse = io.Mouse()  # Create Mouse instance
mouse.set_logging(True)  # Log mouse
mouse.hide_cursor(True, True)  # Hide cursor

setCursor(arrow)

bs = stimuli.BlankScreen(bgColor)  # Create blank screen

exp.clock.wait(shortRest, process_control_events=True)

correctAnswers = np.zeros((len(classPictures), nbBlocksMax))
currentCorrectAnswers = correctAnswers[0:len(classPictures), 0]
nBlock = 0

instructionRectangle = stimuli.Rectangle(size=(windowSize[0], matrices[0].gap * 2 + cardSize[1]), position=(
    0, -windowSize[1]/float(2) + (2 * matrices[0].gap + cardSize[1])/float(2)), colour=constants.C_DARKGREY)

''' Presentation all locations '''
presentationOrder = newRandomPresentation()

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

instructionRectangle.plot(bs)
bs.present(False, True)

new_matrix_presentation_order = None
learning_matrix_presentation_order = None
matrices_to_present = np.array(range(len(classPictures)))
# if experimentName == 'Encoding':
#     test_matrix_presentation_order = None
# elif experimentName == 'Test-Encoding':
#     test_matrix_presentation_order = getPreviousMatrixOrder(subjectName, 0, 'Encoding')
# elif experimentName == 'ReTest-Encoding':
#     test_matrix_presentation_order = getPreviousMatrixOrder(subjectName, 0, 'Test-Encoding')

while [score >= correctAnswersMax for score in currentCorrectAnswers].count(True) < min_number_learned_matrices \
        and nBlock < nbBlocksMax:

    # PRESENTATION BLOCK
    if 1 != nbBlocksMax or experimentName == 'Encoding':
        exp.add_experiment_info('Presentation_Block_{}_timing_{}'.format(nBlock, exp.clock.time))

        if len(matrices_to_present) > 2:
            while new_matrix_presentation_order == learning_matrix_presentation_order:
                new_matrix_presentation_order = list(np.random.permutation(matrices_to_present))
        else:
            new_matrix_presentation_order = list(np.random.permutation(matrices_to_present))
        learning_matrix_presentation_order = new_matrix_presentation_order
        exp.add_experiment_info(
            'Presentation_Block_{}_MatrixPresentationOrder_{}_timing_{}'.format(nBlock,
                                                                                learning_matrix_presentation_order,
                                                                                exp.clock.time))  # Add sync info
        instructions = stimuli.TextLine(presentation_screen_text[language],
                                        position=(0, -windowSize[1]/float(2) + (2*matrices[0].gap + cardSize[1])/float(2)),
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

        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI, process_control_events=True)

        # LOG and SYNC: Start Presentation
        exp.add_experiment_info('StartPresentation_Block_{}_timing_{}'.format(nBlock, exp.clock.time))  # Add sync info

        for index_matrix_pres_order, i in enumerate(learning_matrix_presentation_order):
            presentationOrder = newRandomPresentation(presentationOrder)
            matrix_i = matrices[i]
            for cuecard_index in range(len(classPictures)):
                matrix_i._cueCard[cuecard_index].color = bgColor
                matrix_i.plotCueCard(cuecard_index, False, bs, False)
            matrix_i.plotDefault(bs, True)

            exp.add_experiment_info('Presentation_Block_{}_matrix_{}_category_{}_timing_{}'.format(
                nBlock, i, matrix_i._category, exp.clock.time))
            exp.add_experiment_info(str(presentationOrder))
            instructions = stimuli.TextLine(
                presentation_screen_text[language] + classNames[language][matrix_i._category].upper() + ' ',
                position=(0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
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

            ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
            exp.clock.wait(ISI, process_control_events=True)

            for nCard in presentationOrder:
                mouse.hide_cursor(True, True)
                sound_played_command, sound_played = matrix_i.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
                exp.add_experiment_info(f"SoundPlayed_{str(sound_played)}_timing_{exp.clock.time}")
                exp.add_experiment_info("sound_played_command")
                exp.add_experiment_info(sound_played_command)
                del sound_played_command, sound_played
                exp.clock.wait(SoundBeforeImageTime, process_control_events=True)
                matrix_i.plotCard(nCard, True, bs, True)  # Show Location for ( 2s )
                exp.add_experiment_info('ShowCard_pos_{}_card_{}_timing_{}_sound_{}'.format(
                    nCard, matrix_i.listPictures[nCard], exp.clock.time,
                    sounds[soundsAllocation_index[matrix_i._category]]))

                exp.clock.wait(presentationCard, process_control_events=True)
                matrix_i.plotCard(nCard, False, bs, True)
                exp.add_experiment_info('HideCard_pos_{}_card_{}_timing_{}'.format(
                    nCard, matrix_i.listPictures[nCard], exp.clock.time))  # Add sync info

                ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
                exp.clock.wait(ISI, process_control_events=True)

            ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
            exp.clock.wait(ISI, process_control_events=True)

        # REST BLOCK
        instructions = stimuli.TextLine(
            rest_screen_text[language],
            position=(0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
            text_font=None, text_size=textSize, text_bold=None, text_italic=None,
            text_underline=None, text_colour=textColor, background_colour=bgColor,
            max_width=None)

        instructions.plot(bs)

        bs.present(False, True)
        exp.add_experiment_info(
            ['StartShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info

        # Preparing Trials for test block
        start_time = get_time()
        pictures_allocation = [list(picture_matrix) for picture_matrix in pictures_allocation]
        pictures_allocation = [[card.rstrip('.png') for card in picture_matrix] for picture_matrix in
                               pictures_allocation]
        trials_order = sum(pictures_allocation, [])
        trials_order = [card.rstrip('.png') for card in trials_order]
        random.shuffle(trials_order)
        trials_order = normalize_test_presentation_order(trials_order, pictures_allocation)
        while (get_time() - start_time) * 1000 < restPeriod:
            exp.keyboard.process_control_keys()

        exp.add_experiment_info(
            ['EndShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
        instructionRectangle.plot(bs)
        bs.present(False, True)

    # TEST BLOCK
    instructions = stimuli.TextLine(' TEST ',
                                    position=(
                                        0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
                                    text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                    text_underline=None, text_colour=textColor,
                                    background_colour=bgColor,
                                    max_width=None)
    instructionRectangle.plot(bs)
    instructions.plot(bs)

    bs.present(False, True)

    # LOG and SYNC Start Test
    exp.add_experiment_info(['StartTest_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info

    exp.clock.wait(shortRest, process_control_events=True)  # Short Rest between presentation and cue-recall

    instructionRectangle.plot(bs)
    bs.present(False, True)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI, process_control_events=True)

    ''' Cue Recall '''

    if nbBlocksMax == 1 or experimentName != 'Encoding':
        # Trials weren't created at the end of the learning phase, since there wasn't a learning phase
        # importing Trials for test block
        pictures_allocation = [list(picture_matrix) for picture_matrix in pictures_allocation]
        pictures_allocation = [[card.rstrip('.png') for card in picture_matrix] for picture_matrix in
                               pictures_allocation]
        if experimentName == 'Test-Encoding':
            trials_order_filename = 'test-encoding-trials.pkl'
        elif experimentName == 'ReTest-Encoding':
            trials_order_filename = 'retest-encoding-trials.pkl'
        trials_order_file = os.path.join(output_dir, trials_order_filename)

        with open(trials_order_file, "rb") as f:
            trials_order = pickle.load(f)

    exp.add_experiment_info(
        f'Test_Block_{nBlock}_timing_{exp.clock.time}')  # Add sync info
    exp.add_experiment_info(f'Test_Block_{nBlock}_Presentation_Order')
    exp.add_experiment_info(str(trials_order))
    matrix_i = matrices[0]
    for cuecard_index in range(len(classPictures)):
        matrix_i._cueCard[cuecard_index].color = constants.C_WHITE
        matrix_i.plotCueCard(cuecard_index, False, bs, False)
    matrix_i.plotDefault(bs, True)
    dont_reuse_previous_trial_pictures = [None] * len(classPictures)
    for trial_index, card in enumerate(trials_order):
        cueCards = []
        category = card[0]
        matrix_index = classPictures.index(category)
        matrix_i = matrices[matrix_index]
        pos = pictures_allocation[matrix_index].index(card)
        cueCards.append({'correct_card': True, 'category': category, 'card': card, 'pos': pos,
                         'matrix_index': matrix_index})
        exp.add_experiment_info(
            f"Trial_trialIndex_{str(trial_index)}_matrix_{category}"
            f"_pos_{pos}_card_{card}_timing_{exp.clock.time}")
        dont_reuse_previous_trial_pictures[matrix_index] = card

        other_indexes = list(range(len(classPictures)))
        other_indexes.pop(matrix_index)
        for i, other_matrix_index in enumerate(other_indexes):
            cueCards.append({})
            cueCards[i + 1]['correct_card'] = False

            # Removing any image that would have used during the previous trial
            # Ensuring wrong (wrong response) images of this trial aren't the right (to be guessed) image of the next
            # trial
            pictures_to_choose_from = list(pictures_allocation[other_matrix_index])
            try:
                next_trial_card = trials_order[trial_index + 1]
                try:
                    pictures_to_choose_from.remove(next_trial_card)
                except ValueError:
                    pass
            except IndexError: # we're at the last trial
                pass
            try:
                pictures_to_choose_from.remove(dont_reuse_previous_trial_pictures[other_matrix_index])
            except ValueError:
                pass
            cueCards[i + 1]['card'] = random.choice(pictures_to_choose_from)
            dont_reuse_previous_trial_pictures[other_matrix_index] = cueCards[i + 1]['card']
            cueCards[i + 1]['category'] = cueCards[i + 1]['card'][0]
            cueCards[i + 1]['matrix_index'] = classPictures.index(cueCards[i + 1]['category'])
            cueCards[i + 1]['pos'] = pictures_allocation[other_matrix_index].index(cueCards[i + 1]['card'])

        random.shuffle(cueCards)

        sound_played_command, sound_played = matrix_i.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
        exp.add_experiment_info(f"SoundPlayed_{str(sound_played)}_timing_{exp.clock.time}")
        exp.add_experiment_info("sound_played_command")
        exp.add_experiment_info(sound_played_command)
        del sound_played_command, sound_played
        exp.clock.wait(SoundBeforeImageTime, process_control_events=True)

        for i in range(len(classPictures)):
            cuecard_matrix = matrices[cueCards[i]['matrix_index']]
            cuecard_pos = cueCards[i]['pos']
            cuecard_card = cueCards[i]['card']
            matrix_i._cueCard[i].setPicture(cuecard_matrix._matrix.item(cuecard_pos).stimuli[0].filename)
            matrix_i.plotCueCard(i, True, bs, True)
            exp.add_experiment_info(
                f"ShowCueCard_trialIndex_{str(trial_index)}_cueCardIndex_{i}_matrix_{cueCards[i]['category']}"
                f"_pos_{cuecard_pos}_card_{cuecard_card}_timing_{exp.clock.time}")
        exp.clock.wait(presentationCard, process_control_events=True)

        instructions = stimuli.TextLine(choose_image_text[language],
                                        position=(
                                            0,
                                            -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
                                        text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                        text_underline=None, text_colour=textColor,
                                        background_colour=bgColor,
                                        max_width=None)
        instructions.plot(bs)
        bs.present(False, True)

        # Mouse Response Block
        time_left = responseTime
        valid_response = False
        rt = True  # Response time; equals None if participant haven't clicked within window time frame they were
        # given to answer
        while not valid_response and rt is not None:
            mouse.show_cursor(True, True)
            start = get_time()
            rt, position = readMouse(start, mouseButton, time_left)
            mouse.hide_cursor(True, True)

            if rt is not None:
                chosenCueCard_index = matrix_i.checkPosition(position, cue_card=True)
                if chosenCueCard_index is not None:
                    chosenCueCard = cueCards[chosenCueCard_index]
                    matrix_cueCard = matrix_i._cueCard[chosenCueCard_index]

                    if chosenCueCard['correct_card'] or \
                            (experimentName == 'Test-Encoding' or experimentName == 'ReTest-Encoding'):
                        exp.add_experiment_info(
                            f"{cuecard_response_logging_text}_trialIndex_{str(trial_index)}"
                            f"_cueCardIndex_{chosenCueCard_index}"
                            f"_matrix_{chosenCueCard['category']}"
                            f"_pos_{chosenCueCard['pos']}"
                            f"_card_{chosenCueCard['card']}"
                            f"_timing_{exp.clock.time}"
                        )
                        instructionRectangle.plot(bs)
                        bs.present(False, True)
                        matrix_i.response_feedback_stimuli_frame(bs, matrix_cueCard.position, True,
                                                                 show_or_hide=True, draw=True, no_feedback=no_feedback)
                        exp.clock.wait(feedback_time, process_control_events=True)
                        matrix_i.response_feedback_stimuli_frame(bs, matrix_cueCard.position, True,
                                                                 show_or_hide=False, draw=True, no_feedback=no_feedback)
                        instructions = stimuli.TextLine(choose_position_text[language],
                                                        position=(
                                                            0,
                                                            -windowSize[1] / float(2) + (
                                                                        2 * matrices[0].gap + cardSize[1]) / float(2)),
                                                        text_font=None, text_size=textSize, text_bold=None,
                                                        text_italic=None,
                                                        text_underline=None, text_colour=textColor,
                                                        background_colour=bgColor,
                                                        max_width=None)
                        instructions.plot(bs)
                        bs.present(False, True)
                        time_left = responseTime - rt - clicPeriod
                        # Ensuring participants have AT LEAST 3s (of value written in config file) to answer
                        if time_left < choose_location_minimum_response_time:
                            time_left = choose_location_minimum_response_time
                        valid_response = True
                        matrix_valid_response = False
                        while not matrix_valid_response:
                            mouse.show_cursor(True, True)
                            start = get_time()
                            rt, position = readMouse(start, mouseButton, time_left)
                            mouse.hide_cursor(True, True)
                            if rt is not None:
                                currentCard = matrix_i.checkPosition(position)
                                if currentCard is not None:
                                    # Click effect feedback block
                                    if currentCard not in removeCards:
                                        matrix_i._matrix.item(currentCard).color = clickColor
                                        matrix_i.plotCard(currentCard, False, bs, True)
                                        exp.clock.wait(clicPeriod, process_control_events=True)  # Wait 200ms
                                        matrix_i._matrix.item(currentCard).color = cardColor
                                        matrix_i.plotCard(currentCard, False, bs, True)
                                    instructionRectangle.plot(bs)
                                    bs.present(False, True)
                                    matrix_valid_response = True
                                    try:
                                        exp.add_experiment_info(
                                            f"MatrixResponse_trialIndex_{str(trial_index)}"
                                            f"_matrix_{chosenCueCard['category']}"
                                            f"_pos_{currentCard}"
                                            f"_card_{(matrices[chosenCueCard['matrix_index']]).listPictures[currentCard]}"
                                            f"_timing_{exp.clock.time}"
                                        )
                                    except:
                                        exp.add_experiment_info(
                                            'MatrixResponse_pos_{}_ERROR_timing_{}'.format(currentCard, exp.clock.time))
                                    if currentCard == chosenCueCard['pos']:
                                        if experimentName == 'Encoding' and nbBlocksMax != 1:
                                            sound_played_command, sound_played = matrix_i.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
                                            exp.add_experiment_info(f"SoundPlayed_{str(sound_played)}_timing_{exp.clock.time}")
                                            exp.add_experiment_info("sound_played_command")
                                            exp.add_experiment_info(sound_played_command)
                                            del sound_played_command, sound_played
                                        correctAnswers[matrix_index, nBlock] += 1
                                    exp.data.add([exp.clock.time, nBlock,
                                                  path_leaf(matrix_i._matrix.item(chosenCueCard['pos']).stimuli[0].filename),
                                                  path_leaf(matrix_i._matrix.item(currentCard).stimuli[0].filename),
                                                  rt])
                                else:
                                    if rt < time_left - clicPeriod:
                                        time_left = time_left - rt - clicPeriod
                                    else:
                                        exp.add_experiment_info(
                                            f"NoMatrixCardResponse_trialIndex_{str(trial_index)}"
                                            f"_timing_{exp.clock.time}")
                                        exp.data.add([exp.clock.time, nBlock,
                                                      path_leaf(matrix_i._matrix.item(chosenCueCard['pos']).stimuli[0].filename),
                                                      None,
                                                      rt])
                                        matrix_valid_response = True
                            else:
                                exp.add_experiment_info(
                                    f"NoMatrixCardResponse_trialIndex_{str(trial_index)}_timing_{exp.clock.time}")
                                matrix_valid_response = True

                    else:
                        exp.add_experiment_info(
                            f"WrongCueCardResponse_trialIndex_{str(trial_index)}"
                            f"_cueCardIndex_{chosenCueCard_index}"
                            f"_matrix_{chosenCueCard['category']}"
                            f"_pos_{chosenCueCard['pos']}"
                            f"_card_{chosenCueCard['card']}"
                            f"_timing_{exp.clock.time}"
                        )
                        instructionRectangle.plot(bs)
                        bs.present(False, True)
                        valid_response = True
                        matrix_i.response_feedback_stimuli_frame(bs, matrix_cueCard.position, False,
                                                                 show_or_hide=True, draw=True)
                        exp.clock.wait(feedback_time, process_control_events=True)
                        matrix_i.response_feedback_stimuli_frame(bs, matrix_cueCard.position, False,
                                                                 show_or_hide=False, draw=True)

                        exp.clock.wait(inter_feedback_delay_time, process_control_events=True)
                        for k in range(len(classPictures)):
                            if cueCards[k]['correct_card']:
                                break

                        # We use subject_correct parameter set to True in order to have green feedback on the correct
                        # image/card
                        sound_played_command, sound_played = matrix_i.playSound(soundsAllocation_index, volumeAdjusted=volumeAdjusted)
                        exp.add_experiment_info(f"SoundPlayed_{str(sound_played)}_timing_{exp.clock.time}")
                        exp.add_experiment_info("sound_played_command")
                        exp.add_experiment_info(sound_played_command)
                        del sound_played_command, sound_played
                        matrix_i.response_feedback_stimuli_frame(bs, (matrix_i._cueCard[k]).position, True,
                                                                 show_or_hide=True, draw=True)
                        exp.clock.wait(feedback_time, process_control_events=True)
                        matrix_i.response_feedback_stimuli_frame(bs, (matrix_i._cueCard[k]).position, True,
                                                                 show_or_hide=False, draw=True)
                else:
                    if rt < time_left - clicPeriod:
                        time_left = time_left - rt - clicPeriod
                    else:
                        exp.add_experiment_info(f"NoCueCardResponse_trialIndex_{str(trial_index)}_timing_{exp.clock.time}")
                        valid_response, rt = True, None
            else:
                exp.add_experiment_info(f"NoCueCardResponse_trialIndex_{str(trial_index)}_timing_{exp.clock.time}")
        instructionRectangle.plot(bs)
        bs.present(False, True)

        for i in range(len(classPictures)):
            matrix_i.plotCueCard(i, False, bs, True)
            exp.add_experiment_info(
                f"HideCueCard_trialIndex_{str(trial_index)}_cueCardIndex_{i}_matrix_{cueCards[i]['category']}"
                f"_pos_{cuecard_pos}_card_{cuecard_card}_timing_{exp.clock.time}")

        # Longer than usual time between two trials, in order to ensure sounds aren't mixed up by participants
        exp.clock.wait(presentationCard, process_control_events=True)
        ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
        exp.clock.wait(ISI, process_control_events=True)

    if nbBlocksMax != 1 and experimentName == 'Encoding':
        matrix_i.plotDefault(bs, draw=True, show_matrix=False)
        results_feedback = f"""{feedback_message[language]}:
        {classNames[language][classPictures[0]]}: {str(int(correctAnswers[0, nBlock]))} out of {str(matrices[0]._matrix.size - len(removeCards))}
        {classNames[language][classPictures[1]]}: {str(int(correctAnswers[1, nBlock]))} out of {str(matrices[1]._matrix.size - len(removeCards))}"""
        # {classNames[language][classPictures[2]]}: {str(int(correctAnswers[2, nBlock]))} out of {str(matrices[2]._matrix.size - len(removeCards))}
        instructions = stimuli.TextBox(results_feedback,
                                       size=(windowSize[0], 4 * cardSize[1]),
                                       position=(0, 0),
                                       text_font=None, text_size=textSize, text_bold=None, text_italic=None,
                                       text_underline=None, text_colour=textColor,
                                       background_colour=bgColor,
                                       text_justification=1)
        instructionRectangle_results = stimuli.Rectangle(size=(windowSize[0], 4 * cardSize[1]), position=(0, 0),
                                                         colour=constants.C_DARKGREY)

        instructions.plot(bs)
        bs.present(False, True)
        exp.clock.wait(thankYouRest, process_control_events=True)
        instructionRectangle_results.plot(bs)
        bs.present(False, True)

        pictures_allocation = [np.asarray([card + '.png' for card in picture_matrix])
                               for picture_matrix in pictures_allocation]
        for i, category in enumerate(classPictures):
            matrices[i].associatePictures(pictures_allocation[i])
        matrix_i = matrices[0]
        matrix_i.plotDefault(bs, True)
        for i in range(len(classPictures)):
            matrix_i.plotCueCard(i, False, bs, draw=True)

    if ignore_one_learned_matrices and \
            [correctAnswers[i, nBlock] >= correctAnswersMax for i in range(numberClasses)].count(True) == 1:
        # one learned matrix
        index_matrix_not_to_present_again =\
            [correctAnswers[i, nBlock] >= correctAnswersMax for i in range(numberClasses)].index(True)
        matrices_to_present = np.delete(matrices_to_present, index_matrix_not_to_present_again)

    ISI = design.randomize.rand_int(min_max_ISI[0], min_max_ISI[1])
    exp.clock.wait(ISI, process_control_events=True)
    exp.clock.wait(shortRest, process_control_events=True)

    instructions = stimuli.TextLine(
        rest_screen_text[language],
        position=(0, -windowSize[1] / float(2) + (2 * matrices[0].gap + cardSize[1]) / float(2)),
        text_font=None, text_size=textSize, text_bold=None, text_italic=None,
        text_underline=None, text_colour=textColor, background_colour=bgColor,
        max_width=None)

    instructions.plot(bs)
    bs.present(False, True)
    exp.add_experiment_info(
        ['StartShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
    exp.clock.wait(restPeriod, process_control_events=True)
    exp.add_experiment_info(
        ['EndShortRest_block_{}_timing_{}'.format(nBlock, exp.clock.time)])  # Add sync info
    instructionRectangle.plot(bs)
    bs.present(False, True)

    currentCorrectAnswers = correctAnswers[:, nBlock]
    if ignore_one_learned_matrices:
        if index_matrix_not_to_present_again is not None:
            currentCorrectAnswers[index_matrix_not_to_present_again] = 15

    nBlock += 1

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

control.end()
delete_temp_files()

try:
    import csv
    i = 1
    score_file = generate_bids_filename(subjectName, session, experimentName,
                                  filename_suffix='_score', filename_extension='.txt', run=None)
    while os.path.isfile(os.path.join(io.defaults.datafile_directory, score_file)):
        i += 1
        i_string = '0' * (2 - len(str(i))) + str(i)  # 0 padding, assuming 2-digits number
        score_file = generate_bids_filename(subjectName, session, experimentName,
                                      filename_suffix='_score', filename_extension='.txt', run=i_string)

    with open(os.path.join(io.defaults.datafile_directory, score_file), 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        for i in range(nBlock-1):  # because there is a <nBlock += 1> at the very end
            row = []
            for j in range(len(classPictures)):
                row.append(
                    f"""category_{classPictures[j]}:{str(int(correctAnswers[j, nBlock]))}/{str(matrices[j]._matrix.size - len(removeCards))} """)
            print(row)
            writer.writerow(row)
except:
    pass
