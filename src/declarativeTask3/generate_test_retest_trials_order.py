import os
import sys
import pickle
import random

from declarativeTask3.config import rawFolder, sessions
from declarativeTask3.ld_utils import normalize_test_presentation_order


# need subject name and session
subjectName = sys.argv[1]
session = sessions[0]
matrices_file = os.path.normpath(os.path.join(
    rawFolder, 'sourcedata', 'sub-' + subjectName, 'ses-' + session, 'beh', 'matrices.pkl'))
with open(matrices_file, "rb") as f:
    pictures_allocation = pickle.load(f)

# generating trials for test-encoding
pictures_allocation = [list(picture_matrix) for picture_matrix in pictures_allocation]
pictures_allocation = [[card.rstrip('.png') for card in picture_matrix] for picture_matrix in
                       pictures_allocation]
trials_order = sum(pictures_allocation, [])
trials_order = [card.rstrip('.png') for card in trials_order]
random.shuffle(trials_order)
trials_order = normalize_test_presentation_order(trials_order, pictures_allocation)

session = 'expePreNap'
output_folder = os.path.normpath(os.path.join(
    rawFolder, 'sourcedata', 'sub-' + subjectName, 'ses-' + session, 'beh'))
session_dir = os.path.normpath(os.path.join(rawFolder, 'sourcedata', 'sub-' + subjectName, 'ses-' + session))
output_dir = os.path.normpath(os.path.join(session_dir, 'beh'))
if not os.path.isdir(session_dir):
    os.mkdir(session_dir)
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
test_encoding_trials_file = os.path.normpath(os.path.join(output_folder, 'test-encoding-trials.pkl'))
with open(test_encoding_trials_file, 'wb') as f:
    pickle.dump(trials_order, f)

# generating trials for retest-encoding
pictures_allocation = [list(picture_matrix) for picture_matrix in pictures_allocation]
pictures_allocation = [[card.rstrip('.png') for card in picture_matrix] for picture_matrix in
                       pictures_allocation]
trials_order = sum(pictures_allocation, [])
trials_order = [card.rstrip('.png') for card in trials_order]
random.shuffle(trials_order)
trials_order = normalize_test_presentation_order(trials_order, pictures_allocation)

session = 'expePostNap'
output_folder = os.path.normpath(os.path.join(
    rawFolder, 'sourcedata', 'sub-' + subjectName, 'ses-' + session, 'beh'))
session_dir = os.path.normpath(os.path.join(rawFolder, 'sourcedata', 'sub-' + subjectName, 'ses-' + session))
output_dir = os.path.normpath(os.path.join(session_dir, 'beh'))
if not os.path.isdir(session_dir):
    os.mkdir(session_dir)
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
retest_encoding_trials_file = os.path.normpath(os.path.join(output_folder, 'retest-encoding-trials.pkl'))
with open(retest_encoding_trials_file, 'wb') as f:
    pickle.dump(trials_order, f)
