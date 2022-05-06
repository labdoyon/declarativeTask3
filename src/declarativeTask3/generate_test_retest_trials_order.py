import os
import sys
import pickle
import random

from declarativeTask3.config import rawFolder, sessions, classPictures, matrixSize, windowSize, tasks_to_generate, \
    experiment_session
from declarativeTask3.ld_utils import normalize_test_presentation_order, getPreviousMatrix
from declarativeTask3.ld_matrix import LdMatrix

# need subject name and session
subjectName = sys.argv[1]
session = sessions[0]

matrices = []
pictures_allocation = []
for i, category in enumerate(classPictures):
    previousMatrix = getPreviousMatrix(subjectName, 0, 'generate-matrix', i, category)
    if previousMatrix is None:
        raise TypeError("no previous matrix found")
    matrices.append(LdMatrix(matrixSize, windowSize))  # Create matrices
    pictures_allocation.append(matrices[i].findMatrix(category, previousMatrix=previousMatrix, keep=True))

for task in tasks_to_generate:
    pictures_allocation = [list(picture_matrix) for picture_matrix in pictures_allocation]
    pictures_allocation = [[card.rstrip('.png') for card in picture_matrix] for picture_matrix in
                           pictures_allocation]
    trials_order = sum(pictures_allocation, [])
    trials_order = [card.rstrip('.png') for card in trials_order]
    random.shuffle(trials_order)
    trials_order = normalize_test_presentation_order(trials_order, pictures_allocation)

    if task[:len('Encoding')] == 'Encoding':
        session = 'expePreNap'
    else:
        session = experiment_session[task]
    output_folder = os.path.normpath(os.path.join(
        rawFolder, 'sourcedata', 'sub-' + subjectName, 'ses-' + session, 'beh'))
    session_dir = os.path.normpath(os.path.join(rawFolder, 'sourcedata', 'sub-' + subjectName, 'ses-' + session))
    output_dir = os.path.normpath(os.path.join(session_dir, 'beh'))
    if not os.path.isdir(session_dir):
        os.mkdir(session_dir)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    trials_file = os.path.join(output_folder, task + '_trials.pkl')
    with open(trials_file, 'wb') as f:
        pickle.dump(trials_order, f)
