import os as os
import sys
import glob

from ld_utils import Day, extract_matrix_and_data, extract_events, recognition_extract_events, \
    write_csv, merge_csv, delete_temp_csv
from src.declarativeTask3.ld_utils import export_encoding_results

rawFolder = os.path.dirname(__file__)
rawdata_folder = os.path.join(rawFolder, 'rawdata')

# ***INSTRUCTIONS***
# Please input the location of the subject folder containing the data you wish to convert to .csv format
# e.g. You are in DeCoNap/ and you wish to convert data located in DeCoNap/data/subject_41/
# Please input: python ld_analysis.py data/subject_41

# Output csv file will be created in the preprocessed_data folder and will have the same name as the directory you
# specified
# In this example, Output will be:  <subject_41_preprocessed_data.csv> <DeCoNap/data/subject_41_preprocessed_data.csv>

sep = os.path.sep
#
# Declaring <subject_folder> and <outputFile> variables, which are self-explanatory
subject_location = sys.argv[1]
subject_id = os.path.basename(subject_location).replace('sub-', '')

subject_folder = os.path.abspath(os.path.join(os.getcwd(), subject_location))

output_file = os.path.abspath(os.path.join(rawdata_folder, subject_id + '_preprocessed_data.csv'))
output_file_tests = os.path.abspath(os.path.join(rawdata_folder, subject_id + '_tests&recognition.csv'))
output_file_learning = os.path.abspath(os.path.join(rawdata_folder, subject_id + '_learning.csv'))

# Gathering all subject files
allFiles = glob.glob(os.path.join(subject_folder, '*', 'beh', '*.xpd'))
# print('\n\n')
# print([file for file in allFiles if 'Encoding' in file])
# encodingFiles = []
# associationFiles = []
# for iFile in allFiles:
#     # if 'EXCLUDED' not in iFile and os.path.isfile(subject_location + sep + iFile):
#     if 'EXCLUDED' not in iFile and os.path.isfile(iFile):
#         if 'ld_recognition' in iFile and '.xpd' in iFile:
#             recognitionFile = iFile
#             encodingFiles.append(recognitionFile)
#         if 'ld_association_learning' in iFile and '.xpd' in iFile:
#             associationFiles.append(iFile)
#         if 'ld_encoding' in iFile and '.xpd' in iFile:
#             encodingFiles.append(iFile)

day1_learning = Day(learning=True)

day2_test = Day()
day2_test_not_reached = True
day3_test = Day()
day3_test_not_reached = True
day3_recognition = Day(recognition=True)
day3_recognition_not_reached = True
day3_association = Day(association=True)
day3_association_not_reached = True

day1_association = Day(association=True)
day1_association_not_reached = True
day1_test_association = Day(test_association=True)
day1_test_association_not_reached = True

ttl_learning = None

