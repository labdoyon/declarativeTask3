from cursesmenu import *
from cursesmenu.items import *
import sys
import os
import glob
import numpy as np
from ast import literal_eval

from datetime import datetime
import expyriment
from dateutil.parser import parse

sep = os.path.sep

rawFolder = os.getcwd() + os.path.sep
subjectName = sys.argv[1]
sessions = ['expePreNap', 'expePostNap']
experiment_session = {
    'choose-sound-association': 'expePreNap',
    'Example':              'expePreNap',
    'Encoding':             'expePreNap',
    'Test-Encoding':        'expePreNap',
    'ReTest-Encoding':      'expePostNap',
    'DayOne-Recognition':   'expePostNap'}
subject_dir = rawFolder + 'sourcedata' + sep + 'sub-' + subjectName + sep
if not os.path.isdir(subject_dir):
    os.mkdir(subject_dir)
dataFolder = rawFolder + 'data' + os.path.sep
sounds = ['shortest-1-100ms.wav', 'shortest-2-100ms.wav', 'shortest-3-100ms.wav']
classPictures = ['a', 'b', 'c']
classNames = {'english': {'a': 'animals', 'b': 'household', 'c': 'clothes'},
              'french': {'a': 'animaux', 'b': 'maison', 'c': 'vêtements'},
              None: {'a': 'a', 'b': 'b', 'c': 'c'}}
soundNames = {
    None: {0: 'S1', 1: 'S2', 2: 'S3'},
    'english': {0: 'standard', 1: 'noise', 2: 'A'},
    'french': {0: 'standard', 1: 'bruit', 2: 'A'}}


def generate_bids_filename(subject_id, session, task, filename_suffix='_beh', filename_extension='.xpd',
                           run=None):
    if run is None:
        return 'sub-' + subject_id + '_ses-' + session + '_task-' + task + filename_suffix + filename_extension
    else:
        return 'sub-' + subject_id + '_ses-' + session + '_task-' + task +\
               '_run-' + str(run) +\
               filename_suffix + filename_extension


def getPrevious(subjectName, daysBefore, experienceName, target):
    currentDate = datetime.now()
    output = None

    data_files = []
    for session in sessions:
        session_dir = subject_dir + 'ses-' + session + sep + 'beh' + sep
        if os.path.isdir(session_dir):
            data_files = data_files + \
                         [session_dir + file for file in os.listdir(session_dir) if file.endswith('_beh.xpd')]

    for dataFile in data_files:
        agg = expyriment.misc.data_preprocessing.read_datafile(dataFile, only_header_and_variable_names=True)
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
                except:  # string
                    output = previousTarget

    # This ensures the latest language choice (or other information) is used, as, if several files have been generated,
    # they should be named <something> <something>_run-02.xpd , <something>_run-03.xpd , etc. etc. And since files are
    # sorted in alphabetical order, the <output> variable that will be returned is the one from the latest file,
    # both alphabetical-wise, run-wise, and time-wise
    return output


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


language = getPrevious(subjectName, 0, 'choose-language', 'language:')

soundsAllocation_index = getPrevious(subjectName, 0, 'choose-sound-association', 'Image classes to sounds (index):')
if soundsAllocation_index is None:
    soundsAllocation_index, soundsAllocation = newSoundAllocation()
    expyriment.control.set_develop_mode(on=True, intensive_logging=False, skip_wait_methods=True)
    experiment_name = 'choose-sound-association'
    exp = expyriment.design.Experiment(experiment_name)  # Save experiment name

    session = experiment_session[experiment_name]
    session_dir = 'sourcedata' + os.path.sep + \
                  'sub-' + subjectName + os.path.sep + \
                  'ses-' + session + os.path.sep
    output_dir = session_dir + 'beh'
    if not os.path.isdir(session_dir):
        os.mkdir(session_dir)
    expyriment.io.defaults.datafile_directory = output_dir
    expyriment.io.defaults.eventfile_directory = output_dir

    exp.add_experiment_info('Subject: ')  # Save Subject Code
    exp.add_experiment_info(subjectName)
    exp.add_experiment_info('Image classes order:')
    exp.add_experiment_info(str(classPictures))
    exp.add_experiment_info('Sounds order:')
    exp.add_experiment_info(str(sounds))
    exp.add_experiment_info('Image classes to sounds:')
    exp.add_experiment_info(str(soundsAllocation))
    exp.add_experiment_info('Image classes to sounds (index):')
    exp.add_experiment_info(str(soundsAllocation_index))
    expyriment.control.initialize(exp)
    i = 1
    wouldbe_datafile = generate_bids_filename(
        subjectName, session, experiment_name, filename_suffix='_beh', filename_extension='.xpd')
    wouldbe_eventfile = generate_bids_filename(
        subjectName, session, experiment_name, filename_suffix='_events', filename_extension='.xpe')

    while os.path.isfile(expyriment.io.defaults.datafile_directory + sep + wouldbe_datafile) or \
            os.path.isfile(expyriment.io.defaults.eventfile_directory + sep + wouldbe_eventfile):
        i += 1
        i_string = '0' * (2 - len(str(i))) + str(i)  # 0 padding, assuming 2-digits number
        wouldbe_datafile = generate_bids_filename(subjectName, session, experiment_name, filename_suffix='_beh',
                                                  filename_extension='.xpd', run=i_string)
        wouldbe_eventfile = generate_bids_filename(subjectName, session, experiment_name, filename_suffix='_events',
                                                   filename_extension='.xpe', run=i_string)

    expyriment.control.start(exp, auto_create_subject_id=True, skip_ready_screen=True)
    exp.data.rename(wouldbe_datafile)
    exp.events.rename(wouldbe_eventfile)
    expyriment.control.end()

