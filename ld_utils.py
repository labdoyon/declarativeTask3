import os
import csv
from math import floor

import numpy as np
import ast
import re
from scipy.spatial import distance
from expyriment.misc import data_preprocessing

matrixSize = (6, 4)
matrixTemplate = [0] * 24
removeCards = []
classPictures = ['a', 'c']
presentationCard = 2000
feedback_time = 1000

sound_title_index = 2
number_learning_blocks_index = 3

dont_suppress_card_double_checking = True
true_sounds = ['standard', 'noise', 'A']
test_recall_suffixes = \
            ['matrixA_order'] + \
            ['matrixA_CueCard' + str(cuecard_index) for cuecard_index in range(len(classPictures))] + \
            ['CueCardResponseImage', 'CueCardResponseCorrect', 'CueCardReactionTime', 'X_clicked', 'Y_clicked',
             'matrixA_distanceToMatrixA', 'matrixA_ReactionTime', 'matrixA_ShowTime', 'matrixA_HideTime']
first_column_titles = ['Subject', 'Item', 'Class', 'Sound', 'BlocksOfLearning',
                       'MA_X_coord', 'MA_Y_coord', 'MR_X_coord', 'MR_Y_coord']
recognition_column_titles = [
    'TestRecognition_matrices_Presentation_order', 'TestRecognition_matrixA_order', 'TestRecognition_matrixA_answer',
    'TestRecognition_matrixA_ReactionTime', 'TestRecognition_matrixA_ShowTime', 'TestRecognition_matrixA_HideTime',

    'TestRecognition_matrixR_order', 'TestRecognition_matrixR_answer', 'TestRecognition_matrixR_ReactionTime',
    'TestRecognition_matrixR_ShowTime', 'TestRecognition_matrixR_HideTime', 'TestRecognition_matrixR_distanceToMatrixA'
             ]


class CorrectCards(object):
    def __init__(self):
        self.answer = []
        self.position = []
        self.picture = []


class WrongCards(object):
    def __init__(self):
        self.answer = []
        self.position = []
        self.picture = []


class Day(object):
    def __init__(self, recognition=False, association=False, learning=False, test_association=False):
        self.matrix = []
        self.header = []
        self.matrix_pictures = []
        self.number_blocks = 0
        self.matrix_size = ()
        self.events = []
        self.classes_order = []
        self.sounds_order = []
        self.classes_to_sounds_index = []
        self.ttl_in_data = None
        self.cards_reaction_time = []
        self.hide_card_absolute_time = []
        self.show_card_absolute_time = []
        self.matrix_presentation_order = []

        self.cards_order = {}
        if not association and not learning and not recognition and not test_association:
            self.recognition = False
            self.association = False
            self.test_association = False
            self.cards_distance_to_correct_card = []
        elif association and not recognition and not learning:
            self.recognition = False
            self.association = True
            self.test_association = False
        elif test_association and not recognition and not learning:
            self.test_association = True
            self.recognition = False
            self.association = False
        elif learning and not recognition and not association:
            self.recognition = False
            self.association = False
            self.test_association = False
            self.show_card_learning_absolute_time = []
            self.hide_card_learning_absolute_time = []
            self.cards_learning_order = []
            self.cards_distance_to_correct_card = []
        elif recognition and not learning and not association:
            self.recognition = True
            self.association = False
            self.test_association = False
            self.cards_answer = {}
            self.recognition_cards_order = {}
            self.recognition_answer = {}
            self.recognition_cards_reaction_time = {}
            self.show_recognition_card_absolute_time = {}
            self.hide_recognition_card_absolute_time = {}


def matrix_index_to_xy_coordinates(matrix_index):
    # this function takes the matrix_index of an image (integer from 0 to 35 in case of a 6-by-6 matrix) and returns
    # the X and Y coord of the image in the matrix
    # (X=1, Y=1) being the top left corner of the matrix, and (X=6, Y=6) being the bottom right corner of the matrix
    # the matrix is populated in columns: as in, matrix_index 0 to 5 are positions (1,1), (1,2), (1,3) ... (1,6),
    # matrix_index 6 to 11 are positions (2,1), (2,2), (2,3) ... (2,6) in (X,Y) coordinates, and so on
    # we add +1 so X and Y are index from 1 and not from 0
    matrix_x_coord, matrix_y_coord = divmod(matrix_index, matrixSize[1])
    return matrix_x_coord+1, matrix_y_coord+1


def learning_file_name(output_location):
    return os.getcwd() + os.path.sep + output_location + '_learning.csv'


