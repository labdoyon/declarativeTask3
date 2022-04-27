from cursesmenu import *
from cursesmenu.items import *
import sys
import os

import expyriment
from declarativeTask3.config import python_interpreter, experiment_session, classPictures, classNames, sounds,\
    soundNames, rawFolder
from declarativeTask3.ld_utils import getPrevious, generate_bids_filename, newSoundAllocation
sep = os.path.sep

subjectName = sys.argv[1]

subject_dir = os.getcwd() + os.path.sep + 'sourcedata' + sep + 'sub-' + subjectName + sep
if not os.path.isdir(subject_dir):
    os.mkdir(subject_dir)

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

# Create the menu
menu = CursesMenu(
    title="Declarative Task - Day One", subtitle='Subject: ' + sys.argv[1] + ' ; language: ' +
                                                 str(language) +
                                                 ' ; Son-Cat: ' + str(menu_soundsAllocation_index).
                                                     replace('{', '').replace('}', ''))

dayOneChooseLanguage = CommandItem(
    text='choose language',
    command=python_interpreter + " " + '"'+os.path.join(rawFolder, "src", "declarativeTask3",
                                                        "ld_choose_language.py")+'"',
    arguments='choose-language, ' + sys.argv[1] + ', ' + 'None',
    menu=menu,
    should_exit=False)

dayOneExample = CommandItem(
    text='Example',
    command=python_interpreter + " " + '"'+os.path.join(rawFolder, "src", "declarativeTask3",
                                                        "ld_example.py")+'"',
    arguments='Example, ' + sys.argv[1],
    menu=menu,
    should_exit=False)

dayOneStimuliPresentation = CommandItem(
    text='stimuli presentation',
    command=python_interpreter + " " + '"'+os.path.join(rawFolder, "src", "declarativeTask3",
                                                        "ld_stimuli_presentation.py")+'"',
    arguments='stimuli-presentation, ' + sys.argv[1],
    menu=menu,
    should_exit=False)

soundVolumeAdjustment = CommandItem(
    text='sound Volume Adjustment',
    command=python_interpreter + " " + '"'+os.path.join(rawFolder, "src", "declarativeTask3",
                                                        "ld_GUI_adjust_sound_volumes.py")+'"',
    arguments='soundVolumeAdjustment, ' + sys.argv[1],
    menu=menu,
    should_exit=False)

dayOneEncoding = CommandItem(
    text='Encoding',
    command=python_interpreter + " " + '"'+os.path.join(rawFolder, "src", "declarativeTask3",
                                                        "ld_encoding.py")+'"',
    arguments='Encoding, ' + sys.argv[1],
    menu=menu,
    should_exit=False)

dayOneTestEncoding = CommandItem(
    text='Test Encoding',
    command=python_interpreter + " " + '"'+os.path.join(rawFolder, "src", "declarativeTask3",
                                                        "ld_encoding.py")+'"',
    arguments='Test-Encoding, ' + sys.argv[1],
    menu=menu,
    should_exit=False)

dayOneReTestEncoding = CommandItem(
    text='ReTest Encoding',
    command=python_interpreter + " " + '"'+os.path.join(rawFolder, "src", "declarativeTask3",
                                                        "ld_encoding.py")+'"',
    arguments='ReTest-Encoding, ' + sys.argv[1],
    menu=menu,
    should_exit=False)

dayOneRecognition = CommandItem(
    text="Recognition",
    command=python_interpreter + " " + '"'+os.path.join(rawFolder, "src", "declarativeTask3",
                                                        "ld_recognition.py")+'"',
    arguments="Day One - Recognition, " + sys.argv[1],
    menu=menu,
    should_exit=False)

menu.append_item(dayOneChooseLanguage)
menu.append_item(dayOneExample)
menu.append_item(soundVolumeAdjustment)
menu.append_item(dayOneStimuliPresentation)
menu.append_item(dayOneEncoding)
menu.append_item(dayOneTestEncoding)
menu.append_item(dayOneReTestEncoding)
menu.append_item(dayOneRecognition)

menu.show()