# for iFile in allFiles:
for iFile in allFiles:
    # header = data_preprocessing.read_datafile(subject_folder + iFile, only_header_and_variable_names=True)
    # header[3].split('\n#e ')

    # for field in header:
    if 'task-' + "Encoding" in iFile:
        events, matrices, matrix_size, classes_order, sounds_order, classes_to_sounds_index, ttl_timestamp = \
            extract_matrix_and_data(subject_folder, iFile, learning=True)

        try:
            day1_learning.cards_order, day1_learning.cards_distance_to_correct_card,\
                day1_learning.position_response_reaction_time,\
                day1_learning.number_blocks, day1_learning.show_card_absolute_time, \
                day1_learning.hide_card_absolute_time,\
                day1_learning.show_card_learning_absolute_time,\
                day1_learning.hide_card_learning_absolute_time,\
                day1_learning.cards_learning_order,\
                day1_learning.matrices_presentation_orders,\
                day1_learning.cards_position, \
                day1_learning.position_response_index_responded, \
                day1_learning.cuecard_presented_image, \
                day1_learning.cuecard_response_image, \
                day1_learning.cuecard_response_correct,\
                day1_learning.cuecards_reaction_time,\
                correctAnswers_CorrectSoundChosen, correctAnswers_CorrectLocationChosen = \
                extract_events(events, matrix_size, classes_order, ttl_timestamp=ttl_timestamp, mode='learning')
        except UnboundLocalError:  # Missing data
            continue

        write_csv(output_file_learning, matrices, number_blocks=day1_learning.number_blocks,
                  cards_order=day1_learning.cards_order,
                  matrices_presentation_order=day1_learning.matrices_presentation_orders,
                  cards_distance_to_correct_card=day1_learning.cards_distance_to_correct_card,
                  position_response_reaction_time=day1_learning.position_response_reaction_time,
                  show_card_absolute_time=day1_learning.show_card_absolute_time,
                  hide_card_absolute_time=day1_learning.hide_card_absolute_time,
                  show_card_learning_absolute_time=day1_learning.show_card_learning_absolute_time,
                  hide_card_learning_absolute_time=day1_learning.hide_card_learning_absolute_time,
                  cards_learning_order=day1_learning.cards_learning_order,
                  classes_order=classes_order,
                  sounds_order=sounds_order,
                  classes_to_sounds_index=classes_to_sounds_index,
                  subject_id=subject_id,
                  day=day1_learning)

        export_encoding_results(
            subject_id, 'expePreNap', 'Encoding', rawdata_folder, day1_learning.number_blocks,
            correctAnswers_CorrectSoundChosen, correctAnswers_CorrectLocationChosen)
        del correctAnswers_CorrectSoundChosen, correctAnswers_CorrectLocationChosen

    if 'task-' + "Test-Encoding" in iFile:
        day2_test.events, day2_test.matrices, day2_test.matrix_size, \
            day2_test.classes_order, day2_test.sounds_order, day2_test.classes_to_sounds_index,\
            day2_test.ttl_in_data = \
            extract_matrix_and_data(subject_folder, iFile)

        day2_test.cards_order, day2_test.cards_distance_to_correct_card, day2_test.position_response_reaction_time,\
            day2_test.number_blocks, day2_test.show_card_absolute_time, \
            day2_test.hide_card_absolute_time, \
            day2_test.cuecard_presented_image, day2_test.cuecard_response_image, \
            day2_test.cuecard_response_correct, day2_test.cuecards_reaction_time, \
            day2_test.position_response_index_responded, day2_test.cards_position,\
            correctAnswers_CorrectSoundChosen, correctAnswers_CorrectLocationChosen = \
            extract_events(day2_test.events, day2_test.matrix_size, classes_order,
                           ttl_timestamp=day2_test.ttl_in_data)
        day2_test_not_reached = False

        export_encoding_results(
            subject_id, 'expePreNap', 'Test-Encoding', rawdata_folder, day1_learning.number_blocks,
            correctAnswers_CorrectSoundChosen, correctAnswers_CorrectLocationChosen)
        del correctAnswers_CorrectSoundChosen, correctAnswers_CorrectLocationChosen

    if 'task-' + "ReTest-Encoding" in iFile:
        day3_test.events, day3_test.matrices, day3_test.matrix_size, \
            day3_test.classes_order, day3_test.sounds_order, day3_test.classes_to_sounds_index,\
            day3_test.ttl_in_data = \
            extract_matrix_and_data(subject_folder, iFile)

        day3_test.cards_order, day3_test.cards_distance_to_correct_card, day3_test.position_response_reaction_time,\
            day3_test.number_blocks, day3_test.show_card_absolute_time, \
            day3_test.hide_card_absolute_time, \
            day3_test.cuecard_presented_image, day3_test.cuecard_response_image, \
            day3_test.cuecard_response_correct, day3_test.cuecards_reaction_time, \
            day3_test.position_response_index_responded, day3_test.cards_position,\
            correctAnswers_CorrectSoundChosen, correctAnswers_CorrectLocationChosen = \
            extract_events(day3_test.events, day3_test.matrix_size, day3_test.classes_order,
                           ttl_timestamp=day3_test.ttl_in_data)
        day3_test_not_reached = False

        export_encoding_results(
            subject_id, 'expePostNap', 'ReTest-Encoding', rawdata_folder, day1_learning.number_blocks,
            correctAnswers_CorrectSoundChosen, correctAnswers_CorrectLocationChosen)
        del correctAnswers_CorrectSoundChosen, correctAnswers_CorrectLocationChosen

    if 'task-' + "DayOne-Recognition" in iFile:
        try:
            day3_recognition.events, day3_recognition.matrices, day3_recognition.matrix_size, \
                day3_recognition.classes_order, day3_recognition.sounds_order, \
                day3_recognition.classes_to_sounds_index, \
                day3_recognition.recognition_matrices, matrices_a_or_rec, \
                presentation_orders, day3_recognition.ttl_in_data,\
                day3_recognition.matrix_presentation_order =\
                extract_matrix_and_data(subject_folder, iFile, recognition=True)

            day3_recognition.cards_order, day3_recognition.cards_answer, day3_recognition.cards_reaction_time, \
                day3_recognition.show_card_absolute_time, day3_recognition.hide_card_absolute_time,\
                day3_recognition.recognition_cards_order, day3_recognition.recognition_answer,\
                day3_recognition.recognition_cards_reaction_time,\
                day3_recognition.show_recognition_card_absolute_time,\
                day3_recognition.hide_recognition_card_absolute_time,\
                day3_recognition.cards_distance_to_correct_card\
                = recognition_extract_events(day3_recognition.events, day3_recognition.matrices,
                                             day3_recognition.recognition_matrices, matrices_a_or_rec,
                                             presentation_orders,
                                             day3_recognition.matrix_size,
                                             ttl_timestamp=day3_recognition.ttl_in_data,
                                             )
            day3_recognition_not_reached = False
        except ValueError:  # experiment was interrupted and data is missing
            pass