def extract_matrix_and_data(i_folder, i_file, recognition=False, learning=False, association=False):
    # header = data_preprocessing.read_datafile(i_folder + i_file, only_header_and_variable_names=True)
    header = data_preprocessing.read_datafile(i_file, only_header_and_variable_names=True)

    # Extracting pictures' positions in the matrix
    header2 = header[3].split('\n#e ')
    find_xpd_file = lambda content, title: ast.literal_eval(
        content[content.index(title) + 1].split('\n')[0].split('\n')[0])
    for string in header2:
        if 'TTL_RECEIVED_timing_' in string:
            ttl_event = string
            break
    ttl_timestamp = int(re.search('timing_([0-9]+)', ttl_event).group(1))

    # if not learning and not recognition:
    #     for string in header2:
    #         if 'MatrixPresentationOrder' in string:
    #             matrix_presentation_order_event = string
    #             break
    #     target = re.search('MatrixPresentationOrder_(.+?)_', matrix_presentation_order_event).group(0)
    #     target = target.replace('MatrixPresentationOrder_', '').replace('_', '')
    #     target = ast.literal_eval(target)
    #     matrix_presentation_order = target
    if recognition:
        for string in header2:
            if 'MatrixPresentationOrder' in string:
                matrix_presentation_order_event = string
                break
        target = re.search('MatrixPresentationOrder_(.*)', matrix_presentation_order_event).group(0)
        target = target.replace('MatrixPresentationOrder_', '').replace('_', '')
        target = ast.literal_eval(target)
        matrix_presentation_order = target

    matrices = []
    if learning or not recognition:
        for index, category in enumerate(classPictures):
            learning_matrix_header = f'matrix {index}, pictures from class {category}:'
            matrix = find_xpd_file(header2, learning_matrix_header)
            matrix = [element.rstrip('.png') if element is not None else None for element in matrix]
            matrices.append(matrix)
    elif recognition and not association:
        learning_matrices = []
        recognition_matrices = []
        matrices_cards_order = []
        matrices_rec_or_a = []
        presentation_orders = []
        for index, category in enumerate(classPictures):
            learning_matrix_header = f'LearningMatrix_{index}_category_{category}:'
            recognition_matrix_header = f'RandomMatrix_{index}_category_{category}:'
            learning_matrix = find_xpd_file(header2, learning_matrix_header)
            recognition_matrix = find_xpd_file(header2, recognition_matrix_header)
            learning_matrix = [element.rstrip('.png') if element is not None else None for element in learning_matrix]
            recognition_matrix = [element.rstrip('.png') if element is not None else None for element in recognition_matrix]
            learning_matrices.append(learning_matrix)
            recognition_matrices.append(recognition_matrix)
            cards_order_index = header2.index(f'matrix_{index}_category_{category}_Presentation Order:')
            cards_order = header2[cards_order_index + 1: cards_order_index + 6]
            cards_order = ''.join(cards_order)
            non_decimal = re.compile(r'[^\d,]+')
            cards_order = non_decimal.sub('', cards_order)
            cards_order = cards_order.split(',')
            cards_order = [order for order in cards_order if order != '']
            matrices_cards_order.append([int(x) for x in cards_order])
            matrix_card_order = matrices_cards_order[index]
            matrices_rec_or_a.append(matrix_card_order[int(len(matrix_card_order)/2):])
            presentation_orders.append(matrix_card_order[:int(len(matrix_card_order)/2)])


    classes_to_sounds_index_position = 'Image classes to sounds (index):'
    classes_to_sounds_index = find_xpd_file(header2, classes_to_sounds_index_position)
    sounds_order_position = 'Sounds order:'
    sounds_order = find_xpd_file(header2, sounds_order_position)
    classes_order_position = 'Image classes order:'
    classes_order = find_xpd_file(header2, classes_order_position)

    # Extracting data
    events = header2
    events = [element.encode('ascii') for element in events]

    if recognition:
        matrices = learning_matrices
    if [len(matrix) for matrix in matrices] == [24] * len(classPictures):
        matrix_size = (6, 4)
    else:
        raise ValueError('Matrix dimensions cannot be identified')

    events = [event.decode('utf-8') for event in events]

    if recognition:
        return events, learning_matrices, matrix_size, \
               classes_order, sounds_order, classes_to_sounds_index, \
               recognition_matrices, matrices_rec_or_a, presentation_orders, ttl_timestamp, matrix_presentation_order
    elif learning:
        return events, matrices, matrix_size, \
               classes_order, sounds_order, classes_to_sounds_index, ttl_timestamp
    else:
        return events, matrices, matrix_size, classes_order, sounds_order, classes_to_sounds_index, ttl_timestamp