menu_soundsAllocation_index = {classNames[language][key]: soundNames[language][soundsAllocation_index[key]] for key in soundsAllocation_index.keys()}
# 'None' if no languages were chosen previously, said language otherwise, e.g. 'french'

python = 'py'

# Create the menu
menu = CursesMenu(
    title="Declarative Task - Day One", subtitle='Subject: ' + sys.argv[1] + ' ; language: ' +
                                                 str(language) +
                                                 ' ; Son-Cat: ' + str(menu_soundsAllocation_index).
                                                     replace('{', '').replace('}', ''))

dayOneChooseLanguage = CommandItem(text='choose language',
                            command=python + " src" + os.path.sep + "ld_choose_language.py",
                            arguments='choose-language, ' + sys.argv[1] + ', ' + 'None',
                            menu=menu,
                            should_exit=False)

dayOneExample = CommandItem(text='Example',
                            command=python + " src" + os.path.sep + "ld_example.py",
                            arguments='Example, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOneStimuliPresentation = CommandItem(text='stimuli presentation',
                            command=python + " src" + os.path.sep + "ld_stimuli_presentation.py",
                            arguments='stimuli-presentation, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

soundVolumeAdjustment = CommandItem(text='sound Volume Adjustment',
                            command=python + " src" + os.path.sep + "ld_GUI_adjust_sound_volumes.py",
                            arguments='soundVolumeAdjustment, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

# dayOneAssociationLearning = CommandItem(text='Sound Category Association Learning',
#                             command=python + " src" + os.path.sep + "ld_association_learning.py",
#                             arguments='Association-Learning, ' + sys.argv[1],
#                             menu=menu,
#                             should_exit=False)

dayOneEncoding = CommandItem(text='Encoding',
                            command=python + " src" + os.path.sep + "ld_encoding.py",
                            arguments='Encoding, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOneTestEncoding = CommandItem(text='Test Encoding',
                            command=python + " src" + os.path.sep + "ld_encoding.py",
                            arguments='Test-Encoding, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOneReTestEncoding = CommandItem(text='ReTest Encoding',
                            command=python + " src" + os.path.sep + "ld_encoding.py",
                            arguments='ReTest-Encoding, ' + sys.argv[1],
                            menu=menu,
                            should_exit=False)

dayOneRecognition = CommandItem(text="Recognition",
                                  command=python + " src" + os.path.sep + "ld_recognition.py ",
                                  arguments="Day One - Recognition, " + sys.argv[1],
                                  menu=menu,
                                  should_exit=False)

# dayOneTestAssociationLearning = CommandItem(text='Test Sound Category Association Learning',
#                             command=python + " src" + os.path.sep + "ld_association_learning.py",
#                             arguments='Test-Association-Learning, ' + sys.argv[1],
#                             menu=menu,
#                             should_exit=False)

# dayOneConfig = CommandItem(text='Show config file',
#                            command=python + " src" + os.path.sep + "ld_showConfigFile.py",
#                            menu=menu,
#                            should_exit=False)

menu.append_item(dayOneChooseLanguage)
menu.append_item(dayOneExample)
menu.append_item(soundVolumeAdjustment)
menu.append_item(dayOneStimuliPresentation)
# menu.append_item(dayOneAssociationLearning)
menu.append_item(dayOneEncoding)
menu.append_item(dayOneTestEncoding)
menu.append_item(dayOneReTestEncoding)
menu.append_item(dayOneRecognition)
# menu.append_item(dayOneTestAssociationLearning)
# menu.append_item(dayOneConfig)

menu.show()
