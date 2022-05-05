import sys
import os

import expyriment

from declarativeTask3.config import classPictures, matrixSize, windowSize, sessions, experiment_session
from declarativeTask3.ld_utils import getPreviousMatrix, generate_bids_filename
from declarativeTask3.ld_matrix import LdMatrix

subjectName = sys.argv[1]

# session = sessions[0]
# output_folder = os.path.normpath(os.path.join(rawFolder, 'sourcedata', 'sub-' + subjectName, 'ses-' + session, 'beh'))

matrices = []
pictures_allocation = []
for i, category in enumerate(classPictures):
    previousMatrix = getPreviousMatrix(subjectName, 0, 'generate-matrix', i, category)
    # previousMatrix will be <None> if there is no previous matrix, the findMatrix function will generate a new matrix
    # if it is fed <None> as previousMatrix
    matrices.append(LdMatrix(matrixSize, windowSize))  # Create matrices
    pictures_allocation.append(matrices[i].findMatrix(category, previousMatrix=previousMatrix, keep=True))
    # Find pictures_allocation
    matrices[i].associateCategory(category)

# with open(os.path.join(output_folder, 'matrices.pkl'), 'wb') as f:
#     pickle.dump(pictures_allocation, f)

expyriment.control.set_develop_mode(on=True, intensive_logging=False, skip_wait_methods=True)
experiment_name = 'generate-matrix'
exp = expyriment.design.Experiment(experiment_name)  # Save experiment name

session = experiment_session[experiment_name]
session_dir = os.path.normpath(os.path.join('sourcedata', 'sub-' + subjectName, 'ses-' + session))
output_dir = os.path.normpath(os.path.join(session_dir, 'beh'))
if not os.path.isdir(session_dir):
    os.mkdir(session_dir)
expyriment.io.defaults.datafile_directory = output_dir
expyriment.io.defaults.eventfile_directory = output_dir

exp.add_experiment_info('Subject: ')  # Save Subject Code
exp.add_experiment_info(subjectName)
exp.add_experiment_info('Image classes order:')
exp.add_experiment_info(str(classPictures))

expyriment.control.initialize(exp)
i = 1
wouldbe_datafile = generate_bids_filename(
    subjectName, session, experiment_name, filename_suffix='_beh', filename_extension='.xpd')
wouldbe_eventfile = generate_bids_filename(
    subjectName, session, experiment_name, filename_suffix='_events', filename_extension='.xpe')

while os.path.isfile(os.path.join(expyriment.io.defaults.datafile_directory, wouldbe_datafile)) or \
        os.path.isfile(os.path.join(expyriment.io.defaults.eventfile_directory, wouldbe_eventfile)):
    i += 1
    i_string = '0' * (2 - len(str(i))) + str(i)  # 0 padding, assuming 2-digits number
    wouldbe_datafile = generate_bids_filename(subjectName, session, experiment_name, filename_suffix='_beh',
                                              filename_extension='.xpd', run=i_string)
    wouldbe_eventfile = generate_bids_filename(subjectName, session, experiment_name, filename_suffix='_events',
                                               filename_extension='.xpe', run=i_string)

expyriment.control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)
for i, category in enumerate(classPictures):
    matrices[i].associatePictures(pictures_allocation[i])  # Associate Pictures to cards
    exp.add_experiment_info('matrix {}, pictures from class {}:'.format(i, category))
    exp.add_experiment_info(str(matrices[i].listPictures))  # Add listPictures
exp.data.rename(wouldbe_datafile)
exp.events.rename(wouldbe_eventfile)
expyriment.control.end()