def extract_events(events, matrix_size, classes_order, ttl_timestamp=None, mode=None):
    if ttl_timestamp is None:
        print("WARNING: no events file found, no ttl found")

    if mode == 'learning':
        matrices_presentation_order = []

    cards_position = []  # the position of the card in the matrix
    cards_distance_to_correct_card = []  # the distance between the card clicked and the correct answer (0 if correct)

    cards_order = []  # the order of presentation of the card in the test phase
    position_response_reaction_time = []
    position_response_index_responded = []
    show_card_absolute_time = []
    hide_card_absolute_time = []
    cuecard_presented_image = []
    cuecard_response_image = []
    cuecard_response_correct = []
    cuecards_reaction_time = []  # the reaction time of the subject when presented with this card in the test phase
    register_on = False
    if mode == 'learning':
        show_card_learning_absolute_time = []
        hide_card_learning_absolute_time = []
        cards_learning_order = []

    for event_index, event in enumerate(events):
        # Marks the beginning of a test block
        if 'Test_Block' in event and 'Presentation_Order' in event:
            # we add a dictionary for
            cards_position.append({})
            cards_distance_to_correct_card.append({})
            cards_order.append({})
            cuecards_reaction_time.append({})
            position_response_reaction_time.append({})
            position_response_index_responded.append({})
            hide_card_absolute_time.append({})
            show_card_absolute_time.append({})
            # cuecard_presented_image.append([{}] * len(classPictures))
            cuecard_presented_image.append([{}, {}, {}])
            cuecard_response_image.append({})
            cuecard_response_correct.append({})
            # ADD MORE DICTIONARIES FOR MORE VALUES/FIELDS
            block_number = len(cards_position) - 1
            register_on = True
            # we start collecting the answers
            order = 0  # we start a 0, first card/image presented during the test
            test_presentation_order = ast.literal_eval(events[event_index + 1])
        # Marks the beginning of a presentation Block
        elif 'Presentation_Block' in event and 'MatrixPresentationOrder' in event:
            register_on = False
            try:
                del hidden_card, test_card, position
            except UnboundLocalError:
                pass
            show_card_learning_absolute_time.append({})
            hide_card_learning_absolute_time.append({})
            cards_learning_order.append({})
            learning_order = 0
            learning_block_number = len(cards_learning_order) - 1
            if mode == 'learning':
                matrices_presentation_order.append({})
                target = re.search('MatrixPresentationOrder_(.+?)_', event).group(0)
                target = target.replace('MatrixPresentationOrder_', '').replace('_', '')
                target = ast.literal_eval(target)
                matrix_presentation_order = target
                matrices_presentation_order[learning_block_number]['presentation'] = matrix_presentation_order
        elif 'Presentation_Block' in event and 'matrix' in event and 'category' in event:
            presentation_matrix_id = int(re.search('matrix_([0-9]+)', event).group(1))
            presentation_category = re.search('(?<=category_)\w+', event).group(0)[0]
            if classes_order[presentation_matrix_id] != presentation_category:
                raise ValueError
        if 'ShowCard' in event and not register_on:
            learning_card = re.search('(?<=card_)\w+', event).group(0)
            show_time = int(re.search('timing_([0-9]+)', event).group(1))
            if ttl_timestamp is not None:
                show_card_learning_absolute_time[learning_block_number][learning_card] = show_time - ttl_timestamp
            else:
                show_card_learning_absolute_time[learning_block_number][learning_card] = show_time
            cards_learning_order[learning_block_number][learning_card] = learning_order
            learning_order += 1
        if 'HideCard' in event and not register_on:
            hidden_card = re.search('(?<=card_)\w+', event).group(0)
            hide_time = int(re.search('timing_([0-9]+)', event).group(1))
            if ttl_timestamp is not None:
                hide_card_learning_absolute_time[learning_block_number][hidden_card] = hide_time - ttl_timestamp
            else:
                hide_card_learning_absolute_time[learning_block_number][hidden_card] = hide_time
        elif register_on and 'Trial' in event:
            test_card = re.search('card_(.+?)_', event).group(1)
            cards_position[block_number][test_card] = trial_position = re.search('pos_([0-9]+)_', event).group(1)
            cards_order[block_number][test_card] = order
            trial_index = int(re.search('trialIndex_([0-9]+)', event).group(1))
            trial_category = re.search('(?<=matrix_)\w+', event).group(0)[0]
            trial_start_time = int(re.search('timing_([0-9]+)', event).group(1))
            next_trial_not_reached = False
        elif 'ShowCueCard' in event and register_on:
            reaction_start = int(re.search('timing_([0-9]+)', event).group(1))
            # Only the latest of all cue cards shown is taken as the "show Cue Card absolute time"
            if ttl_timestamp is not None:
                show_card_absolute_time[block_number][test_card] = int(re.search('timing_([0-9]+)', event).group(1)) - \
                    ttl_timestamp
            else:
                show_card_absolute_time[block_number][test_card] = int(re.search('timing_([0-9]+)', event).group(1))
            cue_card_index = int(re.search('cueCardIndex_([0-9]+)', event).group(1))
            cuecard_presented_image[block_number][cue_card_index][test_card] = re.search('card_(.+?)_', event).group(1)
        elif 'HideCueCard' in event and register_on:
            hide_card_time = int(re.search('timing_([0-9]+)', event).group(1))
            # Only the latest of all cue cards shown is taken as the "show Cue Card absolute time"
            if ttl_timestamp is not None:
                hide_card_absolute_time[block_number][test_card] = hide_card_time - ttl_timestamp
            else:
                hide_card_absolute_time[block_number][test_card] = int(re.search('timing_([0-9]+)', event).group(1))
            if not next_trial_not_reached:
                order += 1
                next_trial_not_reached = True
        elif 'CueCardResponse' in event:
            if 'NoCueCardResponse' in event:
                cuecard_response_image[block_number][test_card] = 'noResponse'
                cuecard_response_correct[block_number][test_card] = 'noResponse'
                cuecards_reaction_time[block_number][test_card] = 'noResponse'
                position_response_index_responded[block_number][test_card] = 'noResponse'
                cards_distance_to_correct_card[block_number][test_card] = 'noResponse'
                position_response_reaction_time[block_number][test_card] = 'noResponse'
            else:
                response_card = re.search('card_(.+?)_', event).group(1)
                cuecard_response_image[block_number][test_card] = response_card
                if response_card == test_card:
                    cuecard_response_correct[block_number][test_card] = 1
                else:
                    cuecard_response_correct[block_number][test_card] = 0
                    if mode == 'learning':
                        position_response_index_responded[block_number][test_card] = 'wrongCueCard'
                        cards_distance_to_correct_card[block_number][test_card] = 'wrongCueCard'
                        position_response_reaction_time[block_number][test_card] = 'wrongCueCard'
                # Since Hide Cue Cards no longer mark the beginning of the trial and appearance of the mouse for the
                # participant, we have to subtract presentationCard (2s) from the reaction Time. This doesn't work if
                # the Escape key of the keyboard was pressed, as this would mean the waiting time wouldn't have been 2s.
                # This information is missing in the .xpd files. Possibly present in .xpe files
                cuecards_reaction_time[block_number][test_card] = int(re.search('timing_([0-9]+)', event).group(1)) \
                    - show_card_absolute_time[block_number][test_card] - presentationCard
                if ttl_timestamp is not None:
                    cuecards_reaction_time[block_number][test_card] -= ttl_timestamp
                cuecard_response_time = int(re.search('timing_([0-9]+)', event).group(1))
        elif 'MatrixResponse' in event and 'ERROR' not in event and register_on:
            response = re.search('(?<=card_)\w+', event).group(0)
            response_time = int(re.search('timing_([0-9]+)', event).group(1))
            position_response_reaction_time[block_number][test_card] = response_time - feedback_time \
                - cuecard_response_time
            if response == test_card:
                cards_distance_to_correct_card[block_number][test_card] = 0
            else:
                response_position = re.search('pos_([0-9]+)_', event).group(1)
                cards_distance_to_correct_card[block_number][test_card] = distance.euclidean(
                    np.unravel_index(int(trial_position), matrix_size),
                    np.unravel_index(int(response_position), matrix_size))
            position_response_index_responded[block_number][test_card] = re.search('pos_([0-9]+)_', event).group(1)
        elif 'MatrixResponse' in event and 'ERROR' in event:
            cards_distance_to_correct_card[block_number][test_card] = 'ERROR'
            position_response_reaction_time[block_number][test_card] = 'ERROR'
            position_response_index_responded[block_number][test_card] = 'ERROR'
        elif 'NoMatrixCardResponse' in event:
            cards_distance_to_correct_card[block_number][test_card] = 'noResponse'
            position_response_reaction_time[block_number][test_card] = 'noResponse'
            position_response_index_responded[block_number][test_card] ='noResponse'

    if mode == 'learning':
        return cards_order, cards_distance_to_correct_card, position_response_reaction_time, block_number + 1, \
               show_card_absolute_time, hide_card_absolute_time, show_card_learning_absolute_time, \
               hide_card_learning_absolute_time, cards_learning_order, matrices_presentation_order, \
               cards_position, position_response_index_responded, cuecard_presented_image, cuecard_response_image, \
               cuecard_response_correct, cuecards_reaction_time
    else:
        return cards_order, cards_distance_to_correct_card, position_response_reaction_time, block_number + 1, \
            show_card_absolute_time, hide_card_absolute_time, cuecard_presented_image, cuecard_response_image, \
            cuecard_response_correct, cuecards_reaction_time, position_response_index_responded, cards_position