# for iFile in associationFiles:
#     header = data_preprocessing.read_datafile(subject_folder + iFile, only_header_and_variable_names=True)
#     header[3].split('\n#e ')
#
#     for field in header:
#         if "Association-Learning" in field and "Experiment" in field and not ("Test-Association-Learning" in field):
#             day1_association.classes_order, day1_association.sounds_order,\
#                 day1_association.classes_to_sounds_index, day1_association.trial_reaction_time,\
#                 day1_association.trial_other_card1, day1_association.trial_other_card2, \
#                 day1_association.trial_number_responses = \
#                 extract_association_data(subject_folder, iFile, matrices, learning=True)
#             day1_association_not_reached = False
#             break
#         if "Test-Association-Learning" in field and "Experiment" in field:
#             day1_test_association.classes_order, day1_test_association.sounds_order, \
#                 day1_test_association.classes_to_sounds_index, day1_test_association.trial_reaction_time, \
#                 day1_test_association.trial_other_card1, day1_test_association.trial_other_card2, \
#                 day1_test_association.trial_response_correct, day1_test_association.trial_response_card = \
#                 extract_association_data(subject_folder, iFile, matrices, test=True)
#             day1_test_association_not_reached = False
#             break

write_csv(output_file_tests, matrices, days=[day2_test, day3_test, day3_recognition],
          days_not_reached=[day2_test_not_reached, day3_test_not_reached,
                            day3_recognition_not_reached],
          classes_order=classes_order)

temp_csv = [output_file_tests] + [output_file_learning]

merge_csv(output_file, temp_csv)

delete_temp_csv(temp_csv)

# as a rule of thumb, for 'DayRec_MatrixA_answer' and 'DayRec_matrixRec_answer', remember that
# 0 means "the subject made a mistake"
# 1 means "the subject got it right"
# 1 in 'DayRec_matrixRec_answer' means the subject clicked "Wrong" when presented with the wrong position. And 0, that
# they were mistaken