def recognition_extract_events(events, matrices_pictures, recognition_matrices, matrices_a_or_rec, presentation_orders,
                               matrix_size, ttl_timestamp=None):
    cards = sum(matrices_pictures, [])
    cards.sort()
    recognition_distance_matrix_a = {}
    recognition_cards_order = {}
    cards_order = {}
    # taking into account the center where there is no card:
    # if len(removeCards) == 1 and removeCards[0] == int(floor(matrixSize[0]*matrixSize[1]/2)):
    #     for i in range(len(presentation_order)):
    #         if presentation_order[i] > removeCards[0]:
    #             presentation_order[i] = presentation_order[i] - 1
    for index, category in enumerate(classPictures):
        recognition_matrix = recognition_matrices[index]
        matrix_pictures = matrices_pictures[index]
        presentation_order = presentation_orders[index]
        for i in range((matrixSize[0]*matrixSize[1]-len(removeCards))*2):
            if matrices_a_or_rec[index][i]:
                recognition_cards_order[recognition_matrix[presentation_order[i]]] = i
            else:
                cards_order[matrix_pictures[presentation_order[i]]] = i

    # Assigning cards_order
    # cards_order = [presentation_order[i] for i in range(len(presentation_order)) if matrix_rec_or_a[i]]
    # cards_order = {cards_no_none[i]: cards_order[i] for i in range(len(cards_order))}
    # Assigning recognition_cards_order
    # recognition_cards_order = [presentation_order[i] for i in range(len(presentation_order)) if not matrix_rec_or_a[i]]
    # recognition_cards_order = {cards_no_none[i]: recognition_cards_order[i] for i in range(len(recognition_cards_order))}

    cards_position = {}
    recognition_cards_position = {}
    cards_answer = {}
    recognition_answer = {}
    cards_reaction_time = {}
    # cards_absolute_time = {}
    hide_card_absolute_time = {}
    show_card_absolute_time = {}
    recognition_cards_reaction_time = {}
    # recognition_cards_absolute_time = {}
    hide_recognition_card_absolute_time = {}
    show_recognition_card_absolute_time = {}

    matrix_category = None
    matrix_index = None
    for event in events:
        if 'matrix' in event and 'category' in event and 'Presentation Order:' in event:
            matrix_index = int(re.search('matrix_([0-9]+)', event).group(1))
            matrix_category = re.search('(?<=category_)\w+', event).group(0)[0]
            presentation_order = presentation_orders[matrix_index]
            matrix_rec_or_a = matrices_a_or_rec[matrix_index]
            matrix_pictures = matrices_pictures[matrix_index]
            recognition_matrix = recognition_matrices[matrix_index]
            counter = 0
        elif matrix_category is not None and matrix_index is not None:
            if 'ShowCard' in event:
                card = re.search('(?<=card_)\w+', event).group(0)
                card = card.rstrip('.png')
                card_position = re.search('pos_([0-9]+)_', event).group(1)

                # Checking if there was no response in the last card
                expected_card = recognition_matrix[presentation_order[counter]] if matrix_rec_or_a[counter] \
                    else matrix_pictures[presentation_order[counter]]
                if card != expected_card:
                    if matrix_rec_or_a[counter]:
                        recognition_answer[last_card] = 'noResponse'
                        recognition_cards_reaction_time[last_card] = 'noResponse'
                    else:
                        cards_answer[last_card] = 'noResponse'
                        cards_reaction_time[last_card] = 'noResponse'
                    counter += 1
                if ttl_timestamp is None:
                    if matrix_rec_or_a[counter]:
                        show_recognition_card_absolute_time[card] = int(re.search('timing_([0-9]+)', event).group(1))
                    else:

                        show_card_absolute_time[card] = int(re.search('timing_([0-9]+)', event).group(1))
                else:
                    if matrix_rec_or_a[counter]:
                        show_recognition_card_absolute_time[card] = \
                            int(re.search('timing_([0-9]+)', event).group(1)) - ttl_timestamp
                    else:
                        show_card_absolute_time[card] = \
                            int(re.search('timing_([0-9]+)', event).group(1)) - ttl_timestamp

                if matrix_rec_or_a[counter]:
                    recognition_cards_position[card] = card_position
                else:
                    cards_position[card] = card_position

                last_card = card
            if 'HideCard' in event:
                hidden_card = re.search('(?<=card_)\w+', event).group(0)
                hidden_card_position = re.search('pos_([0-9]+)_', event).group(1)
                reaction_start = int(re.search('timing_([0-9]+)', event).group(1))
                if ttl_timestamp is None:
                    if matrix_rec_or_a[counter]:
                        hide_recognition_card_absolute_time[hidden_card] = int(re.search('timing_([0-9]+)', event).group(1))
                    else:
                        hide_card_absolute_time[hidden_card] = int(re.search('timing_([0-9]+)', event).group(1))
                else:
                    if matrix_rec_or_a[counter]:
                        hide_recognition_card_absolute_time[hidden_card] = \
                            int(re.search('timing_([0-9]+)', event).group(1)) - ttl_timestamp
                    else:
                        hide_card_absolute_time[hidden_card] = \
                            int(re.search('timing_([0-9]+)', event).group(1)) - ttl_timestamp
                if dont_suppress_card_double_checking and\
                        (hidden_card != card or hidden_card_position != card_position):
                    raise Exception("""It seems a card was not hidden after being shown. Something may be wrong with
                    the .xpd files you're using as input. You may skip this double-checking by changing
                    `dont_suppress_card_double_checking` to `False` in ld_utils.py if you know what you're doing""")
            if 'Response_NoRT' in event:
                if matrix_rec_or_a[counter]:
                    recognition_answer[card] = 'noResponse'
                    recognition_cards_reaction_time[card] = 'noResponse'
                elif not matrix_rec_or_a[counter]:
                    cards_answer[card] = 'noResponse'
                    cards_reaction_time[card] = 'noResponse'
            if 'Response' in event and 'Response_NoRT' not in event:
                # response = re.search('(?<=Response_)\w+', event).group(0)
                response = re.search('Response_([a-zA-Z]+)_', event).group(1)
                response_time = int(re.search('timing_([0-9]+)', event).group(1))
                # matrix_rec_or_a[counter] == 1 means a recognition picture was shown
                # matrix_rec_or_a[counter] == 0 means a matrixA picture was shown
                if not matrix_rec_or_a[counter] and response == 'MatrixA':
                    cards_answer[card] = 1
                    cards_reaction_time[card] = response_time - reaction_start
                elif not matrix_rec_or_a[counter] and response == 'None':
                    cards_answer[card] = 0
                    cards_reaction_time[card] = response_time - reaction_start
                elif matrix_rec_or_a[counter] and response == 'None':
                    recognition_answer[card] = 1
                    recognition_cards_reaction_time[card] = response_time - reaction_start
                elif matrix_rec_or_a[counter] and response == 'MatrixA':
                    recognition_answer[card] = 0
                    recognition_cards_reaction_time[card] = response_time - reaction_start
                counter += 1
    # Edge case: If there is no response at the very last card in the presentation:
    try:
        test = recognition_answer[card]
        test = recognition_cards_reaction_time[card]
    except KeyError:
        recognition_answer[card] = 'noResponse'
        recognition_cards_reaction_time[card] = 'noResponse'
    try:
        test = cards_answer[card]
        test = cards_reaction_time[card]
    except KeyError:
        cards_answer[card] = 'noResponse'
        cards_reaction_time[card] = 'noResponse'
    # (END OF) Edge case: If there is no response at the very last card in the presentation:

    for card in cards:
        recognition_distance_matrix_a[card] = distance.euclidean(
            np.unravel_index(int(cards_position[card]), matrix_size),
            np.unravel_index(int(recognition_cards_position[card]), matrix_size))
    return cards_order, cards_answer, cards_reaction_time, show_card_absolute_time, hide_card_absolute_time,\
        recognition_cards_order, recognition_answer, recognition_cards_reaction_time,\
        show_recognition_card_absolute_time, hide_recognition_card_absolute_time, recognition_distance_matrix_a


def extract_association_data(i_folder, i_file, matrices, learning=False, test=False):
    if (not learning and not test) or (learning and test):
        raise Exception("""extract_association_data must have either <learning> or <test> parameter set to True
            Only one of the two parameters can be set to True""")
    header = data_preprocessing.read_datafile(i_folder + i_file, only_header_and_variable_names=True)

    header2 = header[3].split('\n#e ')
    find_xpd_file = lambda content, title: ast.literal_eval(
        content[content.index(title) + 1].split('\n')[0].split('\n')[0])
    classes_to_sounds_index_position = 'Image classes to sounds (index):'
    classes_to_sounds_index = find_xpd_file(header2, classes_to_sounds_index_position)
    sounds_order_position = 'Sounds order:'
    sounds_order = find_xpd_file(header2, sounds_order_position)
    classes_order_position = 'Image classes order:'
    classes_order = find_xpd_file(header2, classes_order_position)

    # Trials are identified by the card you had to guess. If in a trial you are presented with 3 cards, whichever card
    # was the correct one, the one you had to guess, this card will be used to identify the trial. No other trial
    # will use this card as target to be correctly guessed. So it is a valid unique id.

    # trial_reaction_time is a dictionary, keys are cards (e.g. a001). The card identifies a trial. The value in the
    # dictionary is the subject's reaction time in ms.
    trial_reaction_time = {}

    trial_other_card1 = {}
    trial_other_card2 = {}
    if learning:
        # trial_number_responses is a dictionary, keys are cards (e.g. a001). The card identifies a trial. The value in
        # the dictionary is the number of responses subject gave before
        trial_number_responses = {}

    if test:
        # trial_response_correct is a dictionary, keys are cards (e.g. a001). The card identifies a trial. The value in
        # the dictionary is whether the subject picked the right card or not (1: yes ; 0: No)
        trial_response_correct = {}
        # trial_response_correct is a dictionary, keys are cards (e.g. a001). The card identifies a trial. The value in
        # the dictionary is the card subject chose
        trial_response_card = {}

    events = header[-1].split('\n')
    experiment_started = 0
    for index_event, event in enumerate(events):
        if experiment_started:
            if 'Trial' in event:
                trial_number = int(re.search('Trial_([0-9]+)', event).group(1))
                if trial_number == 6:
                    print()
                sound_index = int(re.search('soundIndex_([0-9]+)', event).group(1))
                sound_id = re.search('soundId_(.*)', event).group(1)
                if sound_id != sounds_order[sound_index]:
                    raise Exception("Sound id doesn't match sound name, please check")
                trial_cards = []
                trial_cards_position = []
                matrix = ast.literal_eval(events[index_event+1][3:])
                matrix = matrix[-3:]
                matrix = [card.rstrip('.png') for card in matrix]
                all_cards_shown = False
                keys_list = list(classes_to_sounds_index.keys())
                values_list = list(classes_to_sounds_index.values())
                category = keys_list[values_list.index(sound_index)]
                correct_card = [card for card in matrix if card[0] == category][0]
            elif 'ShowCard' in event:
                last_show_card_timing = int(re.search('timing_([0-9]+)', event).group(1))
            elif 'Response' in event:
                pos = int(re.search('pos_([0-9]+)_', event).group(1))
                response_card = matrix[pos]
                response_card = response_card.rstrip('.png')
                # trial_number_responses
                if learning and not ('Correct' in event):
                    try:
                        trial_number_responses[correct_card] += 1
                    except KeyError:
                        trial_number_responses[correct_card] = 1
                # trial_reaction_time
                if test or ('Correct' in event):
                    trial_reaction_time[correct_card] = \
                        int(re.search('timing_([0-9]+)', event).group(1)) - last_show_card_timing
                # trial_response_correct
                if test and correct_card != response_card:
                    trial_response_correct[correct_card] = 0
                elif test and correct_card == response_card:
                    trial_response_correct[correct_card] = 1
                # trial_response_card
                if test:
                    trial_response_card[correct_card] = response_card
                # trial_other_card1 ; trial_other_card2
                if (learning and 'Correct' in event) or test:
                    matrix_left = list(matrix)
                    matrix_left.remove(response_card)
                    trial_other_card1[correct_card] = matrix_left[0]
                    trial_other_card2[correct_card] = matrix_left[1]
        if 'StartExp' in event:
            experiment_started = 1

    cards = sum(matrices, [])
    for card in cards:
        try:
            trial_reaction_time[card]
            trial_reaction_time[card]
            trial_other_card1[card]
        except KeyError:
            trial_reaction_time[card] = 'noTrial'
            trial_other_card1[card] = 'noTrial'
            trial_other_card2[card] = 'noTrial'
            if learning:
                trial_number_responses[card] = 'noTrial'
            if test:
                trial_response_correct[card] = 'noTrial'
                trial_response_card[card] = 'noTrial'

    if learning:
        return classes_order, sounds_order, classes_to_sounds_index, trial_reaction_time, \
            trial_other_card1, trial_other_card2, trial_number_responses
    if test:
        return classes_order, sounds_order, classes_to_sounds_index, trial_reaction_time, \
            trial_other_card1, trial_other_card2, trial_response_correct, trial_response_card


# def association_extract_events(events, matrices_pictures, matrix_size, presentation_order, sounds_order,
#                                ttl_timestamp=False):
#
#     cards_order = {}
#     order = 0
#     experiment_started = False
#     show_card_absolute_time = {}
#     hide_card_absolute_time = {}
#     cards_answer = {}
#     cards_bool_answer = {}
#     cards_reaction_time = {}
#     presentation_order_temp = []
#     if len(removeCards) == 1: #only handling case where only one card is removed
#         for x in presentation_order:
#             if x > removeCards[0]:
#                 presentation_order_temp.append(x-1)
#             else:
#                 presentation_order_temp.append(x)
#     presentation_order = presentation_order_temp
#     for event in events:
#         if experiment_started:
#             if 'TTL_RECEIVED' in event:
#                 ttl_timestamp = int(re.search('timing_([0-9]+)', event).group(1))
#             if 'ShowCard' in event:
#                 card = re.search('(?<=card_)\w+', event).group(0)
#                 expected_card = matrix_pictures[presentation_order[order]]
#                 if card != expected_card:
#                     cards_answer[expected_card] = 'noResponse'
#                     cards_bool_answer[expected_card] = 'noResponse'
#                     cards_reaction_time[expected_card] = 'noResponse'
#                     order += 1
#                 show_time = int(re.search('timing_([0-9]+)', event).group(1))
#                 if ttl_timestamp is not None:
#                     show_card_absolute_time[card] = show_time - ttl_timestamp
#                 else:
#                     show_card_absolute_time[card] = show_time
#                 cards_order[card] = order
#             elif 'HideCard' in event:
#                 hidden_card = re.search('(?<=card_)\w+', event).group(0)
#                 hide_time = int(re.search('timing_([0-9]+)', event).group(1))
#                 if ttl_timestamp is not None:
#                     hide_card_absolute_time[hidden_card] = reaction_start = hide_time - ttl_timestamp
#                 else:
#                     hide_card_absolute_time[hidden_card] = reaction_start = hide_time
#             elif 'ERROR' in event:
#                 cards_answer[card] = 'ERROR'
#                 cards_bool_answer[card] = 'ERROR'
#                 cards_reaction_time[card] = 'ERROR'
#                 order += 1
#             elif 'NoResponse' in event:
#                 cards_answer[card] = 'noResponse'
#                 cards_bool_answer[card] = 'noResponse'
#                 cards_reaction_time[card] = 'noResponse'
#                 order += 1
#             elif 'Response' in event:
#                 response = int(re.search('responded-([0-9]+)', event).group(1))
#                 cards_answer[card] = true_sounds[sounds_order[response]]
#                 response_time = int(re.search('timing_([0-9]+)', event).group(1))
#                 if ttl_timestamp is not None:
#                     response_time = response_time - ttl_timestamp
#                 cards_reaction_time[card] = response_time - reaction_start
#
#                 bool_answer = re.search('(?<=Response_correct-)\w+', event).group(0)
#                 if bool_answer[0:5] == 'False':
#                     bool_answer = False
#                 elif bool_answer[0:4] == 'True':
#                     bool_answer = True
#                 else:
#                     bool_answer = 'ERROR'
#                 cards_bool_answer[card] = bool_answer
#                 order += 1
#         if 'StartExp' in event:
#             experiment_started = 1
#
#     return cards_order, cards_answer, cards_bool_answer, cards_reaction_time,\
#            show_card_absolute_time, hide_card_absolute_time


def write_csv(output_file, matrix_pictures,
              classes_order=None, sounds_order=None, classes_to_sounds_index=None,
              days=None, number_blocks=0,
              cards_order=None, cards_distance_to_correct_card=None, position_response_reaction_time=None,
              show_card_absolute_time=None,
              hide_card_absolute_time=None,
              cards_learning_order=None,
              show_card_learning_absolute_time=None,
              hide_card_learning_absolute_time=None,
              matrices_presentation_order=None,
              days_not_reached=[False]*3,
              subject_id=None,
              day=None):

    if days is None:
        days = []
    i_csv = csv.writer(open(output_file, "w", newline=''))

    first_row = list(first_column_titles)


    if not days:
        block_range = range(number_blocks)
        for i in block_range:
            learning_titles = ['Learning_Block' + str(i) + '_matrixA_test_order'] + \
                ['Learning_Block' + str(i) + '_matrixA_CueCard' + str(cuecard_index) for
                 cuecard_index in range(len(classPictures))] + \
                ['Learning_Block' + str(i) + '_CueCardResponseImage',
                 'Learning_Block' + str(i) + '_CueCardResponseCorrect',
                 'Learning_Block' + str(i) + '_CueCardReactionTime',
                 'Learning_Block' + str(i) + '_matrixA_X_clicked',
                 'Learning_Block' + str(i) + '_matrixA_Y_clicked',
                 'Learning_Block' + str(i) + '_matrixA_distanceToMatrixA',
                 'Learning_Block' + str(i) + '_matrixA_positionResponse_ReactionTime',
                 'Learning_Block' + str(i) + '_matrixA_test_ShowTime',
                 'Learning_Block' + str(i) + '_matrixA_test_HideTime',
                 'Learning_Block' + str(i) + '_matrixA_presentation_order',
                 'Learning_Block' + str(i) + '_matrixA_presentation_matrixPresentationOrder',
                 'Learning_Block' + str(i) + '_matrixA_PresentationShowTime',
                 'Learning_Block' + str(i) + '_matrixA_PresentationHideTime']
            first_row.extend(learning_titles)
            len_learning_titles = len(learning_titles)
    else:
        test_recall_titles = ['TestRecall_' + item for item in test_recall_suffixes]
        retest_recall_titles = ['RetestRecall_' + item for item in test_recall_suffixes]
        first_row.extend(
            test_recall_titles + retest_recall_titles + recognition_column_titles)

    i_csv.writerow(first_row)
    if not days:
        write_csv_learning(i_csv, matrix_pictures, cards_order, matrices_presentation_order,
                           cards_distance_to_correct_card, position_response_reaction_time,
                           show_card_absolute_time, hide_card_absolute_time, number_blocks,
                           cards_learning_order, show_card_learning_absolute_time, hide_card_learning_absolute_time,
                           classes_order=classes_order, sounds_order=sounds_order,
                           classes_to_sounds_index=classes_to_sounds_index,
                           subject_id=subject_id,
                           day=day, len_learning_titles=len_learning_titles)
    else:
        write_csv_test(i_csv, matrix_pictures, classes_order, days, days_not_reached)


def write_csv_learning(i_csv, matrix_pictures, cards_order, matrices_presentation_order,
                       cards_distance_to_correct_card, position_response_reaction_time,
                       show_card_absolute_time, hide_card_absolute_time, number_blocks,
                       cards_learning_order, show_card_learning_absolute_time, hide_card_learning_absolute_time,
                       classes_order=None, sounds_order=None, subject_id=None, classes_to_sounds_index=None, day=None,
                       len_learning_titles=None):
    cards = sum(matrix_pictures, [])
    cards.sort()
    for card in cards:
        # Add item; Add category
        try:
            card = card.rstrip('.png')
        except AttributeError:  # card already is without .png at the end
            pass
        card_class = card[0]
        sound = true_sounds[classes_to_sounds_index[card_class]]
        matrix_index = classes_order.index(card_class)
        position = (matrix_pictures[matrix_index]).index(card)
        matrixA_coord = matrix_index_to_xy_coordinates(position)
        item_list = [subject_id, card, card_class, sound, number_blocks, matrixA_coord[0], matrixA_coord[1], None, None]
        # add answers and card orders
        for block_number in range(number_blocks):
            matrix_presentation_order_index = classes_order.index(card_class)
            try:
                matrix_presentation_order = (matrices_presentation_order[block_number]['presentation'])\
                    .index(matrix_presentation_order_index)
            except ValueError:
                matrix_presentation_order = 'noPresentation'
            try:
                if day.position_response_index_responded[block_number][card].isnumeric():
                    XY_clicked_coord = list(
                        matrix_index_to_xy_coordinates(int(day.position_response_index_responded[block_number][card])))
                elif day.position_response_index_responded[block_number][card] == 'noResponse':
                    XY_clicked_coord = ['noResponse'] * 2
                elif day.position_response_index_responded[block_number][card] == 'wrongCueCard':
                    XY_clicked_coord = ['wrongCueCard'] * 2
                else:
                    XY_clicked_coord = ['script_failed_extract_data'] * 2
                item_list.extend(
                    [cards_order[block_number][card]] +
                    [day.cuecard_presented_image[block_number][cuecard_index][card]
                     for cuecard_index in range(len(classPictures))] +
                    [day.cuecard_response_image[block_number][card],
                     day.cuecard_response_correct[block_number][card],
                     day.cuecards_reaction_time[block_number][card]] +
                    XY_clicked_coord +
                    [cards_distance_to_correct_card[block_number][card],
                     position_response_reaction_time[block_number][card],
                     show_card_absolute_time[block_number][card],
                     hide_card_absolute_time[block_number][card]]
                )
            except KeyError:
                item_list.extend(['script_failed_extract_data'] * (len_learning_titles - 4))
            try:
                item_list.extend(
                     [cards_learning_order[block_number][card],
                     matrix_presentation_order,
                     show_card_learning_absolute_time[block_number][card],
                     hide_card_learning_absolute_time[block_number][card]
                     ]
                )
            except KeyError:
                if matrix_presentation_order == 'noPresentation':
                    item_list.extend(['noPresentation'] * 4)
                else:
                    item_list.extend(['script_failed_extract_data']*4)
        i_csv.writerow(item_list)


def write_csv_test(i_csv, matrix_pictures, classes_order, days, days_not_reached):
    cards = sum(matrix_pictures, [])
    cards.sort()
    for card in cards:
        # Add item; Add category
        try:
            card = card.rstrip('.png')
        except AttributeError:
            pass
        card_class = card[0]
        matrix_index = classes_order.index(card_class)
        position = (matrix_pictures[matrix_index]).index(card)
        matrixA_coord = matrix_index_to_xy_coordinates(position)
        item_list = [None, card, card_class, None, matrixA_coord[0], matrixA_coord[1], None, None]
        sound_not_added = True
        for i in range(len(days)):
            day = days[i]
            if days_not_reached[i]:
                if not day.recognition:
                    item_list.extend(['noFile'] * len(test_recall_suffixes))
                else:
                    item_list.extend(['noFile'] * len(recognition_column_titles))
            else:
                try:
                    for j in range(len(day.classes_order)):
                        if day.classes_order[j] == card_class:
                            sound = true_sounds[day.classes_to_sounds_index[card_class]]
                            if sound_not_added:
                                item_list.insert(sound_title_index, sound)
                                sound_not_added = False
                except:
                    item_list.insert(sound_title_index, 'soundNotFound')
                try:
                    if not day.recognition:
                        if day.position_response_index_responded[0][card].isnumeric():
                            XY_clicked_coord = list(
                                matrix_index_to_xy_coordinates(int(day.position_response_index_responded[0][card])))
                        elif day.position_response_index_responded[0][card] == 'noResponse':
                            XY_clicked_coord = ['noResponse'] * 2
                        elif day.position_response_index_responded[0][card] == 'wrongCueCard':
                            XY_clicked_coord = ['wrongCueCard'] * 2
                        else:
                            XY_clicked_coord = ['script_failed_extract_data'] * 2
                        item_list.extend(
                            [day.cards_order[0][card]] +
                            [day.cuecard_presented_image[0][cuecard_index][card]
                             for cuecard_index in range(len(classPictures))] +
                            [day.cuecard_response_image[0][card],
                             day.cuecard_response_correct[0][card],
                             day.cuecards_reaction_time[0][card]] +
                            XY_clicked_coord +
                            [day.cards_distance_to_correct_card[0][card],
                             day.position_response_reaction_time[0][card], day.show_card_absolute_time[0][card],
                             day.hide_card_absolute_time[0][card]])
                    else:
                        item_list.extend([day.matrix_presentation_order[classes_order.index(card_class)],
                                          day.cards_order[card],
                                          day.cards_answer[card],
                                          day.cards_reaction_time[card], day.show_card_absolute_time[card],
                                          day.hide_card_absolute_time[card],

                                          day.recognition_cards_order[card], day.recognition_answer[card],
                                          day.recognition_cards_reaction_time[card],
                                          day.show_recognition_card_absolute_time[card],
                                          day.hide_recognition_card_absolute_time[card],
                                          day.cards_distance_to_correct_card[card]])
                        position = day.recognition_matrices[matrix_index].index(card)
                        matrixR_coord = matrix_index_to_xy_coordinates(position)
                        item_list[6] = matrixR_coord[0]
                        item_list[7] = matrixR_coord[1]
                except KeyError:
                    if not day.recognition:
                        item_list.extend(['script_failed_extract_data'] * len(test_recall_suffixes))
                    else:  # Recognition
                        item_list.extend(['script_failed_extract_data'] * len(recognition_column_titles))

        i_csv.writerow(item_list)


def extract_correct_answers(i_folder, i_file):
    agg = data_preprocessing.Aggregator(data_folder=i_folder, file_name=i_file)
    header = data_preprocessing.read_datafile(i_folder + i_file, only_header_and_variable_names=True)

    # Extracting pictures' positions in the matrix
    header = header[3].split('\n#e ')
    matrix_pictures = ast.literal_eval(header[header.index('Positions pictures:') + 1].split('\n')[0].split('\n')[0])
    matrix_pictures = [element for element in matrix_pictures if element is not None]

    # Extracting data
    data = {}
    for variable in agg.variables:
        data[variable] = agg.get_variable_data(variable)

    block_indexes = np.unique(data['NBlock'])
    for block in block_indexes:
        correct_answers = np.logical_and(data['Picture'] == data['Answers'], data['NBlock'] == block)
        wrong_answers = np.logical_and(data['Picture'] != data['Answers'], data['NBlock'] == block)

    # list(set(my_list)) is one of the smoothest way to eliminate duplicates
    classes = list(set([element[0] for element in matrix_pictures if element is not None]))
    classes = list(np.sort(classes))  # Order the classes

    valid_cards = CorrectCards()
    invalid_cards = WrongCards()
    for idx, val in enumerate(correct_answers):
        if val:
            valid_cards.answer.append(data['Answers'][idx][0])
            valid_cards.position.append(matrix_pictures.index(data['Answers'][idx]))

    for idx, val in enumerate(wrong_answers):
        if val:
            invalid_cards.answer.append(data['Answers'][idx][0])
            invalid_cards.picture.append(data['Picture'][idx][0])
            if 'None' in data['Answers'][idx][0]:
                invalid_cards.position.append(100)
            else:
                invalid_cards.position.append(matrix_pictures.index(data['Answers'][idx]))

    for idx, val in enumerate(wrong_answers):
        if val:
            invalid_cards.answer.append(data['Answers'][idx][0])
            invalid_cards.picture.append(data['Picture'][idx][0])
            if 'None' in data['Answers'][idx][0]:
                invalid_cards.position.append(100)
            else:
                invalid_cards.position.append(matrix_pictures.index(data['Answers'][idx]))

    for element in classes:
        valid_cards.element = [word for word in valid_cards.answer if word[0] == element]
        invalid_cards.element = [word for word in invalid_cards.picture if word[0] == element]

    return matrix_pictures, data, valid_cards, invalid_cards, len(block_indexes)


def merge_csv(output_file, csv_list):
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        rows = {k: [] for k in range(1+len(matrixTemplate)*len(classPictures))}
        for i, fname in enumerate(csv_list):
            try:
                with open(fname, 'r', newline='') as infile:
                    reader = csv.reader(infile)
                    for j, row in enumerate(reader):
                        if i == 0:
                            rows[j] += row
                        else:
                            rows[j] += row[len(first_column_titles):]
                        # see first_row
                        if row[number_learning_blocks_index] is not None:
                            rows[j][number_learning_blocks_index] = row[number_learning_blocks_index]
                        if row[0] is not None:
                            rows[j][0] = row[0]
            except IOError:
                pass
        for j in range(len(rows)):
            writer.writerow(rows[j])


def delete_temp_csv(temp_csv):
    for temp_file in temp_csv:
        try:
            os.remove(temp_file)
        except IOError:
            pass
        except WindowsError:
            pass
